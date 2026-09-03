import os
from dotenv import load_dotenv

load_dotenv()


#  TARGET SITES

TARGET_SITES = [
    # Trusted
    "https://www.lemonde.fr",
    "https://www.bbc.com",
    "https://www.reuters.com",
    "https://www.france24.com",
    "https://www.dw.com",

    # International
    "https://edition.cnn.com",
    "https://apnews.com",
    "https://www.theguardian.com",
    "https://www.nytimes.com",

    # Controversial
    "https://www.rt.com",
    "https://sputniknews.com",

    # Arabic
    "https://www.aljazeera.com",
    "https://www.bbc.com/arabic",
    "https://www.france24.com/ar/"
]


#  DATABASE CONFIG

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "cyberintel"
)

NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687"
)

NEO4J_USER = os.getenv(
    "NEO4J_USER",
    "neo4j"
)

NEO4J_PASS = os.getenv(
    "NEO4J_PASS",
    "password"
)

ELASTIC_HOST = os.getenv(
    "ELASTIC_HOST",
    "http://localhost:9200"
)

ELASTIC_INDEX = os.getenv(
    "ELASTIC_INDEX",
    "cyberintel_pages"
)

#  SCRAPING SETTINGS

SCRAPING_DELAY = int(
    os.getenv("SCRAPING_DELAY", 1)
)

TIMEOUT = int(
    os.getenv("TIMEOUT", 15)
)

MAX_PAGES_PER_SITE = int(
    os.getenv("MAX_PAGES_PER_SITE", 200)
)

TOTAL_MAX_PAGES = int(
    os.getenv("TOTAL_MAX_PAGES", 3000)
)

RESPECT_ROBOTS = True

# LINK FILTERING


EXCLUDED_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".css",
    ".js",
    ".ico",
    ".pdf",
    ".zip",
    ".mp4"
]

EXCLUDED_DOMAINS = [
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "t.me",
    "youtube.com"
]


#  BOT DETECTION

BOT_REQUEST_THRESHOLD = 50
BOT_VELOCITY_THRESHOLD = 5.0

# GRAPH SETTINGS


USE_EDGE_WEIGHTS = True
MIN_LINKS_FOR_COMMUNITY = 3