#/usr/bin/python

#Script for Monte Carlo Simulaton Confirmation of 011

import numpy as np
SamplingDraw = np.random.default_rng()

import sys

global colors
if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <integer>")
    sys.exit(1)

try:
    colors = int(sys.argv[1])
except ValueError:
    print("Error: argument must be an integer.")
    sys.exit(1)
assert colors <= 6 #Number of colors in Magic and colorless (Wastes)

print(f"Colorcount entered: {colors}")

#Defining values for the rest of the analysis

global Draws
Draws = 7 #Starting hand
#Define acceptable hands.
#Anything with less than 2 lands is an automatic muligan and will not be considered. Automatically mullignaned.
global Land_cutoff
Land_cutoff = 2
#Additional turns/draws after starting hand
global Adraws
Adraws = 5
#Adraws = 1
#Number of lands
global Lands
Lands = 40
#Population/Deck
global Decksize 
Decksize = 99
global Simulations
Simulations = 100






def main():
    Basic_count = define_basic_land_count( colors )

    Category_identities = sorted( list( Basic_count.keys() ) )
    Category_identities.append( "Other" )

    land_combinations = return_basicland_combinations( Basic_count, Population = Decksize, Land_count = Lands, previous_draw = [] )
    land_combinations = dict(zip(Category_identities, land_combinations))#This is the deck population!

    deck = form_deck( combinations = land_combinations )


    for round in range(Simulations):
        
        sample_deck = deck[:]

        Starting_hand_sample = SamplingDraw.choice(sample_deck, size=7, replace=False)
        print( round,  land_combinations, Starting_hand_sample )


def form_deck( combinations ):
    Category_identities = list( combinations.keys() )
    deck = []
    for Category in Category_identities:
        deck += [str(Category)]*combinations[Category]
    return(deck)

def return_basicland_combinations( Basic_count, Population = Decksize , Land_count = Lands, previous_draw = [] ):
    #returns the combination distribution of basic lands, given how many colors are there.
    #Adds all the non lands at the end
    #Adjusts for previous draw combinations

    #Uses dictionaries
    
    Basics = [ category for category in sorted(list(Basic_count.keys()))]

    if previous_draw:
        print(previous_draw)
        non_lands_previous_draw = int(previous_draw.pop())

        lands_in_previous_draw = sum([int(ele) for ele in previous_draw ])

        Land_count -= lands_in_previous_draw #redunant but good for understanding
        Population -= (non_lands_previous_draw + lands_in_previous_draw)
        
        land_combinations = [ Basic_count[land+1]-int( previous_draw[land]) for land in range(len(Basics))]#dictionary Basiccount starts with 1
        #print( Basic_count, land_combinations)
        
    else:
        land_combinations = [ Basic_count[category] for category in Basics]
    land_combinations.append( Population-Land_count )
    
    #print(land_combinations )
    return( land_combinations )

def define_basic_land_count( colors ):
    #defines the basic land count for the given amount of colors 
    #without any extra calculations like duals or pips.
    Basic_count = dict()
    i = 0
    basic_land_type = 1
    while (i < Lands):
        if basic_land_type>colors:
            basic_land_type = 1
        Basic_count[ basic_land_type ] = Basic_count.get( basic_land_type, 0) + 1
        i += 1
        basic_land_type +=1

    return(Basic_count)











main()
