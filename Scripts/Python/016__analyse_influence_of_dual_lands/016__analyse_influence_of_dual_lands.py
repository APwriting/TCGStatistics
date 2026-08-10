#/usr/bin/python

#Script for hypergeometric calculations 

from scipy.stats import multivariate_hypergeom
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


def main():

    #Define Categories, number of basic land types

    Basic_count = define_basic_land_count( colors ) #Define basics for later on

    #Generate possible dual land categories from the colors
    Basic_names = list(Basic_count.keys())

    Duals = create_dual_land_categories( Basic_names )

    to_write_list = list()  #Easier to save the lines in the for loop and write everything clean later.

    Different_probabilities_numbers = [ i for i in range(colors+1) ]

    #Go through each possible number of dual_lands
    for Dual_trial in range( Lands+1 ):
        Updated_duals = distribute_land_count(counter = Duals, land_count = Dual_trial)


        Updated_land_base = add_duals_to_land_base(Basic_color_land_base = Basic_count.copy(), duals_to_add = Updated_duals)
        Updated_land_base = Add_other_category(counter = Updated_land_base)
        print( Updated_land_base)
        Updated_land_base_copy = Updated_land_base.copy()


        #Start tinkering
        Updated_land_base_keys = sorted([str(ele) for ele in list( Updated_land_base.keys() )])
        print( "Updated_land_base_keys", "Updated_land_base_keys", Updated_land_base_keys )


        Dual_Combinatorics = Get_combinations_Updated(Sample_Size = Draws, Categories = Updated_land_base, at_least = 0 )

        Ordered_keys = list(Dual_Combinatorics[0].keys())
        Dual_Combinatorics = convert_list_counter_to_combinatorics( Dual_Combinatorics, Ordered_keys )


        Dual_Deck_combinations = convert_list_counter_to_combinatorics( [Updated_land_base], Ordered_keys )[0]
        Combination_probabilities_dual = Combinatorics_Probabilities_General( Dual_Combinatorics, Dual_Deck_combinations, previous_draw = [] )
        size_percentages_sum = dict()
        for combination in sorted( list(Combination_probabilities_dual.keys())):

            Combination_counter = Convert_combination_to_counter( combination = combination, keys= Ordered_keys )
            #Combination_counter = remove_zeros(Combination_counter)
            comb_available_colors = count_available_colors(Combination_counter)
            #print("comb_available_colors",comb_available_colors)

            size_available_colors = len( comb_available_colors )
            probability = Combination_probabilities_dual[ combination ]
            size_percentages_sum[ size_available_colors ] = size_percentages_sum.get( size_available_colors,0 )+probability
            #print( "\t".join( [c] ) )
            #proxy = input()
        #percentages_string = "\t".join( [ str(size_percentages_sum[ key ]) for key in list( size_percentages_sum.keys() )  ] )
        print( Updated_land_base , "TETSTTTT UPDATED LAND BASE")
        #sys.exit()
        print( Updated_land_base)
        #key_counter = counter_to_string(Updated_land_base)
        
        key_counter = list()
        checking_colors = [ str(i) for i in range(colors+1)]
        for key in Updated_land_base_keys:
            if key in checking_colors:
                key = int(key)
            #print( key )
            #key_counter.append( key )
            key_counter.append( str( Updated_land_base[key] ) )
            #print( key_counter, key, "key_counter")
            #proxy = input()
        for key in Different_probabilities_numbers:
            key_counter.append( str(  size_percentages_sum.get( key, 0)  ) )
        key_counter = "\t".join(key_counter)
        #prepare header
        Header_list = Updated_land_base_keys[:]
       # for ele in sorted( [str(ele) for ele in list(size_percentages_sum.keys())] ):
       #     Header_list.append( ele )
        for ele in Different_probabilities_numbers:
            Header_list.append( str(ele) )
        Header = "\t".join( Header_list )

        to_write_list.append( "\t".join( [ key_counter ] ) )

###     ####
        Available_colors = count_available_colors(Updated_land_base)

    with open( "016_analysis_results_{}_colors_dual_analysis.txt".format( colors ), "w" ) as OUT:
        print( Header, file = OUT )
        for line in to_write_list:
            print( line, file = OUT )







         
def counter_to_string(counter):
    return "_".join(
        f"{key}_{counter[key]}"
        for key in counter
    )


def remove_zeros(counter):
    return Counter({
        key: value
        for key, value in counter.items()
        if value != 0
    })

def convert_list_counter_to_combinatorics( Counter_list, order = [] ):
    if not order:
        sorted(list(Counter_list[0].keys()))

    comb_list = list()
    for ele in Counter_list:
        #print( ele)
        combinations = [ ele[key] for key in order]
        comb_list.append( combinations )
    return( comb_list )


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

