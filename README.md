# 🛡️ CyberIntel — Web Disinformation Detection

> **An intelligent Cyber Threat Intelligence platform for detecting suspicious web content and domains through Web Mining, Machine Learning, NLP, behavioral analysis, and graph analytics.**

CyberIntel is an end-to-end Cyber Threat Intelligence platform designed to analyze web information and identify signals associated with potentially suspicious or misleading content.

The platform combines **Web Crawling, NLP, Machine Learning, Deep Learning, behavioral analysis, and graph-based intelligence** to transform raw web data into actionable threat indicators and visual investigations.

---

## 🎯 Project Overview

The modern web contains an enormous amount of information published across news websites, blogs, forums, and other online platforms. This environment can also facilitate the rapid propagation of misinformation, coordinated campaigns, automated activity, and manipulated content.

CyberIntel addresses this problem by analyzing **three complementary dimensions**:

* 🕸️ **Structural analysis** — relationships and connectivity between websites
* 🤖 **Behavioral analysis** — detection of potentially automated activity
* 🧠 **Semantic analysis** — analysis of textual content using NLP and AI

The objective is to combine these signals into a unified intelligence pipeline capable of identifying suspicious domains and prioritizing further investigation.

---

## ✨ Key Features

### 🌐 Web Intelligence & Crawling

* Automated collection of web pages
* Static and dynamic page scraping
* Extraction of textual content and metadata
* Internal and external link discovery
* Multi-source and multilingual data collection
* Respect for website crawling policies through `robots.txt`

More than **2,200 web pages** were collected from multiple categories of sources.

### 🗄️ Multi-Database Architecture

CyberIntel uses specialized databases for different types of information:

| Technology        | Role                                           |
| ----------------- | ---------------------------------------------- |
| **MongoDB**       | Storage of collected web documents             |
| **Elasticsearch** | Full-text indexing and fast search             |
| **Neo4j**         | Graph representation and relationship analysis |

This hybrid architecture separates document storage, search, and graph intelligence according to their respective strengths.

### 🕸️ Graph Intelligence

Each web page is represented as a node and hyperlinks are represented as edges.

The graph analysis includes:

* **PageRank** — identification of influential domains
* **HITS** — identification of hubs and authorities
* **Community Detection** — discovery of highly connected groups
* Link-structure analysis
* Suspicious network identification

The resulting graph contained **2,102 nodes and 4,806 links**, with **22 communities** detected.

### 🤖 Behavioral & Bot Analysis

CyberIntel analyzes browsing behavior using:

* Request frequency
* Request speed
* Regularity
* Activity patterns

A **Bot Score between 0 and 1** is calculated to quantify suspicious automated behavior.

Higher values indicate more suspicious activity. The project reports Bot Scores reaching **0.984** for some detected IPs.

### 🧹 Data Processing & Preparation

The preprocessing pipeline includes:

* Text normalization
* Lowercasing
* URL removal
* Punctuation removal
* Special-character cleaning
* Whitespace normalization
* Dataset structuring with Pandas
* Automatic labeling
* Feature integration

The final analytical dataset combines web, graph, behavioral, label, and metadata information.

---

# 🧠 Artificial Intelligence Pipeline

CyberIntel combines classical Machine Learning with semantic Deep Learning techniques.

## Machine Learning Models

The following classification algorithms were evaluated:

* Logistic Regression
* Random Forest
* HistGradientBoostingClassifier

Because the original dataset contained significantly fewer `fake` examples than `real` examples, class balancing was taken into account during model training.

## 🤗 BERT / Sentence Transformers

Sentence Transformers were integrated to generate **384-dimensional semantic embeddings** from web content.

These embeddings allow the system to capture contextual and semantic information beyond traditional text-based features.

## 🔄 Data Augmentation

To address the limited number of fake examples, the training data was augmented using:

* Synonym replacement
* Back Translation

Augmentation was applied only to the training data to avoid test-set contamination.

## 📊 Model Evaluation

The models were evaluated using:

* Accuracy
* F1-score
* F1-macro
* ROC-AUC
* Confusion Matrix

The best-performing model in the final evaluation was **HistGradientBoostingClassifier**:

| Metric   |     Result |
| -------- | ---------: |
| Accuracy | **95.98%** |
| F1-macro | **0.8492** |
| ROC-AUC  | **0.9372** |

