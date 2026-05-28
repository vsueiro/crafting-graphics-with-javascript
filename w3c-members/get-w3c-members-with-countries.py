#!/usr/bin/env python3

import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.w3.org"
LIST_URL = "https://www.w3.org/membership/list/"
OUTPUT_FILE = "members.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) Python scraper"
}


def get_countries():
    """Fetch unique country IDs and names from the country dropdown."""
    print("Fetching country list...")

    response = requests.get(LIST_URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    select = soup.find("select", id="countries")
    if not select:
        raise Exception("Could not find <select id='countries'>")

    countries = []

    for option in select.find_all("option"):
        country_id = option.get("value", "").strip()
        country_name = option.get_text(strip=True)

        # Skip empty/default option
        if not country_id or not country_name:
            continue

        countries.append({
            "countryId": country_id,
            "countryName": country_name
        })

    print(f"Found {len(countries)} countries")
    return countries


def get_members_for_country(country_id):
    """Fetch member links and names for one country."""
    url = f"{LIST_URL}?countries[]={country_id}"
    print(f"Scraping {url}")

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    members = []

    links = soup.find_all("a", class_="card__link")

    for link in links:
        member_name = link.get_text(strip=True)
        href = link.get("href", "").strip()

        if not member_name or not href:
            continue

        member_link = urljoin(BASE_URL, href)

        members.append({
            "memberName": member_name,
            "memberLink": member_link
        })

    print(f"  Found {len(members)} members")
    return members


def main():
    countries = get_countries()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # CSV header
        writer.writerow([
            "countryName",
            "countryId",
            "memberName",
            "memberLink"
        ])

        for country in countries:
            country_name = country["countryName"]
            country_id = country["countryId"]

            try:
                members = get_members_for_country(country_id)

                for member in members:
                    writer.writerow([
                        country_name,
                        country_id,
                        member["memberName"],
                        member["memberLink"]
                    ])

                # polite delay
                time.sleep(1)

            except Exception as e:
                print(f"Error processing {country_name}: {e}")

    print(f"\nDone. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()