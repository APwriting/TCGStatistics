#/usr/bin/python

#Script for Monte Carlo Simulaton Confirmation of 011

import numpy as np
SamplingDraw = np.random.default_rng()
from collections import Counter

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
#Number of lands
global Lands
Lands = 40
#Population/Deck
global Decksize 
Decksize = 99
#Number of Simulations, duh
global Simulations
Simulations = 10000
#The limit of lands so that a mulligan is not necessary, defined to be clear and have options in script
global Mulligan_limit
Mulligan_limit = 2
#Toggle for saving the individual run statistics
global Save_Monte_Carlo
Save_Monte_Carlo = True




def main():
    Basic_count = define_basic_land_count( current_colors )

    Category_identities = sorted( list( Basic_count.keys() ) )
    Category_identities.append( "Other" )

    land_combinations = return_basicland_combinations( Basic_count, Population = Decksize, Land_count = Lands, previous_draw = [] )
    land_combinations = dict(zip(Category_identities, land_combinations))#This is the deck population!

    deck = form_deck( combinations = land_combinations )



    Starting_hand_all_basics = dict()
    turns_until_all_colors = list()
    for round in range(Simulations):

        Total_runs = round+1
        sample_deck = deck[:]

        Starting_hand_sample = SamplingDraw.choice(sample_deck, size=7, replace=False)
        Card_counts = Count_categories( Sample=Starting_hand_sample )
        Mulligan_necessary = Test_for_mulligan( Categories = Category_identities, Counts = Card_counts )
        if Mulligan_necessary:
            Starting_hand_all_basics[ Mulligan_necessary ] = Starting_hand_all_basics.get( Mulligan_necessary, 0 )+1
        else:
            All_basics_present = Are_all_basics_present( Categories = Category_identities, Counts = Card_counts )
            Starting_hand_all_basics[ All_basics_present ] = Starting_hand_all_basics.get( All_basics_present, 0 )+1
            #check if with extra draws the thing would be present.
            if not All_basics_present:
                #Adjust deck
                sample_deck_after_sh = Adjust_deck_by_sample( sample_deck, Starting_hand_sample )
                Turn_count = 0
                #Go into while loop
                while (not All_basics_present):
                    #Take a sample of one draw
                    Next_draw = SamplingDraw.choice(sample_deck_after_sh, size=1, replace=False)
                    sample_deck_after_sh = Adjust_deck_by_sample( sample_deck_after_sh, Next_draw )

                    #Adjust card counts from already drawn
                    for card in Next_draw:
                        Card_counts[str(card)] = Card_counts.get(str(card),0)+1
                    All_basics_present = Are_all_basics_present( Categories = Category_identities, Counts = Card_counts )
                    Turn_count+=1

                turns_until_all_colors.append( Turn_count )
                if Save_Monte_Carlo:
                    print(  "\t".join( [ str(Total_runs),str(Turn_count),str(current_colors) ] ) ,file=SAVE)

            else:
                turns_until_all_colors.append( 0 )
                if Save_Monte_Carlo:
                    print(  "\t".join( [ str(Total_runs),"0",str(current_colors) ] ) ,file=SAVE)

    Average_number_of_turns = sum(turns_until_all_colors)/len(turns_until_all_colors)

    print( "Over {} Simulations, it took an average of {} turns until all colors are reached for a {} color deck with only basics".format(Simulations,Average_number_of_turns,current_colors))

def Adjust_deck_by_sample( sample_deck, past_draws ):
    #Important function to adjust the actual deck counts.
    remove = Counter(past_draws)
    remaining = []

    for card in sample_deck:
        if remove[card]:
            remove[card] -= 1
        else:
            remaining.append(card)
    return( remaining )


def Test_for_mulligan( Categories, Counts ):
    #Gives back if all basic lands are present
    total_lands = 0
    for cat in Categories:
        if cat != "Other":
            total_lands += Counts.get( str(cat), 0 )
    if total_lands >= Mulligan_limit:
        return( False )
    else:
        return( "Mulligan" )

def Count_categories( Sample ):
    return( dict(Counter(Sample)) )

def Are_all_basics_present( Categories, Counts ):
    #Gives back if all basic lands are present
    all_present = 1
    for cat in Categories:
        if cat != "Other":
            all_present = all_present*Counts.get( str(cat), 0 )
    return( all_present > 0 )

def Count_categories( Sample ):
    return( dict(Counter(Sample)) )


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
    
    Basics = [ category for category in sorted(list(Basic_count.keys()))]

    if previous_draw:
        print(previous_draw)
        non_lands_previous_draw = int(previous_draw.pop())

        lands_in_previous_draw = sum([int(ele) for ele in previous_draw ])

        Land_count -= lands_in_previous_draw #redunant but good for understanding
        Population -= (non_lands_previous_draw + lands_in_previous_draw)
        
        land_combinations = [ Basic_count[land+1]-int( previous_draw[land]) for land in range(len(Basics))]#dictionary Basiccount starts with 1
        
    else:
        land_combinations = [ Basic_count[category] for category in Basics]
    land_combinations.append( Population-Land_count )

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




if Save_Monte_Carlo:
    file_name = "014_Simulations_{}_until_all_colors__maximum_{}_colors.txt".format(Simulations,colors)
    SAVE = open( file_name, "w")
    print(  "\t".join( [ "Total_runs","Turns","Color_count" ] ) ,file=SAVE)
global current_colors
for color in range(colors):
    current_colors = color+1
    main()
if Save_Monte_Carlo:
    SAVE.close()