The reported final test set contained **24 fake** and **324 real** examples.

---

# 🔍 Advanced Content Analysis

## Semantic Similarity

Cosine similarity is used to compare suspicious content with predefined semantic reference profiles.

Two reference profiles were constructed:

* Propagandistic profile
* Neutral profile

The semantic similarity signal is combined with other indicators rather than being used alone to classify an article.

## 🧭 Stance Analysis

The system performs stance analysis to identify broad ideological orientations:

* Pro-Russian
* Pro-Western
* Neutral

The analysis is based on a geopolitical keyword lexicon and its results are incorporated into the unified scoring system.

## ✍️ Stylometric Analysis

Stylometric features are extracted to compare writing characteristics between fake and real content.

The analyzed features include:

* Average word length
* Vocabulary richness
* Text length

This provides an additional linguistic signal for identifying suspicious writing patterns.

---

# 🚨 Unified Threat Scoring

One of the core components of CyberIntel is the **Unified Suspicion Scoring Engine**.

Instead of relying on a single model, the system combines multiple analytical signals:

```text
                    ┌─────────────────────┐
                    │   Web Intelligence  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ML Prediction         Graph Analysis        Behavioral Analysis
        │                      │                      │
        ▼                      ▼                      ▼
   ML Score             Community Score          Bot Score
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                     Stance / Content Analysis
                               │
                               ▼
                  ┌─────────────────────────┐
                  │ Unified Suspicion Score │
                  └────────────┬────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Risk Classification│
                    └─────────────────────┘
                       LOW / MEDIUM / HIGH
```

The unified score incorporates:

* Machine Learning predictions
* Community isolation
* Stance analysis
* Contradiction rate
* Graph metrics
* Behavioral signals

This multi-dimensional approach provides a broader assessment than relying exclusively on textual classification.

### Risk Levels

| Level         | Condition           |
| ------------- | ------------------- |
| 🟢 **LOW**    | Score < 0.45        |
| 🟠 **MEDIUM** | 0.45 ≤ Score < 0.62 |
| 🔴 **HIGH**   | Score ≥ 0.62        |

These thresholds are used by the dashboard to prioritize potentially suspicious domains.

---

# 📊 Cyber Threat Intelligence Dashboard

CyberIntel includes an interactive **Streamlit dashboard** designed for investigation and threat visualization.

The dashboard follows a dark **SOC-inspired cybersecurity interface** and is organized into five main modules:

### 1. Overview

Provides a global view of the system:

* Total analyzed domains
* Number of HIGH-risk domains
* Average suspicion score
* Number of predictions
* Suspicion score distribution
* Most suspicious domains

### 2. Domains

Provides detailed domain-level investigation:

* Suspicion score
* Risk level
* Fake probability
* Contradiction rate
* Stance score
* Community isolation
* Interactive filtering and sorting
* CSV / JSON export

### 3. ML Engine

Provides Machine Learning analysis:

* Model comparison
* Accuracy
* F1-score
* ROC-AUC
* Prediction confidence
* Confusion matrix
* Class distribution

### 4. Network

Provides graph-based investigation:

* Interactive domain network
* Domain relationships
* Suspicious clusters
* Community detection
* Central hubs
* Community statistics

The graph is built with **NetworkX**, with nodes representing domains and edges representing relationships.

### 5. Pipeline

Provides a global view of the CyberIntel pipeline:

* Pages analyzed
* Domains scored
* Models compared
* Stylometric analysis
* Pipeline-generated metrics

---

# 🏗️ System Architecture

```text
                         WEB SOURCES
                              │
                              ▼
                  ┌──────────────────────┐
                  │     Web Crawlers     │
                  │ Requests / Selenium  │
                  │ BeautifulSoup / URLs │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Data Storage      │
                  │ MongoDB              │
                  │ Elasticsearch        │
                  │ Neo4j                │
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Text Analysis   Graph Analysis  Behavioral
              │              │              │
              ▼              ▼              ▼
          NLP / BERT     PageRank/HITS    Bot Score
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    Unified Scoring Engine
                             │
                             ▼
                    Risk Classification
                  LOW / MEDIUM / HIGH
                             │
                             ▼
                    Streamlit Dashboard
```

---

# 📁 Project Structure

