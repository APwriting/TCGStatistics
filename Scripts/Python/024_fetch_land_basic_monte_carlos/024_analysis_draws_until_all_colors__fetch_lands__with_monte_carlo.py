#/usr/bin/python

#Script for Monte Carlo Simulaton Confirmation of 011

import numpy as np
SamplingDraw = np.random.default_rng()
from collections import Counter
from pathlib import Path

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
Simulations = 1000
#The limit of lands so that a mulligan is not necessary
global Mulligan_limit
Mulligan_limit = 2
#Toggle for saving the individual run statistics
global Save_Monte_Carlo
Save_Monte_Carlo = False

################################################################################################

#Add fetch land adding function
#Add funcitonality to look for FETCH when looking for categories.
#Add checker and changer for deck

#Other approach is to directly fix FETCH in draws, if it works, remove deck functionality from color counting functions for FETCHEs

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
    

    file_name = "024_Saved_run_for_plotting__{}_colors.txt".format(colors)
    SAVE = open( file_name, "w")
    print(  "\t".join( [ "Dual_land","Cards_drawn","Color_Counts","Color_Counts_during_trials" ] ) ,file=SAVE)


    #Go through each possible number of dual_lands
    for Dual_trial in range( 16 ):
        Updated_duals = distribute_land_count(counter = Duals, land_count = Dual_trial)


        #Updated_land_base = add_duals_to_land_base(Basic_color_land_base = Basic_count.copy(), duals_to_add = Updated_duals)
        #Updated_land_base = Add_other_category(counter = Updated_land_base)

        #Updated_land_base = add_all_color_land_to_land_base(Basic_color_land_base = Basic_count.copy(), lands_to_add = Dual_trial)#Dual trial is only a proxy for number of lands to add.
        #Updated_land_base = Add_other_category(counter = Updated_land_base)
        #print( Updated_land_base, "Updated_land_base")

        Updated_land_base = add_fetch_land_to_land_base(Basic_color_land_base = Basic_count.copy(), lands_to_add = Dual_trial)#Dual trial is only a proxy for number of lands to add.
        Updated_land_base = Add_other_category(counter = Updated_land_base)
        print( Updated_land_base, "Updated_land_base")

        #proxy = input()

        #Start tinkering
        Updated_land_base_keys = sorted([str(ele) for ele in list( Updated_land_base.keys() )])


        #Category_identities = sorted( [ str( ele ) for ele in list( Updated_land_base.keys() ) ] )

        deck = form_deck( combinations = Updated_land_base )
        #print( deck )
        Sample_runs_2_color_count = Monte_carlo_simulation( repertitions= Simulations, deck = deck, Category_identities = Updated_land_base_keys, Starting_hand = False, lower_range = 7, higher_range = 8, Trial_count = Dual_trial )
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


################################################################################################
################################################################################################

