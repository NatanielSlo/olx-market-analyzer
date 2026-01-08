# iPhone Market Analyzer (Modular ETL Scraper)

A professional asynchronous data pipeline designed for monitoring and analyzing smartphone market trends on the OLX platform. The project implements a modular Extract, Transform, Load (ETL) architecture, facilitating scalable data collection and technical parameter extraction.

## Core Features

* **Modular ETL Pipeline:** Strict separation of concerns between link discovery, deep detail extraction, and data normalization.
* **Asynchronous Execution:** High-performance scraping powered by `asyncio` and `Playwright`, utilizing `Semaphore` for controlled concurrency.
* **Stealth Integration:** Implementation of `playwright-stealth` and randomized browser fingerprints to ensure reliable data access and bypass basic bot detection.
* **Advanced Data Extraction:** Automated parsing of battery health, storage capacity, and model specifications from unstructured text using regular expressions and specialized processors.
* **Resilient Storage:** Incremental data persistence using `.jsonl` (JSON Lines) format to ensure data integrity during long-running sessions.

## Project Architecture

The system is organized into three distinct execution stages:

1.  **Stage 1: Search Discovery** (`run_1_general.py`)
    * Initializes search parameters based on global configuration.
    * Aggregates listing URLs, titles, and base prices into a central repository.
2.  **Stage 2: Technical Detail Extraction** (`run_2_details.py`)
    * Executes deep dives into individual listings.
    * Retrieves full descriptions, technical specifications, and publication timestamps.
3.  **Stage 3: Data Transformation & Analysis** (`run_3_data_handler.py`)
    * Normalizes raw data and standardizes technical parameters.
    * Prepares datasets for ingestion into analytical warehouses or SQL databases.

## Technology Stack

* **Language:** Python 3.13
* **Automation:** Playwright (Chromium)
* **Concurrency:** Asyncio
* **Data Processing:** Regex, Dateparser, Pandas
* **Design Pattern:** Page Object Model (POM), Modular Architecture

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/NatanielSlo/olx-market-analyzer.git](https://github.com/NatanielSlo/olx-market-analyzer.git)
    cd iphone-market-analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **Execute the pipeline:**
    ```bash
    python run_1_general.py
    python run_2_details.py
    python run_3_data_handler.py
    ```

## Directory Structure

```text
project-root/
├── src/
│   ├── core/           # Business logic and scraper implementations
│   ├── pages/          # Page Object Model definitions
│   ├── utils/          # Specialized data processors and URL builders
│   └── config.py       # Global operational parameters
├── data/               # Local data storage (ignored by git)
├── run_1_general.py    # Link discovery entry-point
├── run_2_details.py    # Detail extraction entry-point
└── run_3_data_handler.py # Data normalization entry-point