```text
projet_cyberintel/
│
├── dashboard.py
├── main.py
├── config.py
├── Unified scoring.py
├── build_clean_pages.py
├── export_data.py
│
├── scrapers/
│   ├── scraper_static.py
│   └── scraper_dynamic.py
│
├── database/
│   ├── mongo_connector.py
│   ├── elastic_connector.py
│   └── neo4j_connector.py
│
├── graph_mining/
│   ├── build_graph.py
│   ├── community_detection.py
│   └── pagerank_hits.py
│
├── usage_mining/
│   └── bot_detector.py
│
├── datasets/
│   ├── graph_links.json
│   ├── comparaison_finale.png
│   ├── stance_analysis.png
│   ├── stylometrie.png
│   └── suspicion_distribution.png
│
├── pipeline_ML.ipynb
├── preprocessing des donnees.ipynb
│
├── bot_scores.json
├── graph_metrics.json
│
├── rapport de projet.pdf
│
└── .gitignore
```

---

# 🛠️ Technologies

### Programming

* Python

### Web Mining

* Requests
* Selenium
* BeautifulSoup
* urllib

### Data Processing

* Pandas
* NumPy
* Regex
* NLTK

### Machine Learning

* Scikit-learn
* Logistic Regression
* Random Forest
* HistGradientBoosting

### Deep Learning / NLP

* BERT
* Sentence Transformers
* Semantic Embeddings
* Cosine Similarity

### Graph Intelligence

* Neo4j
* NetworkX
* PageRank
* HITS
* Community Detection

### Databases & Search

* MongoDB
* Elasticsearch

### Visualization

* Streamlit
* Interactive charts and network visualization

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Python 3.x
* MongoDB
* Elasticsearch
* Neo4j

installed and configured.

## Installation

Clone the repository:

```bash
git clone https://github.com/Karima2003/projet_cyberintel.git
cd projet_cyberintel
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```cmd
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** A `requirements.txt` file should be added to the repository if one is not already present.

## Configuration

Create a `.env` file locally containing your database configuration and other environment-specific variables.

**Do not commit `.env` to GitHub.**

The repository already uses `.gitignore` to prevent `.env` from being uploaded.

---

# ▶️ Running the Dashboard

After configuring the required services and environment variables:

```bash
streamlit run dashboard.py
```

The dashboard provides access to:

```text
Overview
   ↓
Domains
   ↓
ML Engine
   ↓
Network
   ↓
Pipeline
```

---

# 📈 Results

The project demonstrates a complete pipeline from web collection to threat visualization.

### Data Collection

* **2,200+ web pages collected**
* Multi-source web dataset
* Multiple categories of information sources

### Graph Analysis

* **2,102 nodes**
* **4,806 links**
* **22 communities detected**

### Behavioral Analysis

* Bot Score ranging from 0 to 1
* Maximum reported score: **0.984**

### Machine Learning

**HistGradientBoostingClassifier**

* **95.98% Accuracy**
* **0.8492 F1-macro**
* **0.9372 ROC-AUC**

## These results correspond to the final evaluation described in the project report.

# 🔬 Methodology

CyberIntel follows a multi-stage intelligence pipeline:

```text
1. Web Crawling
       ↓
2. Data Storage
       ↓
3. Data Cleaning
       ↓
4. Graph Construction
       ↓
5. Community Detection
       ↓
6. Behavioral Analysis
       ↓
7. Dataset Construction
       ↓
8. NLP & Feature Engineering
       ↓
9. ML / BERT Analysis
       ↓
10. Stance Analysis
       ↓
11. Stylometric Analysis
       ↓
12. Unified Suspicion Scoring
       ↓
13. Risk Classification
       ↓
14. Cyber Threat Intelligence Dashboard
```

---

# ⚠️ Disclaimer

CyberIntel is a **research and academic project** designed to identify suspicious patterns and support investigation.

A domain or article receiving a high suspicion score should **not automatically be interpreted as definitive proof of disinformation or malicious activity**.

The system combines multiple signals to assist analysis and prioritization.

---



# ⭐ Project Highlights

```text
🕸️ Web Mining
🤖 Machine Learning
🧠 NLP & BERT
🕵️ Behavioral Analysis
🕸️ Graph Intelligence
🗄️ Multi-Database Architecture
🚨 Unified Threat Scoring
📊 Interactive CTI Dashboard
```

**CyberIntel transforms raw web data into structured intelligence for the investigation of suspicious information ecosystems.**
