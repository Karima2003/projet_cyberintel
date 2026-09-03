
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx

WEIGHTS = {
    "ml_fake_proba":      0.55,
    "community_iso":      0.15,
    "stance_score":       0.15,
    "contradiction_rate": 0.15,
}

THRESHOLDS = {
    "high":   0.62,  
    "medium": 0.45,
}

WHITELIST_DOMAINS = {
    # Médias français reconnus
    "lemonde.fr", "telerama.fr", "courrierinternational.com",
    "monde-diplomatique.fr", "mondediplo.net", "lavie.fr", "huffingtonpost.fr",
    "rfi.fr", "france24.com", "liberation.fr", "lefigaro.fr",
    "leparisien.fr", "lesechos.fr", "nouvelobs.com", "lexpress.fr",
    # Institutions publiques françaises et internationales
    "cnil.fr", "cfi.fr", "oneplanetsummit.fr",
    # Plateformes mondiales
    "play.google.com", "google.com", "youtube.com",
    "pressreader.com", "anchor.fm",
}

def is_whitelisted(domain: str) -> bool:
    """Retourne True si le domaine ou son domaine parent est dans la whitelist."""
    domain = domain.lower().strip()
    if domain in WHITELIST_DOMAINS:
        return True
    # Vérifie le domaine parent (ex: boutique.lemonde.fr → lemonde.fr)
    parts = domain.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[i:])
        if parent in WHITELIST_DOMAINS:
            return True
    return False


# =============================================================================
# LOAD DATA
# =============================================================================

def load_predictions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"[OK] Predictions ML : {len(df)} pages")
    return df


def load_clean_pages(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"[OK] clean_pages : {len(df)} pages")
    return df


def load_graph_metrics(path: str = "graph_metrics.json") -> pd.DataFrame:
    from urllib.parse import urlparse

    p = Path(path)
    if not p.exists():
        print("[WARN] graph_metrics introuvable")
        return pd.DataFrame(columns=["domain"])

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)


    # On extrait le domaine (netloc sans www.) et on agrège par domaine
    records = [{"domain": k, **v} for k, v in data.items()] if isinstance(data, dict) else data
    df = pd.DataFrame(records)

    # Détection : si la colonne "domain" ressemble à des URLs → extraction netloc
    if "domain" not in df.columns and "url" in df.columns:
        df["domain"] = df["url"]

    sample = df["domain"].dropna().iloc[0] if len(df) > 0 else ""
    if sample.startswith("http"):
        df["domain"] = df["domain"].apply(
            lambda u: urlparse(str(u)).netloc.lstrip("www.")
        )

    # Agréger les métriques par domaine (plusieurs URLs → même domaine)
    agg_cols = {c: "mean" for c in ["pagerank", "authority", "hub", "community_iso"] if c in df.columns}
    if agg_cols:
        df = df.groupby("domain").agg(agg_cols).reset_index()
    else:
        df = df[["domain"]].drop_duplicates()

    print(f"[OK] graph_metrics : {len(df)} domaines (après extraction depuis URLs)")
    return df



def load_bot_scores(path: str = "bot_scores.json") -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        print("[WARN] bot_scores introuvable")
        return pd.DataFrame(columns=["domain", "bot_score", "is_bot"])

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    
    if isinstance(data, list):
        df = pd.DataFrame(data)

        
        if "ip" in df.columns:
            df["domain"] = df["ip"]

    
    elif isinstance(data, dict):
        records = []
        for k, v in data.items():
            row = {"domain": k}
            if isinstance(v, dict):
                row.update(v)
            records.append(row)
        df = pd.DataFrame(records)

    else:
        raise ValueError("Format bot_scores.json non reconnu")

    # sécurité colonnes
    if "domain" not in df.columns:
        df["domain"] = "unknown"

    if "bot_score" not in df.columns:
        df["bot_score"] = 0.0

    if "is_bot" not in df.columns:
        df["is_bot"] = False

    print(f"[OK] bot_scores : {len(df)} domaines")
    return df


# =============================================================================
# ML SCORE
# =============================================================================

