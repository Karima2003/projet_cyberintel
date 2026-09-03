import pandas as pd
import random
import time
from database.mongo_connector import save_bot_score



#  SIMULATION LOGS


def simulate_logs(pages: list, n_sessions: int = 200) -> list:
    """
    Simule des logs réalistes :
    - 50% bots / 50% humains
    - Bots : rapides + semi-réguliers
    - Humans : lents + irréguliers
    """

    logs = []

    if not pages:
        return logs

    for _ in range(n_sessions):

        ip = f"192.168.1.{random.randint(1, 255)}"

        # 50% bots
        is_bot = random.random() < 0.5

        nb_requests = random.randint(5, 30)

        start_time = time.time() - random.randint(0, 1000)

        for j in range(nb_requests):

            if is_bot:
                #  bot: rapide + petit bruit
                delta = random.uniform(0.05, 0.5)
            else:
                # humain: lent + irrégulier
                delta = random.uniform(1.0, 6.0)

            timestamp = start_time + j * delta

            logs.append({
                "ip": ip,
                "url": random.choice(pages)["url"],
                "timestamp": timestamp,
                "is_bot_true": is_bot   # utile pour ML plus tard
            })

    return logs


#  DETECTION BOTS


def detect_bots(logs: list) -> pd.DataFrame:
    """
    Analyse les logs et attribue un bot_score + classification
    """

    if not logs:
        print("[WARNING] No logs to analyze")
        return pd.DataFrame()

    df = pd.DataFrame(logs)

    # convertir timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    # trier
    df = df.sort_values(["ip", "timestamp"])

    results = []

    for ip, group in df.groupby("ip"):

        # durée session
        duration = max(
            (group["timestamp"].max() - group["timestamp"].min()).total_seconds(),
            1
        )

        # vitesse
        velocity = len(group) / duration

        # régularité
        intervals = group["timestamp"].diff().dt.total_seconds().dropna()
        regularity = intervals.std() if len(intervals) > 1 else 999

  
        #  SCORE EQUILIBRE
    

        score = (
            0.5 * (velocity / 5) +
            0.5 * (1 / (regularity + 1))
        )
        score = round(min(score, 1.0), 3)

        #  DECISION (NON AGRESSIVE)
  

        is_bot = score > 0.7

        result = {
            "ip": ip,
            "nb_requests": len(group),
            "velocity_rps": round(velocity, 3),
            "regularity_std": round(regularity, 3),
            "bot_score": score,
            "is_bot": is_bot
        }

        results.append(result)

        # sauvegarde MongoDB
        try:
            save_bot_score(result)
        except Exception as e:
            print(f"[ERROR] Mongo save failed: {e}")

    df_result = pd.DataFrame(results)

    print("\n[BOTS] Resultats :")
    print(df_result.sort_values("bot_score", ascending=False).to_string(index=False))

    return df_result