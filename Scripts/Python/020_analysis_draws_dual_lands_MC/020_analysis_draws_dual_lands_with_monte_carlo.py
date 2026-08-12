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
Simulations = 10000
#The limit of lands so that a mulligan is not necessary
global Mulligan_limit
Mulligan_limit = 2
#Toggle for saving the individual run statistics
global Save_Monte_Carlo
Save_Monte_Carlo = True

################################################################################################


def main():

    #Define Categories, number of basic land types

    Basic_count = define_basic_land_count( colors ) #Define basics for later on

    #Generate possible dual land categories from the colors
    Basic_names = list(Basic_count.keys())

    Duals = create_dual_land_categories( Basic_names )

    #to_write_list = list()  #Easier to save the lines in the for loop and write everything clean later.

    Different_probabilities_numbers = [ str(i) for i in range(colors+1) ]
    Different_probabilities_numbers.append( "Mulligan" )

    ####################
    

    file_name = "020_Saved_run_for_plotting__{}_colors.txt".format(colors)
    SAVE = open( file_name, "w")
    print(  "\t".join( [ "Dual_land","Cards_drawn","Color_Counts","Color_Counts_during_trials" ] ) ,file=SAVE)


    #Go through each possible number of dual_lands
    for Dual_trial in range( Lands+1 ):
        Updated_duals = distribute_land_count(counter = Duals, land_count = Dual_trial)


        Updated_land_base = add_duals_to_land_base(Basic_color_land_base = Basic_count.copy(), duals_to_add = Updated_duals)
        Updated_land_base = Add_other_category(counter = Updated_land_base)
        #print( Updated_land_base)
        #Updated_land_base_copy = Updated_land_base.copy()


        #Start tinkering
        Updated_land_base_keys = sorted([str(ele) for ele in list( Updated_land_base.keys() )])
        #print( "Updated_land_base_keys", "Updated_land_base_keys", Updated_land_base_keys )



        Category_identities = sorted( [ str( ele ) for ele in list( Updated_land_base.keys() ) ] )

        #print( Category_identities )

        deck = form_deck( combinations = Updated_land_base )
        #print( deck )
        #print("Test")
        #proxy = input()
        Sample_runs_2_color_count = Monte_carlo_simulation( repertitions= Simulations, deck = deck, Category_identities = Updated_land_base_keys, Starting_hand = True, lower_range = 7, higher_range = 7 )
        number_drawn_run = sorted( list( Sample_runs_2_color_count.keys() ))
        for run in number_drawn_run:
            print( run, "RUNNNN")
            Color_count = Sample_runs_2_color_count[ run ]
            Counts = sorted( list( Color_count.keys() ))
            for count in Different_probabilities_numbers:
                print( "\t".join([ str(ele) for ele in [Dual_trial, run, count, Color_count.get( count, 0 ) ] ]), file=SAVE )
    SAVE.close()
    sys.exit()
################################################################################################



   # land_combinations = return_basicland_combinations( Basic_count, Population = Decksize, Land_count = Lands, previous_draw = [] )
    #land_combinations = dict(zip(Category_identities, land_combinations))#This is the deck population!

 #   deck = form_deck( combinations = land_combinations )


    Starting_hand_all_basics = dict()
    All_basics_after_draws = dict()#counts the one, where after certain draws all basics were represented.
    for round in range(Simulations):
        sys.exit()
        #sample_deck = deck[:]

        #Starting_hand_sample = SamplingDraw.choice(sample_deck, size=7, replace=False)
        #Card_counts = Count_categories( Sample=Starting_hand_sample )
        #Mulligan_necessary = Test_for_mulligan( Categories = Category_identities, Counts = Card_counts )
        if Mulligan_necessary:
            pass
            #Starting_hand_all_basics[ Mulligan_necessary ] = Starting_hand_all_basics.get( Mulligan_necessary, 0 )+1
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


################################################################################################
################################################################################################

def Monte_carlo_simulation( repertitions, deck, Category_identities, Starting_hand = False, lower_range = 7, higher_range = 7 ):
    #Doing Monte Carlo Runs Land tests

    if Starting_hand:
        lower_range = 7
        higher_range = 8

    Sample_runs_2_color_count = dict()
    
    for sample_size in range( lower_range, higher_range ):
        print( sample_size, "sample_size")
        Color_count = dict()
        for round in range(repertitions ):
        
            sample_deck = deck[:]

            MC_Sample = SamplingDraw.choice(sample_deck, size=sample_size, replace=False)
            Card_counts = Count_categories( Sample=MC_Sample )
            if Starting_hand:   #extra test fpr mulligan if the whole ordeal is supposed to test the starting hand.
                Mulligan_necessary = Test_for_mulligan( Categories = Category_identities, Counts = Card_counts )
                if Mulligan_necessary:
                    Color_count[ Mulligan_necessary ] = Color_count.get( Mulligan_necessary, 0 )+1
            else:
                Mulligan_necessary = False
            
            print( MC_Sample, Mulligan_necessary, Card_counts )

            #Count Colors
            #Counte Colors function
            available_colors = count_available_colors( Card_counts )
            print( "COLORS:", available_colors)
            print("Test")
            MC_run_color_count = str( len( available_colors ) )
            print( "MC_run_color_count", MC_run_color_count )
            Color_count[ MC_run_color_count ] = Color_count.get( MC_run_color_count, 0 )+1
            print( "Color_count", Color_count )
            #proxy = input()
        Sample_runs_2_color_count[ sample_size ] = Color_count
    return( Sample_runs_2_color_count )

################################################################################################

def add_duals_to_land_base(Basic_color_land_base, duals_to_add):
    Basics  = sorted( [ str(ele) for ele in list(Basic_color_land_base.keys()) ] )

    Current_Basic_to_fix_ID = 0
    for dual, count in duals_to_add.items():
        Basic_color_land_base[dual] += count


        for _ in range(count):
            Basic_to_fix = int( Basics[ Current_Basic_to_fix_ID ] )
            Basic_color_land_base[ Basic_to_fix ] -= 1
            if Current_Basic_to_fix_ID == len( Basics )-1:
                Current_Basic_to_fix_ID = 0
            else:
                Current_Basic_to_fix_ID += 1

    return Basic_color_land_base


def Add_other_category(counter):
    other_count = Decksize - sum(
        count for key, count in counter.items()
        if key != "Other"
    )

    counter["Other"] = other_count

    return counter

def create_dual_land_categories( basics ):

    duals = []
    for i in range( len( basics ) ):
        for j in range(i+1,len(basics)):
            dual_land = "{}_{}".format(basics[i],basics[j])

            duals.append( dual_land )
    return( Counter(duals) )


def count_available_colors(counter):
    available_colors = set()

    for key in counter.keys():
        if key == "Other":
            continue

        if counter[key] != 0:

            colors = str(key).split("_")

            for color in colors:
                available_colors.add(color)

    return available_colors

#def create_dual_land_categories( basics ):



def distribute_land_count(counter, land_count):
    keys = sorted(counter.keys())
    
    base_count = land_count // len(keys)
    remainder = land_count % len(keys)

    for i, key in enumerate(keys):
        counter[key] = base_count
        
        if i < remainder:
            counter[key] += 1

    return counter

################################################################################################ 

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
    Basic_count = Counter(Basic_count)
    return(Basic_count)











main()