def compute_ml_score(df):
    """
    Problème : le modèle classe des pages (URLs), pas des domaines.
    Un même domaine peut avoir fake(0.85) et real(0.87) → mean = bruit.
    Solution : weighted mean par confidence — les prédictions sûres comptent plus.
    """
    df = df.copy()

    df["ml_fake_proba"] = df.apply(
        lambda r: r["prediction_confidence"]
        if r["predicted_label"] == "fake"
        else 1 - r["prediction_confidence"],
        axis=1
    )

    # Poids = confidence (une prédiction à 0.90 pèse 2x plus qu'une à 0.55)
    df["weight"] = df["prediction_confidence"]

    def weighted_mean(g):
        return (g["ml_fake_proba"] * g["weight"]).sum() / g["weight"].sum()

    result = df.groupby("domain").apply(weighted_mean).reset_index()
    result.columns = ["domain", "ml_fake_proba"]

    # Diagnostic : domaines avec prédictions contradictoires
    def contradiction(g):
        if len(g) < 2:
            return 0.0
        fakes = (g["predicted_label"] == "fake").sum()
        reals = (g["predicted_label"] == "real").sum()
        total = len(g)
        minority = min(fakes, reals)
        return minority / total  # 0=cohérent, 0.5=totalement contradictoire

    contra = df.groupby("domain").apply(contradiction).reset_index()
    contra.columns = ["domain", "contradiction_rate"]

    result = result.merge(contra, on="domain", how="left")

    n_contradicted = (result["contradiction_rate"] > 0.2).sum()
    print(f"[INFO] Domaines contradictoires (>20% pages en désaccord) : {n_contradicted}")

    return result[["domain", "ml_fake_proba", "contradiction_rate"]]


# =============================================================================
# BOT NORMALIZATION
# =============================================================================

def normalize_bot_score(df):
    df = df.copy()

    if df["bot_score"].max() > 1:
        df["bot_score"] = df["bot_score"] / 100.0

    df["bot_score"] = df["bot_score"].clip(0, 1)
    return df[["domain", "bot_score", "is_bot"]]


# =============================================================================
# PAGERANK
# =============================================================================

def compute_pagerank_inv(df):
    """
    Pagerank élevé = site connu et référencé = moins suspect.
    Problème avec normalisation linéaire : valeurs très resserrées → aucune discrimination.
    Solution : log-scaling pour étaler les différences, puis inversion.
    """
    import numpy as np

    df = df.copy()

    if "pagerank" not in df.columns:
        df["pagerank"] = 0.0

    # Remplacer les 0 par epsilon pour éviter log(0)
    pr = df["pagerank"].clip(lower=1e-10)

    # Log-scaling : étale les petites différences entre valeurs proches
    log_pr = np.log10(pr)

    # Normalisation min-max sur les valeurs log
    log_min = log_pr.min()
    log_max = log_pr.max()

    if log_max > log_min:
        pr_normalized = (log_pr - log_min) / (log_max - log_min)
    else:
        pr_normalized = 0.0

    # Inversion : pagerank élevé (site connu) → suspicion basse
    df["pagerank_inv"] = 1 - pr_normalized

    print(f"[INFO] pagerank_inv — min={df['pagerank_inv'].min():.3f} "
          f"max={df['pagerank_inv'].max():.3f} "
          f"mean={df['pagerank_inv'].mean():.3f}")

    return df[["domain", "pagerank_inv"]]




def compute_community_iso(df):
    """
    Calcule un score d'isolation communautaire à partir de graph_metrics.
    Si la colonne 'community_iso' n'existe pas, renvoie 0 par défaut.
    """
    df = df.copy()

    if "community_iso" not in df.columns:
        df["community_iso"] = 0.0

    df["community_iso"] = df["community_iso"].clip(0, 1)
    return df[["domain", "community_iso"]]


# =============================================================================
# STANCE
# =============================================================================

def compute_stance(df):
    """
    clean_pages.csv contient une colonne 'label' (fake/real) sur 1736 lignes.
    On l'utilise directement comme stance_score :
      - fake  → 1.0
      - real  → 0.0
      - NaN   → 0.5 (neutre)
    Agrégé par domaine avec weighted mean selon la confiance implicite.
    """
    df = df.copy()

    if "label" in df.columns:
        def label_to_score(lbl):
            if pd.isna(lbl):
                return None
            lbl = str(lbl).strip().lower()
            if lbl == "fake":
                return 1.0
            elif lbl == "real":
                return 0.0
            return None

        df["stance_score"] = df["label"].apply(label_to_score)

        # Agréger : moyenne des labels connus par domaine
        result = df.groupby("domain").apply(
            lambda g: g["stance_score"].dropna().mean()
            if g["stance_score"].notna().any()
            else 0.5
        ).reset_index()
        result.columns = ["domain", "stance_score"]

        # Domaines sans aucun label → neutre 0.5
        result["stance_score"] = result["stance_score"].fillna(0.5)

        n_fake = (result["stance_score"] > 0.5).sum()
        n_real = (result["stance_score"] < 0.5).sum()
        n_neutral = (result["stance_score"] == 0.5).sum()
        print(f"[INFO] stance — fake:{n_fake}  real:{n_real}  neutre:{n_neutral}")

    else:
        print("[WARN] Colonne label absente — stance_score neutre")
        domains = df["domain"].unique()
        result = pd.DataFrame({"domain": domains, "stance_score": 0.5})

    return result


