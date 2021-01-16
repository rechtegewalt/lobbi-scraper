import re

import dataset
import get_retries
from bs4 import BeautifulSoup
from dateparser import parse

from tqdm import tqdm

db = dataset.connect("sqlite:///data.sqlite")

tab_incidents = db["incidents"]
tab_sources = db["sources"]
tab_chronicles = db["chronicles"]


tab_chronicles.insert(
    {
        "iso3166_1": "DE",
        "iso3166_2": "DE-MV",
        "chronicler_name": "LOBBI",
        "chronicler_description": "Landesweite Opferberatung, Beistand und Information für Betroffene rechter Gewalt in Mecklenburg-Vorpommern",
        "chronicler_url": "https://lobbi-mv.de/",
        "chronicle_source": "https://lobbi-mv.de/monitoring/",
    }
)


BASE_URL = "https://lobbi-mv.de/such-ergebnisse-chronologie/?ort=&landkreis=&delikt=&motiv=&von=&bis="


def fetch(url):
    html_content = get_retries.get(url, verbose=True, max_backoff=128).text
    soup = BeautifulSoup(html_content, "lxml")
    return soup


def process_report(report, add_sources=False, **kwargs):
    county = report.find("span", class_="title-zusatz-landkreis").extract().get_text()
    county = re.sub(r"[()]", "", county).strip()

    # only text elements
    date_city = report.find("h3").find(text=True)

    date, city = date_city.split(" - ")
    date = parse(date, languages=["de"])

    sources = []
    for x in report.select("li.quelle"):
        sources += x.get_text().replace("Quelle: ", "").replace("; ", ", ").split(",")
    sources = [x.strip() for x in sources]

    description = report.select_one("p.intro-content").get_text().strip()

    rg_id = "lobbi-mv-" + report.get("id")
    only_id = re.findall(r"\d+", rg_id)[0]
    url = "https://lobbi-mv.de/?p=" + only_id

    # print(url, city, county, date, city, sources, description)

    data = dict(
        url=url,
        rg_id=rg_id,
        date=date,
        city=city,
        county=county,
        description=description,
        chronicler_name="LOBBI",
    )

    # merge with other values
    data = {**data, **kwargs}

    # was not sure if we have to be careful to not override old values
    # but motives and factums can only have on value (on lobbi-mv.de)

    # print(data)
    # old_data = tab_incidents.find_one(rg_id=rg_id)

    # if old_data is not None:
    #     # print('old_data')
    #     if 'factums' in old_data and old_data['factums']:
    #         print('x')
    #         data['factums'] = ', ' + old_data['factums']
    #     if 'motives' in old_data and old_data['motives']:
    #         print('y')
    #         data['motives'] = ', ' + old_data['motives']
    # print(data)

    tab_incidents.upsert(data, ["rg_id"])

    if add_sources:
        sources_data = [dict(rg_id=rg_id, name=x) for x in sources]
        for x in sources_data:
            tab_sources.insert(x)


all_posts = fetch(BASE_URL)

for report in tqdm(all_posts.select("article.category-chronologie")):
    process_report(report, add_sources=True)


for x in tqdm(all_posts.select("#exampleList_delikt option")):
    x = x.get_text().strip()
    url = f"https://lobbi-mv.de/such-ergebnisse-chronologie/?ort=&landkreis=&delikt={x}&motiv=&von=&bis="
    new_site = fetch(url)
    print(x)
    print(url)
    for report in new_site.select("article.category-chronologie"):
        process_report(report, factums=x)

for x in tqdm(all_posts.select("#exampleList_motiv option")):
    x = x.get_text().strip()
    url = f"https://lobbi-mv.de/such-ergebnisse-chronologie/?ort=&landkreis=&delikt=&motiv={x}&von=&bis="
    print(x)
    print(url)
    new_site = fetch(url)
    for report in new_site.select("article.category-chronologie"):
        process_report(report, motives=x)
