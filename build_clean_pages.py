
import argparse
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from pymongo import MongoClient

# ── NLP optionnel ──────────────────────────────
try:
    import nltk
    from nltk.corpus import stopwords
    nltk.download("stopwords", quiet=True)
    STOPWORDS = set(stopwords.words("english")) | set(stopwords.words("french"))
    HAS_NLTK = True
except ImportError:
    STOPWORDS = set()
    HAS_NLTK = False
    print("⚠️ nltk non installé — nettoyage basique uniquement")


# ═══════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════

KNOWN_LABELS = {
    "lemonde.fr": "real",
    "bbc.com": "real",
    "bbc.co.uk": "real",
    "reuters.com": "real",
    "france24.com": "real",
    "cnn.com": "real",
    "dw.com": "real",
    "aljazeera.net": "real",
    "rt.com": "fake",
    "sputnikglobe.com": "fake",
    "sputniknews.com": "fake",
}


# ═══════════════════════════════════════════════
# MONGODB
# ═══════════════════════════════════════════════

def connect_mongodb(uri: str, db_name: str):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        print(f"✅ MongoDB connecté : {uri} / {db_name}")
        return client[db_name]
    except Exception as e:
        raise ConnectionError(f"❌ MongoDB erreur : {e}")


def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url if url.startswith("http") else "https://" + url)
        domain = parsed.netloc.lower()
        return re.sub(r"^www\d?\.", "", domain)
    except Exception:
        return url


def load_raw_pages(db, collection_name="raw_pages") -> pd.DataFrame:
    col = db[collection_name]

    total = col.count_documents({})
    print(f"   {total} documents dans '{collection_name}'")

    projection = {
        "_id": 0,
        "url": 1,
        "domain": 1,
        "text": 1,
        "content": 1,
        "links": 1,
        "headers": 1,
        "scraped_at": 1,
        "label": 1,
    }

    docs = list(col.find({}, projection))

    # ⭐ FIX IMPORTANT
    if len(docs) == 0:
        print(f"⚠️ Collection '{collection_name}' vide — arrêt du pipeline.")
        return pd.DataFrame()

    df = pd.DataFrame(docs)

    if "text" not in df.columns and "content" in df.columns:
        df.rename(columns={"content": "text"}, inplace=True)
    if "text" not in df.columns:
        df["text"] = ""

    if "domain" not in df.columns or df["domain"].isna().all():
        df["domain"] = df["url"].apply(extract_domain)

    return df


# ═══════════════════════════════════════════════
# CLEAN TEXT
# ═══════════════════════════════════════════════

def clean_text(raw: str, min_words: int = 20) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return ""

    text = raw.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s']", " ", text)

    if HAS_NLTK:
        words = [w for w in text.split() if w not in STOPWORDS and len(w) > 1]
        text = " ".join(words)

    text = re.sub(r"\s+", " ", text).strip()

    if len(text.split()) < min_words:
        return ""

    return text


# ═══════════════════════════════════════════════
# FUSION SAFE
# ═══════════════════════════════════════════════

def merge_all(df_pages, df_graph, df_bots):
    if df_pages.empty:
        return df_pages

    df_pages["domain"] = df_pages["domain"].fillna("").str.lower()

    if not df_graph.empty:
        df = df_pages.merge(df_graph, on="domain", how="left")
    else:
        df = df_pages.copy()

    if not df_bots.empty:
        df = df.merge(df_bots, on="domain", how="left")

    return df


def assign_labels(df):
    if df.empty:
        return df

    def get_label(row):
        if "label" in row and pd.notna(row["label"]):
            return row["label"]
        return KNOWN_LABELS.get(row.get("domain", ""), None)

    df["label"] = df.apply(get_label, axis=1)
    return df


def compute_suspicion_score(df):
    if df.empty:
        return df

    df["pagerank"] = df.get("pagerank", 0.0)
    df["bot_score"] = df.get("bot_score", 0.0)

    df["suspicion_score"] = (
        0.5 * df["bot_score"].fillna(0)
        + 0.3 * (1 - df["pagerank"].fillna(0))
        + 0.2
    )

    return df


# ═══════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════

def build_clean_pages_csv(df, output_path):
    if df.empty:
        print("❌ Aucun data à exporter.")
        return df

    df["clean_text"] = df["text"].apply(clean_text)
    df = df[df["clean_text"] != ""]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✅ CSV généré : {output_path}")
    print(f"📊 {len(df)} lignes")

    return df


# ═══════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════

def run(mongo_uri="mongodb://localhost:27017",
        db_name="cyberintel",
        collection="raw_pages",
        output="datasets/clean_pages.csv"):

    print("=" * 50)
    print("CYBERINTEL PIPELINE")
    print("=" * 50)

    db = connect_mongodb(mongo_uri, db_name)

    print("\n📦 Chargement MongoDB")
    df_pages = load_raw_pages(db, collection)

    # ⭐ FIX IMPORTANT
    if df_pages.empty:
        print("❌ Pipeline arrêté : aucune donnée dans MongoDB")
        return

    print("\n🔗 Fusion")
    df = merge_all(df_pages, pd.DataFrame(), pd.DataFrame())

    print("\n🏷 Labels")
    df = assign_labels(df)

    print("\n⚡ Score")
    df = compute_suspicion_score(df)

    print("\n💾 Export")
    build_clean_pages_csv(df, output)

    print("\n✅ Terminé")


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--db", default="cyberintel")
    parser.add_argument("--collection", default="raw_pages")
    parser.add_argument("--output", default="datasets/clean_pages.csv")

    args = parser.parse_args()

    run(
        mongo_uri=args.mongo_uri,
        db_name=args.db,
        collection=args.collection,
        output=args.output
    )