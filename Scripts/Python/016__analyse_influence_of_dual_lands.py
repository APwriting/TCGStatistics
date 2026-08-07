#/usr/bin/python

#Script for hypergeometric calculations 

from scipy.stats import hypergeom
from scipy.stats import multivariate_hypergeom


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

    Basic_count = define_basic_land_count( colors )
    print(Basic_count)



    #Combinations for starting hand
    Combinatorics = Get_combinations( Sample_Size = Draws, at_least = Land_cutoff)
    #sys.exit()

    #Results for starting hand
    All_colors_present, Combination_probabilities = Combinatorics_Probabilities_Basics( Combinatorics, Basic_count, previous_draw = [] )


    print(All_colors_present, Combination_probabilities)






def Combinatorics_Probabilities_Basics( Combinatorics, Basic_count, Sample_Size = 7 , previous_draw = [] ):
    #first get the basic land combinations with all non lands
    #global Decksize
    land_combinations = return_land_combinations( Basic_count, Population = Decksize, Land_count = Lands, previous_draw = previous_draw )

    #Define deictionary to give back later
    Basic_lands_present = dict()
    basic_keys = list()
    Combination_probabilities = dict()
    
    for ele in Combinatorics:
        Combination = ele[:]    #making sure that this is its own object
        #print()
        leftover_sample = Sample_Size - sum(Combination) #adds the amount of non lands
        Combination.append(leftover_sample)#adds the amount of non lands (non-defined category) to sample

        #Create Key to identify each pair
        hand_drawn_key = "_".join([ str(i) for i in Combination])
        basic_keys.append(hand_drawn_key)
        #Create a check whether all colors are represented in combinatorics sample
        Basic_lands_present[ hand_drawn_key ] = Check_if_all_land_types(Previous_draw = previous_draw, New_draws = Combination)

        Probability  = multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=land_combinations,   # category sizes
            n=Sample_Size             # cards drawn
            ) 

        Combination_probabilities[ hand_drawn_key ] = Probability


    return( Basic_lands_present, Combination_probabilities )




def return_land_combinations( Basic_count, Population = Decksize , Land_count = Lands, previous_draw = [] ):
    #returns the combination distribution of basic lands, given how many colors are there.
    #Adds all the non lands at the end
    #Adjusts for previous draw combinations
    
    if previous_draw:
        if "_".join(previous_draw) == "0_3_4":
            print( "Basic_count ", Basic_count )

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
    
    #print(land_combinations )
    return( land_combinations )



def Check_if_all_land_types(Previous_draw = [], New_draws = []):
    if Previous_draw:
        List_to_check = [ int(Previous_draw[i])+int(New_draws[i]) for i in range(colors)]
       #print(List_to_check)
    else:
        List_to_check= [ New_draws[i] for i in range(colors)]
        #print(List_to_check)

    return( all( [basic_type_count >= 1 for basic_type_count in List_to_check] ) )


def fill_in_space( list_of_lists, max_range, pos):

    max_range +=1 #Adjusting limitation of range function for sample
    temp_list = list()
    for ele in list_of_lists:
        for i in range(max_range):
            temp_unit = ele[:]
            temp_unit[pos] = i
            temp_list.append(temp_unit)
    return(temp_list)

def Get_combinations(Sample_Size, at_least = 0, ):
    #For the number of colors defined, a combination of how many of each possible color is defined 
    #for a given sample size
    #at_least defines how many of each category have to be filled at least to account for mulligans
    
    Combinatorics = list()
    Combinatorics_list = [ 0 for i in range(colors)]

    List_of_Combinations = list()
    for i in range(colors):

        print( "Reality", List_of_Combinations)

        if not List_of_Combinations:
            temp_list = [Combinatorics_list[::]]
        else:
            temp_list = List_of_Combinations[::]

        new_temp = fill_in_space( list_of_lists = temp_list, max_range = Sample_Size, pos = i)

        List_of_Combinations = new_temp[::]

                
    for ele in List_of_Combinations:
        total = sum(ele)
        if total <= Sample_Size and total >= at_least:
            Combinatorics.append(ele)

    return(Combinatorics)

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