def Monte_carlo_simulation( repertitions, deck, Category_identities, Starting_hand = False, lower_range = 7, higher_range = 7, Trial_count = 0 ):
    #Doing Monte Carlo Runs Land tests

    if Starting_hand:
        lower_range = 7
        higher_range = 8

    Sample_runs_2_color_count = dict()
    #print( Category_identities, "I need these right?")
    Color_set_to_test_availability = Category_identities[:]
    if "ALL" in Color_set_to_test_availability:
        Color_set_to_test_availability.remove("ALL")
    if "FETCH" in Color_set_to_test_availability:
        Color_set_to_test_availability.remove("FETCH")
    Color_set_to_test_availability.remove("Other")

    for sample_size in range( lower_range, higher_range ):
        #print( sample_size, "sample_size")
        Color_count = dict()
        for round in range(repertitions ):
        
            sample_deck = deck[:]
            #sample_deck[ 0 ] = "FETCH"
            #sample_deck[ 1 ] = "FETCH"
            #sample_deck[ 2 ] = "FETCH"
            #print( sample_deck)
            #Color_count = Color_count_base.copy()
            MC_Sample = SamplingDraw.choice(sample_deck, size=sample_size, replace=False)
            #For testing!!!!!!!Testing Fetch repalcing function
            #MC_Sample[0]="FETCH"


            Card_counts = Count_categories( Sample=MC_Sample )
            #if Starting_hand:   #extra test fpr mulligan if the whole ordeal is supposed to test the starting hand.
            Mulligan_necessary = Test_for_mulligan( Categories = Category_identities, Counts = Card_counts )

            
            print( MC_Sample, Mulligan_necessary, Card_counts )

            #Count Colors
            #Counte Colors function
            print( Color_set_to_test_availability, "Color_set_to_test_availability TESTTTTTTTT" )
           # proxy = input()
            available_colors = count_available_colors( Card_counts )
            MC_run_color_count = str( len( available_colors ) )
            print( Color_set_to_test_availability, "Color_set_to_test_availability TESTTTTTTTT2222" )
          #  proxy = input()
            #Draws untila all colors
            sample_deck_after_sh = Adjust_deck_by_sample( sample_deck, MC_Sample )
            print( Color_set_to_test_availability, "Color_set_to_test_availability TESTTTTTTTT2222" )
          # proxy = input()
            if "FETCH" in Card_counts:  #For purpose of other sumulation this would not work for turn 0
                sample_deck_after_sh, Card_counts = change_Fetch_in_draw( sample_deck = sample_deck_after_sh, draw = Card_counts,  Color_set_to_test_availability = Color_set_to_test_availability, available_colors = available_colors )

                #sys.exit()
            #turn_file_path = Path("022_turns_until_all_colors__{}__dual_lands__MC_simulation.txt".format(colors))
            turn_file_path = Path("024_turns_until_all_colors__{}__fetch_lands__MC_simulation.txt".format(colors))
            if (not turn_file_path.exists() or Trial_count == 0) and round == 0:
                print("File does not exists")
                OUT = open( turn_file_path, "w")
                print( "Trial_land_count\tcolors\ttrial_number\tturns_until_all_colors\tMulligan", file = OUT)
            else:
                OUT = open( turn_file_path, "a")

            turn = 0
            if int(MC_run_color_count) < colors:
                while ( int(MC_run_color_count) < colors or turn == 0):

                    turn +=1
                    Next_draw = SamplingDraw.choice(sample_deck_after_sh, size=1, replace=False)
                    #Next_draw = ["FETCH"]
                    #print( len( sample_deck_after_sh), "Before")
                    sample_deck_after_sh = Adjust_deck_by_sample( sample_deck_after_sh, Next_draw )
                    #print( len( sample_deck_after_sh), "After")
                    if "FETCH" in Next_draw:  #For purpose of other sumulation this would not work for turn 0
                        print( Next_draw, "BEFORE" )
                        sample_deck_after_sh, Next_draw = change_Fetch_in_draw( sample_deck = sample_deck_after_sh, draw = Next_draw,  Color_set_to_test_availability = Color_set_to_test_availability, available_colors = available_colors )
                        print( len(sample_deck_after_sh ), "sample_deck_after_sh")
                        print( Next_draw, "AFTER" )
                        #sys.exit()

                    #proxy = input()
                    for card in Next_draw:
                        Card_counts[str(card)] = Card_counts.get(str(card),0)+1
                    available_colors = count_available_colors( Card_counts )
                    MC_run_color_count = str( len( available_colors ) )
                    
                    #print( turn, MC_run_color_count, Next_draw, Card_counts )
            print_list = [str(ele) for ele in [ Trial_count, colors, round, turn, Mulligan_necessary  ] ]

            print( "\t".join(print_list), file = OUT)
            Color_count[ MC_run_color_count ] = Color_count.get( MC_run_color_count, 0 )+1
            #print( "Color_count", Color_count )
    
        Sample_runs_2_color_count[ sample_size ] = Color_count
        OUT.close()
    return( Sample_runs_2_color_count )

######################################################d##########################################

#Functions for manipulating the deck with repetitive draws

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


