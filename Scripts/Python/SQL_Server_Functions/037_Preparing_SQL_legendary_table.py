import subprocess
import sys
from pathlib import Path
import yaml
import requests
import time

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, Text

from sqlalchemy import inspect

import MTG_SQL as Msql

# ============================================================
# Configuration
# ============================================================

KUBE_CONTEXT = "kind-carddata"
DATABASE_NAME = "MTGDATA"

DB_PORT = 5436

# PostgreSQL Kubernetes Service
DB_SERVICE = "postgres"

# PostgreSQL credentials
DB_USER = "postgres"
DB_PASSWORD = "postgres"


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
Tables_to_Create = [
    "Legendary_creatures"

]
Force = 1


def main():

    deploy_yaml_path = "../Kubernetes_cluster_initiation_SQL_database/postgreSQL_deployment__credentials.yaml"
    DB_USER, DB_PASSWORD  = get_sql_credentials(deployment_yaml = deploy_yaml_path)

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


    port_forward_process = None
    engine = None


    try:
        port_forward_process = start_port_forward()

        engine = create_engine(
            f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
            f"@127.0.0.1:{DB_PORT}/{DATABASE_NAME}",
            connect_args={"connect_timeout": 5}
        )

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"SQLAlchemy connection successful: {result.scalar()}")

    finally:
        print( "SQLAlchemy engine created. Connected.")

    inspector = inspect(engine)
    Table_names = inspector.get_table_names()

    #Table_names = engine.table_names()
    print(Table_names)

    # Create a MetaData object

    #Inspector = inspect(engine)

    for Table_name in Tables_to_Create:
        if Table_name not in Table_names:
            metadata = MetaData()

            legendary_table = Table( "legendary_table", metadata )            
            print( "Generating Table..." )
            
            #Adding Table elements
            for column_name in card_data:
                legendary_table.append_column( Column(column_name, Text) )

            legendary_table.create(engine, checkfirst=True)

    OUT = open("Commanders_by_years.txt","w")
    for year in range(1994,2027):
        print( f"Checking year {year} for legendary creatures....")

        Scryfall_Query = f"type:legendary is:firstprinting year:{year} is:commander"
        print( Scryfall_Query )
        Search_results_scryfall = get_all_cards(search_query = Scryfall_Query)
        #Put here preparations for the database


        #Print the general information for later use.

        print( str(year)+"\t"+str(len(Search_results_scryfall)), file = OUT  )
    OUT.close()

    if engine is not None:
        engine.dispose()

    if port_forward_process is not None:
        stop_port_forward(port_forward_process)


    return 1




###########################################################################################################################################################
#Functions





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

def get_all_cards(search_query):
    time.sleep(0.1)

    url = "https://api.scryfall.com/cards/search"
    params = {"q": search_query}

    headers = {
        "User-Agent": "MagicDeckStatistics/1.0"
    }

    all_cards = []

    while url:
        response = requests.get(
            url,
            params=params,
            headers=headers
        )

        response.raise_for_status()
        data = response.json()

        all_cards.extend(data["data"])

        if data["has_more"]:
            url = data["next_page"]
            params = None
            time.sleep(0.1)
        else:
            url = None

    return all_cards


def number_of_cards(search_query):
    time.sleep(0.1)
    url = "https://api.scryfall.com/cards/search"

    headers = {
        "User-Agent": "MagicDeckStatistics/1.0"
    }

    response = requests.get(
        url,
        params={"q": search_query},
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    return data["total_cards"]


def start_port_forward():
    """Start kubectl port-forward in the background."""

    command = [
        "kubectl",
        "--context", KUBE_CONTEXT,
        "port-forward",
        f"service/{DB_SERVICE}",
        f"{DB_PORT}:{DB_PORT}",
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait until the local port becomes available.
    import socket

    for _ in range(50):
        if process.poll() is not None:
            error = process.stderr.read()
            raise RuntimeError(
                f"Port forwarding failed:\n{error}"
            )

        try:
            with socket.create_connection(
                ("127.0.0.1", DB_PORT), timeout=0.2
            ):
                print(
                    f"Port forwarding active on "
                    f"localhost:{DB_PORT}"
                )
                return process
        except OSError:
            time.sleep(0.2)

    process.terminate()
    process.wait(timeout=5)
    raise RuntimeError("Timed out waiting for port forwarding.")

#Getting User data from deployment YAML:

def get_sql_credentials(deployment_yaml):
    """
    Read PostgreSQL username and password from a Kubernetes
    Deployment YAML file.

    Returns:
        tuple[str, str]: username, password
    """

    with open(deployment_yaml, "r", encoding="utf-8") as file:
        deployment = yaml.safe_load(file)

    containers = deployment["spec"]["template"]["spec"]["containers"]

    for container in containers:
        for env in container.get("env", []):

            if env["name"] == "POSTGRES_USER":
                username = env["value"]

            elif env["name"] == "POSTGRES_PASSWORD":
                password = env["value"]

    return username, password

def stop_port_forward(process):
    """Stop the kubectl port-forward subprocess."""

    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

if __name__ == "__main__":
    sys.exit(main())






    