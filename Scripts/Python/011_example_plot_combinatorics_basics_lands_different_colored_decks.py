#/usr/bin/python

#Script for hypergeometric calculations 

from scipy.stats import hypergeom
from scipy.stats import multivariate_hypergeom


import sys


def main():
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
    #Number of lands
    global Lands
    Lands = 40
    #Population/Deck
    global Decksize 
    Decksize = 99

    #Define Categories, number of basic land types

    Basic_count = define_basic_land_count( colors )
    print(Basic_count)
    Combinatorics = Get_combinations( Sample_Size = Draws, at_least = Land_cutoff)
    sys.exit()
    Basics = [ land for land in sorted(list(Basic_count.keys()))]
    land_combinations = [ Basic_count[land] for land in Basics]
    land_combinations.append( Decksize-Lands )
    #print(land_combinations)
    Basic_lands_present = dict()
    basic_keys = list()
    Combination_probabilities = dict()
    Cumulative_basic_present = dict()
    for Combination in Combinatorics:

        leftover_hand = Draws - sum(Combination) #adds the amount of non lands
        hand_drawn_key = "_".join([ str(i) for i in Combination])
        basic_keys.append(hand_drawn_key)

        Combination.append(leftover_hand)#adds the amount of non lands

        Basic_lands_present[ hand_drawn_key ] = Check_if_all_land_types(Previous_draw = [], New_draws = Combination)
        print(Combination)
        print(land_combinations)
        print(Draws)
        Probability  = multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=land_combinations,   # category sizes
            n=Draws             # cards drawn
            ) 
        sys.exit()
        Combination_probabilities[ hand_drawn_key ] = Probability

        Cumulative_basic_present[ Basic_lands_present[ hand_drawn_key ] ] = Cumulative_basic_present.get(Basic_lands_present[ hand_drawn_key ],0)+Probability

        if Basic_lands_present[ hand_drawn_key ] :
            print("See")
        if 0:
            print( multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=land_combinations,   # category sizes
            n=Draws             # cards drawn
            ) )
    print( Cumulative_basic_present )



def Check_if_all_land_types(Previous_draw = [], New_draws = []):
    if Previous_draw:
        List_to_check = [ Previous_draw[i]+New_draws[i] for i in range(colors)]
       #print(List_to_check)
    else:
        List_to_check= [ New_draws[i] for i in range(colors)]
        #print(List_to_check)

    return( all( [basic_type_count >= 1 for basic_type_count in List_to_check] ) )


def fill_in_space( list_of_lists, max_range, pos):
    #print("ENTER")
    #print(list_of_lists)
    #print(id(list_of_lists))
    temp_list = list()
    for ele in list_of_lists:
        for i in range(max_range):
            temp_unit = ele[:]
            temp_unit[pos] = i
            temp_list.append(temp_unit)
    return(temp_list)

def Get_combinations(Sample_Size, at_least = 0, ):
    Combinatorics = list()
    Combinatorics_list = [ 0 for i in range(colors)]
    print( "Combinatorics_list", Combinatorics_list )
        #for j in range(Sample_Size):
    List_of_Combinations = list()
    for i in range(colors):
        print(i)
        print( "Reality", List_of_Combinations)
        if not List_of_Combinations:
            temp_list = [Combinatorics_list[::]]
        else:
            temp_list = List_of_Combinations[::]
        #print("Temp",temp_list)
        temp_list_list = list()
        new_temp = fill_in_space( list_of_lists = temp_list, max_range = Sample_Size, pos = i)
        #print("new_temp",new_temp)
        List_of_Combinations = new_temp[::]
        print( "Reality2", List_of_Combinations)
                

        if 0:
            for j in range(Sample_Size):
                if List_of_Combinations:
                    for ele in List_of_Combinations:
                        ele.append(j)
                        temp_list.append( ele )
                        print(temp_list)
                    
                else:
                    print("J",j)
                    temp_list.append( [j] )
        #List_of_Combinations = temp_list[:]
        
    if 0:
        for i in range(Sample_Size):
            for j in range(Sample_Size):
                for k in range(Sample_Size):
                    total = i+j+k
                    if total <= Sample_Size and total >= at_least:
                        Combinatorics.append([i,j,k])
                        #print(Combinatorics[-1])
    return(Combinatorics)

def define_basic_land_count( colors ):
    #defines the basic land count for the given amount of colors without any extra calculations like duals or pips.
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