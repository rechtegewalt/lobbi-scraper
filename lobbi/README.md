# LOBBI Scraper

Scraping right-wing incidents in Mecklenburg-Western Pomerania (_Mecklenburg-Vorpommern_), Germany as monitored by the NGO [LOBBI](https://lobbi-mv.de/).

-   Website: <https://lobbi-mv.de/monitoring/>
-   Data: <https://morph.io/rechtegewalt/lobbi-scraper>

## Usage

For local development:

-   Install [poetry](https://python-poetry.org/)
-   `poetry install`
-   `poetry run python scraper.py`

For Morph:

-   `poetry export -f requirements.txt --output requirements.txt`
-   commit the `requirements.txt`
-   modify `runtime.txt`

## Morph

This is scraper runs on [morph.io](https://morph.io). To get started [see the documentation](https://morph.io/documentation).