def change_Fetch_in_draw( sample_deck, draw,  Color_set_to_test_availability, available_colors = [] ):
    #looks into draw and counts the FETCH,
    print( draw )
    if type(draw) != Counter:
        draw = Counter(draw)
    print( draw )
    #proxy = input()
    Count_fetch = draw["FETCH"]
    if type(Color_set_to_test_availability) != set:
        print( Color_set_to_test_availability )
        Color_set_to_test_availability = set(Color_set_to_test_availability)
        print( Color_set_to_test_availability )

    #proxy = input()
    draw.pop("FETCH", None)#removes FETCH

    if not available_colors:
        available_colors = count_available_colors( draw )
    if type(available_colors) != set:
        print( available_colors, "ERROROOROROROOR" )
        available_colors = set(available_colors)
    #looks at available colors, defines missing colors
    print( type(Color_set_to_test_availability) )
    print( type(available_colors), "available_colors" )
    missing_colors = Color_set_to_test_availability-available_colors
    print( missing_colors, available_colors )

    #add the missing colors
    for color in list(missing_colors):
        #add_color_to_sample
        draw[ color ] = 1
        print( len(sample_deck))
        #remove from deck
        try:
            sample_deck.remove(color)
        except:
            print( sample_deck )
            print("OHH NO")
            print( color )
            sys.exit()
        print( len(sample_deck))
        #proxy = input()
        Count_fetch -= 1
        if Count_fetch == 0:
            return( sample_deck, draw )
        print( Count_fetch, "Counter_fetch")
        #proxy = input()

    #for fetches where all colors are available
    for i in range(Count_fetch):
        #get random color
        color = SamplingDraw.choice(list(Color_set_to_test_availability))
        #remove from deck
        sample_deck.remove(color)
        print( Count_fetch, "Counter_fetch")
        #proxy = input()
        #pass

    return( sample_deck, draw )

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


def add_all_color_land_to_land_base(Basic_color_land_base, lands_to_add):
    #Add lands to a land base that can tap for all colors. Identifier for this is defined in the function
    Basics  = sorted( [ str(ele) for ele in list(Basic_color_land_base.keys()) ] )

    #Defining all color land
    All_color_land_ID = "ALL"

    Current_Basic_to_fix_ID = 0
    for i in range(lands_to_add):
        Basic_color_land_base[All_color_land_ID] += 1

        Basic_to_fix = int( Basics[ Current_Basic_to_fix_ID ] )
        Basic_color_land_base[ Basic_to_fix ] -= 1
        if Current_Basic_to_fix_ID == len( Basics )-1:
            Current_Basic_to_fix_ID = 0
        else:
            Current_Basic_to_fix_ID += 1

    return Basic_color_land_base


def add_fetch_land_to_land_base(Basic_color_land_base, lands_to_add):
    #Add lands to a land base that can fetch other lands. Identifier for this is defined in the function
    Basics  = sorted( [ str(ele) for ele in list(Basic_color_land_base.keys()) ] )

    #Defining all color land
    Fetch_land_ID = "FETCH"

    Current_Basic_to_fix_ID = 0
    for i in range(lands_to_add):
        Basic_color_land_base[Fetch_land_ID] += 1

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


def add_colors_from_all_color_land( Fetch_land_count, colors_present, colors_possible = set(["1","2","3","4","5"]), deck=[]):
    #all_color_land_count fo r all color lands. FOr this version if the script only focus on Fetch lands
    for i in range(Fetch_land_count):
        #print( colors_present, "colors_present" )
        #proxy = input()
        if colors_possible == colors_present:
            return( colors_present )
        missing_colors = colors_possible - colors_present
        color = next(iter(missing_colors))

        #Adjust deck by removing lands
        print( len( deck), "Before")
        print( deck )
        deck.remove( color )
        print( len( deck), "After")
        #proxy = input()
        colors_present.add( color )
        #print( colors_present, "colors_present" )
        #proxy = input()
    print( deck )
    print( colors_present)
    return( deck, colors_present )

def count_available_colors(counter):
    #Counts available colors. Uses different decisions for different keys.
    available_colors = set()
    #All_present_checked = False
    Fetch_presentchecked = False
    for key in counter.keys():
        if key == "Other":
            continue
        #if key == "ALL" and not All_present_checked:
        #    All_color_land_count = counter["ALL"]
            #available_colors = add_colors_from_all_color_land( all_color_land_count = All_color_land_count, colors_present = available_colors, colors_possible = set(Color_set_to_test_availability))
        #    All_present_checked = True

        if key == "FETCH" and not Fetch_presentchecked:
            Fetch_land_count = counter["FETCH"]
            #available_colors = add_colors_from_all_color_land( all_color_land_count = All_color_land_count, colors_present = available_colors, colors_possible = set(Color_set_to_test_availability))
            Fetch_presentchecked = True

        elif counter[key] != 0:

            colors = str(key).split("_")

            for color in colors:
                available_colors.add(color)
    if Fetch_presentchecked:     #All_present_checked:
        pass
        #deck, available_colors = add_colors_from_all_color_land( Fetch_land_count = Fetch_land_count, colors_present = available_colors, colors_possible = set(Color_set_to_test_availability), deck = deck)

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
