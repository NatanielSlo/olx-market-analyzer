iPhone Market Analyzer (Modular ETL Scraper)
A asynchronous data pipeline designed to monitor and analyze smartphone market trends on the OLX platform. The project implements a modular Extract, Transform, Load (ETL) architecture, allowing for scalable data collection and refined technical parameter extraction.

Core Features:
- Modular ETL Pipeline: Separation of concerns between link discovery, deep detail extraction, and data normalization.
- Asynchronous Execution: High-performance scraping powered by asyncio and Playwright, utilizing Semaphore for controlled concurrency.
- Stealth Integration: Implementation of playwright-stealth and randomized browser fingerprints to ensure reliable data access.
- Advanced Data Extraction: Automated extraction of battery health, storage capacity, and model specifications from unstructured text using regular expressions and specialized data processors.
- Resilient Storage: Incremental data persistence using .jsonl (JSON Lines) format to ensure data integrity during long-running scraping sessions.

Project Architecture
The system is organized into three distinct execution stages:
- Stage 1: Search Discovery (run_1_general.py)
Initializes the search parameters based on the global configuration.
Aggregates primary listing data (URLs, base prices, titles) into a central repository.
- Stage 2: Technical Detail Extraction (run_2_details.py)
Executes deep dives into individual listings.
Retrieves full descriptions, technical specifications, and publication timestamps.
- Stage 3: Data Transformation & Analysis (run_3_data_handler.py)
Normalizes raw data and standardizes technical parameters.
Prepares datasets for ingestion into analytical warehouses or SQL databases.

Technology Stack
Language: Python 3.13
Automation: Playwright (Chromium)
Concurrency: Asyncio
Data Processing: Regex, Dateparser

Design Pattern: Page Object Model (POM), Modular Architecture

Installation

Clone the repository:
git clone https://github.com/NatanielSlo/olx-market-analyzer.git
cd iphone-market-analyzer

Install dependencies:

pip install -r requirements.txt
playwright install chromium

Execute the pipeline:

python run_1_general.py
python run_2_details.py
python run_3_data_handler.py

Directory Structure:
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