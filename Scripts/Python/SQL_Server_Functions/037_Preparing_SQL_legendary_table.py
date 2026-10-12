import subprocess
import sys
from pathlib import Path

import requests

import MTG_SQL as Msql

SQL_CHECK_SCRIPT = Path(__file__).parent / "036_SQL_service_checking.py"
LOG_FILE = Path(__file__).parent / "sql_service_checking.log"

card_data = [
    "object",
    "id",
    "oracle_id",
    "multiverse_ids",
    "name",
    "released_at",
    "uri",
    "scryfall_uri",
    "layout",
    "highres_image",
    "image_status",
    "image_updated_at",
    "image_uris",
    "mana_cost",
    "cmc",
    "type_line",
    "oracle_text",
    "power",
    "toughness",
    "colors",
    "color_identity",
    "keywords",
    "legalities",
    "games",
    "reserved",
    "game_changer",
    "reprint",
    "variation",
    "set_id",
    "set",
    "set_name",
    "set_type",
    "set_uri",
    "set_search_uri",
    "scryfall_set_uri",
    "rulings_uri",
    "prints_search_uri",
    "collector_number",
    "digital",
    "rarity",
    "watermark",
    "flavor_text",
    "card_back_id",
    "artist",
    "artist_ids",
    "illustration_id",
    "border_color",
    "frame",
    "security_stamp",
    "textless",
    "booster",
    "story_spotlight",
    "edhrec_rank",
    "penny_rank",
]

def main():

    LOG = open(LOG_FILE,"w")
    print("Starting SQL table creation and update", file = LOG)
    LOG.close()
    #Testing for SQL cluster availability
    Msql.check_cluster_availability(file_name = SQL_CHECK_SCRIPT, log_file = LOG_FILE)

    #Getting example card data.

    Example_legendary = "Nicol Bolas"
    example_card = get_card_data(card_name = Example_legendary)

    print( example_card )

    scryfall_card_descriptors = list(example_card.keys())

    LOG = open(LOG_FILE,"a")

    for column_name in scryfall_card_descriptors:
        if column_name not in card_data:
            print(f"{column_name} not relevant. Skipping for table creation.", file = LOG )

    LOG.close()
    return 1




###########################################################################################################################################################
#Functions



import requests

def get_card_data(card_name: str) -> dict:
    url = "https://api.scryfall.com/cards/named"

    response = requests.get(
        url,
        params={"fuzzy": card_name},
        headers={
            "User-Agent": "MTGStatistics/1.0",
            "Accept": "application/json"
        },
        timeout=10
    )

    #print("Status:", response.status_code)
    #print("Response:", response.text)

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    sys.exit(main())






    