# =============================================================================
# FINAL SCORE
# =============================================================================

def compute_final(df_ml, df_community, df_stance):
    # bot_score retiré     : IPs simulées
    # pagerank_inv retiré  : graphe local, trop peu de variance
    # contradiction_rate   : inclus dans df_ml
    df = df_ml.merge(df_community, on="domain", how="left")
    df = df.merge(df_stance, on="domain", how="left")

    df = df.fillna(0)

    df["suspicion_score"] = (
        WEIGHTS["ml_fake_proba"]      * df["ml_fake_proba"] +
        WEIGHTS["community_iso"]      * df["community_iso"] +
        WEIGHTS["stance_score"]       * df["stance_score"] +
        WEIGHTS["contradiction_rate"] * df["contradiction_rate"]
    )

    return df


# =============================================================================
# PIPELINE
# =============================================================================

def run():
    # =========================================================
    # LOAD DATA
    # =========================================================
    df_pages = load_predictions("datasets/predictions_finales.csv")
    df_clean = load_clean_pages("datasets/clean_pages.csv")

    df_graph = load_graph_metrics("graph_metrics.json")
    # =========================================================
    # COMPUTE SCORES
    # =========================================================
    df_ml = compute_ml_score(df_pages)
    df_community = compute_community_iso(df_graph)  # pagerank_inv supprimé
    df_stance = compute_stance(df_clean)

    # =========================================================
    # FINAL SCORE
    # =========================================================
    df_final = compute_final(df_ml, df_community, df_stance)

    # =========================================================
    # CLASSIFICATION
    # =========================================================
    def classify(score):
        if score >= THRESHOLDS["high"]:
            return "HIGH"
        elif score >= THRESHOLDS["medium"]:
            return "MEDIUM"
        return "LOW"

    df_final["risk_level"] = df_final["suspicion_score"].apply(classify)

    # =========================================================
    # WHITELIST — forcer les médias légitimes à LOW
    # =========================================================
    whitelisted = df_final["domain"].apply(is_whitelisted)
    n_whitelisted = whitelisted.sum()
    df_final.loc[whitelisted, "risk_level"] = "LOW"
    df_final.loc[whitelisted, "suspicion_score"] = df_final.loc[whitelisted, "suspicion_score"].clip(upper=0.44)
    print(f"[INFO] Whitelist appliquée : {n_whitelisted} domaines forcés à LOW")

    # =========================================================
    # CONTRIBUTIONS (EXPLICATION DU SCORE)
    # =========================================================
    df_final["ml_contrib"]             = df_final["ml_fake_proba"]      * WEIGHTS["ml_fake_proba"]
    df_final["community_contrib"]      = df_final["community_iso"]      * WEIGHTS["community_iso"]
    df_final["stance_contrib"]         = df_final["stance_score"]       * WEIGHTS["stance_score"]
    df_final["contradiction_contrib"]  = df_final["contradiction_rate"] * WEIGHTS["contradiction_rate"]

    # =========================================================
    # EXPORT CSV FINAL
    # =========================================================
    output_csv = "datasets/suspicion_scores.csv"
    df_final.to_csv(output_csv, index=False)
    print(f"[OK] Scores exportés : {output_csv}")

    # =========================================================
    # EXPORT GRAPH LINKS
    # =========================================================
    G = nx.Graph()

    domains = df_final["domain"].dropna().unique()

    for i in range(len(domains) - 1):
        G.add_edge(domains[i], domains[i + 1])

    links = [
        {"source": s, "target": t}
        for s, t in G.edges()
    ]

    with open("datasets/graph_links.json", "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2, ensure_ascii=False)

    print("[OK] graph_links.json exporté")

    # =========================================================
    # TOP DOMAINS
    # =========================================================
    print("\n========== TOP SUSPICIOUS DOMAINS ==========")
    print(
        df_final.sort_values("suspicion_score", ascending=False)[
            ["domain", "suspicion_score", "risk_level"]
        ].head(10)
    )

    # =========================================================
    # STATISTICS
    # =========================================================
    print("\n========== RISK DISTRIBUTION ==========")
    print(df_final["risk_level"].value_counts())

    # =========================================================
    # VISUALISATION
    # =========================================================
    plt.figure(figsize=(10, 5))
    plt.hist(df_final["suspicion_score"], bins=30)
    plt.title("Distribution des scores de suspicion")
    plt.xlabel("Score")
    plt.ylabel("Nombre de domaines")
    plt.grid(True)
    plt.savefig("datasets/suspicion_distribution.png")
    plt.close()  
    print("[OK] Graphique sauvegardé")


if __name__ == "__main__":
    run()