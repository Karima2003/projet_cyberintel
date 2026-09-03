# CyberIntel — Web Disinformation Detection

CyberIntel is a web disinformation detection project developed as part of an academic project in Big Data and Artificial Intelligence.

The objective is to collect and analyze web content in order to identify suspicious pages and domains. The project combines **web scraping, NLP, machine learning, graph analysis, and behavioral analysis** to build a unified view of potentially misleading or suspicious content.

The system processes collected web pages, extracts relevant features, analyzes relationships between domains and pages, and produces a suspicion score that can be explored through a Streamlit dashboard.

---

## Project Overview

The system follows several stages:

1. Collect web pages from different sources.
2. Store the collected information in databases.
3. Clean and preprocess the textual content.
4. Build a graph representing relationships between pages and domains.
5. Analyze the graph using network analysis algorithms.
6. Detect suspicious or automated behavior.
7. Extract NLP and stylometric features.
8. Apply machine learning models for classification.
9. Combine the different signals into a final suspicion score.
10. Visualize the results through an interactive dashboard.

The project was designed to combine different types of information rather than relying on a single classification model.

---

## Main Features

### Web Data Collection

The scraping pipeline collects information from web pages, including:

* Page URLs
* Domain information
* Titles
* Text content
* Links between pages
* Metadata used during analysis

The scraping part uses tools such as **Requests, Selenium and BeautifulSoup**.

---

### Data Storage

Different databases were used depending on the type of information being handled:

* **MongoDB** — storage of collected web documents
* **Elasticsearch** — indexing and searching textual data
* **Neo4j** — representation of relationships between pages and domains

This allowed the project to work with both document-oriented and graph-based data.

---

## Graph Analysis

A graph was constructed to represent relationships between the collected web pages and domains.

The graph contains:

* Nodes representing pages/domains
* Edges representing relationships between them

Several graph analysis techniques were used, including:

* PageRank
* HITS
* Community detection
* Degree-based analysis
* NetworkX graph processing

The final dataset used in the project contains more than **2,100 nodes** and **4,800 relationships**, with **22 detected communities**.

These relationships help identify groups of domains and pages that behave similarly or are strongly connected.

---

## NLP and Text Analysis

The textual content of the collected pages was cleaned and transformed before being used by the machine learning pipeline.

The preprocessing includes operations such as:

* Text cleaning
* Tokenization
* Stop-word handling
* Normalization
* Feature extraction

Different NLP approaches were explored, including:

* TF-IDF
* BERT-based embeddings
* Sentence Transformers
* Semantic similarity
* Stance analysis
* Stylometric analysis

The goal was to extract both semantic and linguistic information from the articles.

---

## Machine Learning

Several machine learning models were evaluated for the classification task.

The project experimented with different algorithms and compared their performance before selecting the final model.

The final model used in the project was **HistGradientBoostingClassifier**.

### Final Results

| Metric   |  Score |
| -------- | -----: |
| Accuracy | 95.98% |
| F1-Macro | 0.8492 |
| ROC-AUC  | 0.9372 |

The model was evaluated using the processed and augmented dataset developed during the project.

---

## Behavioral / Bot Analysis

The project also includes behavioral analysis to identify domains or sources showing characteristics associated with automated or suspicious activity.

A **Bot Score** was calculated from different behavioral indicators.

The resulting score is used as one of the signals in the final analysis instead of being treated as the only criterion for deciding whether content is suspicious.

---

## Suspicion Scoring

The different analysis components are combined into a unified suspicion score.

The scoring system takes into account several signals, including:

* Machine learning predictions
* Graph-based information
* Behavioral analysis
* Semantic similarity
* Stance analysis
* Stylometric features

The resulting score is used to classify the analyzed content into different suspicion levels.

### Suspicion Levels

* **LOW** — limited evidence of suspicious behavior
* **MEDIUM** — several suspicious indicators
* **HIGH** — strong combination of suspicious indicators

The score is intended as an analytical indicator and should not be considered a definitive fact-checking decision.

---

## Dashboard

A Streamlit dashboard was developed to provide an interface for exploring the results of the analysis.

The dashboard contains several sections:

### Overview

Provides a general view of the collected data and the main analysis results.

### Domains

Allows exploration of domains and their associated information.

### ML Engine

Displays machine learning predictions and classification-related results.

### Network

Provides graph-based information and network analysis results.

### Pipeline

Shows the different stages of the data processing and analysis pipeline.

---

## System Architecture

The general workflow of the project can be summarized as:

```text
                    Web Sources
                         |
                         v
                +------------------+
                |   Web Scraping   |
                | Requests/Selenium|
                |   BeautifulSoup  |
                +--------+---------+
                         |
                         v
                +------------------+
                |  Data Storage    |
                | MongoDB / ES     |
                | Neo4j            |
                +--------+---------+
                         |
                         v
                +------------------+
                | Preprocessing    |
                | Cleaning / NLP   |
                +--------+---------+
                         |
             +-----------+-----------+
             |                       |
             v                       v
      +-------------+         +-------------+
      | NLP / ML    |         | Graph       |
      | Analysis    |         | Analysis    |
      +------+------+         +------+------+
             |                       |
             +-----------+-----------+
                         |
                         v
                +------------------+
                | Behavioral       |
                | Analysis         |
                +--------+---------+
                         |
                         v
                +------------------+
                | Unified Suspicion|
                | Score            |
                +--------+---------+
                         |
                         v
                +------------------+
                | Streamlit        |
                | Dashboard        |
                +------------------+
```

---

## Project Structure

```text
projet_cyberintel/
│
├── database/
│   ├── mongo_connector.py
│   ├── neo4j_connector.py
│   └── elastic_connector.py
│
├── datasets/
│   ├── graph_links.json
│   ├── comparaison_finale.png
│   ├── comparaison_modeles.csv
│   ├── stance_analysis.png
│   ├── stylometrie.png
│   ├── suspicion_distribution.png
│   └── ...
│
├── graph_mining/
│   ├── community_detection.py
│   ├── graph_analysis.py
│   └── ...
│
├── scrapers/
│   ├── scraper.py
│   └── ...
│
├── usage_mining/
│   ├── bot_detector.py
│   └── ...
│
├── build_clean_pages.py
├── config.py
├── dashboard.py
├── export_data.py
├── main.py
├── Unified scoring.py
│
├── notebooks/
│   └── ...
│
├── .gitignore
└── README.md
```

> The exact files and modules may change as the project evolves.

---

## Technologies

### Programming

* Python

### Data Collection

* Requests
* Selenium
* BeautifulSoup
* urllib

### Data Processing

* Pandas
* NumPy
* Regular Expressions

### NLP

* NLTK
* Scikit-learn
* BERT
* Sentence Transformers
* TF-IDF

### Machine Learning

* Scikit-learn
* HistGradientBoosting
* Other classification models evaluated during experimentation

### Databases

* MongoDB
* Elasticsearch
* Neo4j

### Graph Analysis

* NetworkX

### Visualization / Interface

* Streamlit
* Matplotlib

---

## Dataset and Results

During the project, more than **2,200 web pages** were collected and processed.

The graph analysis produced approximately:

* **2,102 nodes**
* **4,806 links**
* **22 communities**

The behavioral analysis also produced high bot-related scores for some sources, with a maximum observed Bot Score of approximately **0.984**.

The machine learning experiments resulted in the following final evaluation:

* Accuracy: **95.98%**
* F1-Macro: **0.8492**
* ROC-AUC: **0.9372**

These results are specific to the datasets and experimental setup used in this project.

---

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

```bash
venv\Scripts\activate
```

Or on Linux/macOS:

```bash
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is not included in the repository yet, it should be created from the project's Python environment before attempting a fresh installation.

---

## Configuration

Some components of the project require external services and environment variables.

Sensitive configuration should be stored in a `.env` file.

Example:

```text
MONGO_URI=your_mongodb_connection
ELASTICSEARCH_URL=your_elasticsearch_url
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_username
NEO4J_PASSWORD=your_password
```

**Do not commit your `.env` file or any credentials to GitHub.**

The repository already ignores `.env` through `.gitignore`.

---

## Running the Dashboard

After installing the dependencies and configuring the required services:

```bash
streamlit run dashboard.py
```

The dashboard will then be available locally through Streamlit.

---

## Reproducing the Pipeline

The main processing workflow can be executed through the project scripts.

The general order is:

```text
Data Collection
      ↓
Data Cleaning
      ↓
Database Storage
      ↓
Graph Construction
      ↓
Graph Mining
      ↓
Behavioral Analysis
      ↓
NLP / Feature Extraction
      ↓
Machine Learning
      ↓
Unified Scoring
      ↓
Dashboard
```

Some steps depend on the availability of the corresponding databases and previously generated datasets.

---

## Limitations

The project has several limitations.

* Web scraping results depend on the availability and structure of websites.
* The collected dataset does not represent the entire web.
* Machine learning performance depends on the quality and distribution of the available training data.
* A high suspicion score does not necessarily mean that a page is objectively false.
* Graph relationships depend on the links present in the collected pages.
* Some components require external database services.
* The system is intended as an analytical and research prototype rather than a production-grade fact-checking system.

---

## Future Improvements

Possible improvements include:

* Increasing the size and diversity of the dataset
* Improving the labeling process
* Adding more multilingual NLP models
* Testing larger language models
* Improving graph-based features
* Developing a more advanced RAG-based analysis pipeline
* Improving real-time data collection
* Adding additional threat-intelligence sources
* Improving dashboard interaction and filtering
* Deploying the system as a complete cloud-based service

---
