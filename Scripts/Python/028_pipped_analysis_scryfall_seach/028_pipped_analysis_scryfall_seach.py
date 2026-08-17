#/usr/bin/python



import requests
import sys

################################################################################################


#general search pattern
#mana:/^(?:\{[0-9]+\})?\{R\}\{R\}\{R\}$/




def main():
    query = "name:avatar"

    query_color_pattern = "\\{INSERT_COLOR\\}"
    scry_fall_template = "mana:/^(?:\\{[0-9]+\\})?INSERT_PIPS$/"
    Colors = ["W", "U" , "B", "R", "G" ]

    OUT = open("028_results_colored_pips_scryfall_search.txt", "w")
    print( "Color\tPips\tresults", file = OUT)

    for color in Colors:
        print( query_color_pattern )
        color_search_pattern = query_color_pattern.replace(  "INSERT_COLOR", color )
        print( color_search_pattern )
        for i in range(2,6):
            total_color_search_pattern = color_search_pattern*i
            print( total_color_search_pattern )
            scryfall_search_pattern = scry_fall_template.replace( "INSERT_PIPS",total_color_search_pattern )
            print( scryfall_search_pattern )
            try:
                scryfall_result = number_of_cards(search_query = scryfall_search_pattern)
            except:
                scryfall_result = 0
            print( scryfall_result )
            result_list = [ color, str(i), str(scryfall_result) ]
            print( "\t".join(result_list), file = OUT)
            #sys.exit()
    OUT.close()
    return(1)
    #sys.exit()

    scryfall_result = number_of_cards(search_query = query)
    print( scryfall_result )













################################################################################################

def number_of_cards(search_query):
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



main()