def Convert_combination_to_counter( combination, keys ):

    if type(combination)==str:
        combination = combination.split("_")
    Counter_object = Counter(keys)
    for pos in range( len(keys)):

        key = keys[pos]

        Counter_object[key] = int(combination[pos])

    return(Counter_object)

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

def create_dual_land_categories( basics ):

    duals = []
    for i in range( len( basics ) ):
        for j in range(i+1,len(basics)):
            dual_land = "{}_{}".format(basics[i],basics[j])

            duals.append( dual_land )
    return( Counter(duals) )

def Add_other_category(counter):
    other_count = Decksize - sum(
        count for key, count in counter.items()
        if key != "Other"
    )

    counter["Other"] = other_count

    return counter

def distribute_land_count(counter, land_count):
    keys = sorted(counter.keys())
    
    base_count = land_count // len(keys)
    remainder = land_count % len(keys)

    for i, key in enumerate(keys):
        counter[key] = base_count
        
        if i < remainder:
            counter[key] += 1

    return counter

#COMBINATORICS AND ANALYSIS FUNCTION

def Combinatorics_Probabilities_General( Combinatorics, Card_count, Sample_Size = 7 , previous_draw = [] ):
    #first get the basic land combinations with all non lands
    #global Decksize
    Deck_combinations = Card_count
    #print( Deck_combinations )
    #proxy = input()

    #Define deictionary to give back later
    basic_keys = list()
    Combination_probabilities = dict()
    
    for ele in Combinatorics:
        Combination = ele[:]    #making sure that this is its own object
        #print()
        #print( "Testing Combination:", Combination )

        #Create Key to identify each pair
        hand_drawn_key = "_".join([ str(i) for i in Combination])
        basic_keys.append(hand_drawn_key)
        #Create a check whether all colors are represented in combinatorics sample

        Probability  = multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=Deck_combinations,   # category sizes
            n=Sample_Size             # cards drawn
            ) 

        Combination_probabilities[ hand_drawn_key ] = Probability


    return( Combination_probabilities )


def Check_if_all_land_types(Previous_draw = [], New_draws = []):
    if Previous_draw:
        List_to_check = [ int(Previous_draw[i])+int(New_draws[i]) for i in range(colors)]
       #print(List_to_check)
    else:
        List_to_check= [ New_draws[i] for i in range(colors)]
        #print(List_to_check)

    return( all( [basic_type_count >= 1 for basic_type_count in List_to_check] ) )


def fill_in_space( list_of_lists, max_range, pos):
    #Function to create the combination rows from the combinations matrix one at a time.
    max_range +=1 #Adjusting limitation of range function for sample
    temp_list = list()
    for ele in list_of_lists:
        for i in range(max_range):
            temp_unit = ele[:]
            temp_unit[pos] = i
            temp_list.append(temp_unit)
    return(temp_list)


#ef Add_categories( list_of_lists, max_range, pos):

def Get_combinations_Updated(Sample_Size, Categories, at_least = 0 ):
    
    Combinatorics = list()

    Category_keys = list(Categories.keys())

    if type(Categories) == Counter:
        #print(Categories)
        Placement = len( Category_keys )
    else:
        Placement = Categories


    Combinatorics_list = [ 0 for i in range(Placement)]

    print( "PLACEMENT", Placement)

    List_of_Combinations = list()
    #for i in Categories:
    #    print( i )
    #    print( "Reality", List_of_Combinations)
    
    for i in range(Placement):
     #   print( i )
     #   print( "Reality", List_of_Combinations)

        if not List_of_Combinations:
            temp_list = [Combinatorics_list[::]]
        else:
            temp_list = List_of_Combinations[::]
     #   print( temp_list, Sample_Size )
        new_temp = fill_in_space( list_of_lists = temp_list, max_range = Sample_Size, pos = i)

        List_of_Combinations = new_temp[::]
    #Make the combinations into a counter itself
    filtered_counters = list()
    for ele in List_of_Combinations:
        #print( ele )
        Empty_counter = Counter(Category_keys)
        Can_be_used = True
        sum = 0
        for i in range( len( Category_keys ) ):
            Empty_counter[Category_keys[i]] = ele[i]
            if Empty_counter[Category_keys[i]] > Categories[Category_keys[i]]:
                Can_be_used = False
            sum +=ele[i]
        if Can_be_used and sum==Sample_Size and sum>=at_least:
            filtered_counters.append( Empty_counter )

    return(filtered_counters)




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

