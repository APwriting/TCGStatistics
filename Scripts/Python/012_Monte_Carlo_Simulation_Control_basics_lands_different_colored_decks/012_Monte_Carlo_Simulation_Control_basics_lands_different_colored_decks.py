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
#Number of Simulations, duh
global Simulations
Simulations = 100000
#The limit of lands so that a mulligan is not necessary
global Mulligan_limit
Mulligan_limit = 2
#Toggle for saving the individual run statistics
global Save_Monte_Carlo
Save_Monte_Carlo = True




def main():
    Basic_count = define_basic_land_count( colors )

    Category_identities = sorted( list( Basic_count.keys() ) )
    Category_identities.append( "Other" )

    land_combinations = return_basicland_combinations( Basic_count, Population = Decksize, Land_count = Lands, previous_draw = [] )
    land_combinations = dict(zip(Category_identities, land_combinations))#This is the deck population!

    deck = form_deck( combinations = land_combinations )

    if Save_Monte_Carlo:
        file_name = "012_Saved_run_for_plotting__{}_colors.txt".format(colors)
        SAVE = open( file_name, "w")
        print(  "\t".join( [ "Total_runs","Proportion_of_Starting_failure","Proportion_failure_after_draws" ] ) ,file=SAVE)

    Starting_hand_all_basics = dict()
    All_basics_after_draws = dict()#counts the one, where after certain draws all basics were represented.
    for round in range(Simulations):
        
        sample_deck = deck[:]

        Starting_hand_sample = SamplingDraw.choice(sample_deck, size=7, replace=False)
        Card_counts = Count_categories( Sample=Starting_hand_sample )
        Mulligan_necessary = Test_for_mulligan( Categories = Category_identities, Counts = Card_counts )
        if Mulligan_necessary:
            Starting_hand_all_basics[ Mulligan_necessary ] = Starting_hand_all_basics.get( Mulligan_necessary, 0 )+1
        else:
            All_basics_present = Are_all_basics_present( Categories = Category_identities, Counts = Card_counts )
            #print( round,  land_combinations, Starting_hand_sample, Card_counts, All_basics_present )
            Starting_hand_all_basics[ All_basics_present ] = Starting_hand_all_basics.get( All_basics_present, 0 )+1
            #check if with extra draws the thing would be present.
            if not All_basics_present:
                #Adjust deck size by previous draws
                sample_deck_after_sh = Adjust_deck_by_sample( sample_deck, Starting_hand_sample )
                #New draws by previously defiend threshold
                Next_draw = SamplingDraw.choice(sample_deck_after_sh, size=Adraws, replace=False)
                #print(Next_draw)
                #print( "Before",Card_counts )
                for card in Next_draw:
                    Card_counts[str(card)] = Card_counts.get(str(card),0)+1
                #print( "After",Card_counts )
                All_basics_present = Are_all_basics_present( Categories = Category_identities, Counts = Card_counts )
                All_basics_after_draws[All_basics_present] = All_basics_after_draws.get(All_basics_present,0)+1
        if Save_Monte_Carlo:
            Total_runs = round+1
            Proportion_of_Starting_failure = Starting_hand_all_basics.get( False,0 )/Total_runs
            Proportion_failure_after_draws = All_basics_after_draws.get( False,0 )/Total_runs
            print(  "\t".join( [ str(ele) for ele in [Total_runs,Proportion_of_Starting_failure,Proportion_failure_after_draws ]] ) ,file=SAVE)
    SAVE.close()

    #Get the results numbers for starting hands
    All_viable_hands = Starting_hand_all_basics[ True ]+Starting_hand_all_basics[ False ]
    total_hands = Starting_hand_all_basics[ "Mulligan" ] +All_viable_hands
    All_basics_proportion = Starting_hand_all_basics[ True ] / All_viable_hands
    No_basics_proportion = Starting_hand_all_basics[ False ] / All_viable_hands
    Mulligan_proportion = Starting_hand_all_basics[ "Mulligan" ] / total_hands
    print(Starting_hand_all_basics )
    print( "\n\nThere were {} viable hands in total from a total of {} hands.\n".format(All_viable_hands, total_hands) )
    print( "Of these there were {} Mulligans. A proportion of {}.".format(Starting_hand_all_basics[ "Mulligan" ] , Mulligan_proportion))
    print( "Of the viable hands {} ({}) had all basic and {} ({}) not all basics.\n\n".format( All_basics_proportion,Starting_hand_all_basics[ True ], No_basics_proportion, Starting_hand_all_basics[ False ]))
    #After extra draws, how many were now good with basics:
    Aftersh_basics_present_count = All_basics_after_draws.get(True,0)/ Starting_hand_all_basics[ False ]*100
    Aftersh_NO_basics_present_count = All_basics_after_draws.get(False,0)/ Starting_hand_all_basics[ False ]*100
    print( "After {} draws, the following adjustment were present:".format(Adraws) )
    print( "of the {} starting hands without all basis, {} \% drew into their colors.".format(Starting_hand_all_basics[ False ], Aftersh_basics_present_count))
    print( "of the {} starting hands without all basis, {} \% missed colors.".format(Starting_hand_all_basics[ False ], Aftersh_NO_basics_present_count))


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
