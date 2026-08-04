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
    #sys.exit()
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
        #print(Combination)
        #print(land_combinations)
        #print(Draws)
        Probability  = multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=land_combinations,   # category sizes
            n=Draws             # cards drawn
            ) 
        #sys.exit()
        Combination_probabilities[ hand_drawn_key ] = Probability

        Cumulative_basic_present[ Basic_lands_present[ hand_drawn_key ] ] = Cumulative_basic_present.get(Basic_lands_present[ hand_drawn_key ],0)+Probability

        if Basic_lands_present[ hand_drawn_key ] :
            #print("See")
            pass
        if 0:
            print( multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=land_combinations,   # category sizes
            n=Draws             # cards drawn
            ) )
    print( Cumulative_basic_present )
    After_sh_prob = dict()
    Combinatorics_after_SH = Get_combinations( Sample_Size = Adraws, at_least = 0)
    print( Combinatorics_after_SH )
   # sys.exit()
    print( Combinatorics_after_SH)
    Probability_to_fix_after_draws = dict()
    print(basic_keys)
   #sys.exit()
    for hand_drawn_key in basic_keys:
        previous_combination = hand_drawn_key.split("_")
        print( Basics, previous_combination )
        after_sh_lands = [ Basic_count[land+1]-int( previous_combination[land]) for land in range(len(Basics))]
        print( "Basics", Basics)
        print( hand_drawn_key )
        print( after_sh_lands )
        after_sh_lands.append( Decksize-Draws-sum(after_sh_lands) )#reduce by the draws.
        print("Test", after_sh_lands)
        #hand_drawn_key = "_".join([ str(i) for i in Combination])
        if not Basic_lands_present[ hand_drawn_key ]:
            print("Wait", hand_drawn_key, Combination_probabilities[ hand_drawn_key ])
            print("SCHLEIFE BEGIN")
            for Combination in Combinatorics_after_SH:

                
                print( id(Combination))
                leftover_hand = Adraws - sum(Combination)
                Combination.append(leftover_hand)#adds the amount of non lands
                print( Combination, after_sh_lands, Adraws )
                print( [ id(i) for i in [Combination, after_sh_lands, Adraws]] )
                #sys.exit()
                Probability  = multivariate_hypergeom.pmf(
                    x=Combination,      # drawn from each category
                    m=after_sh_lands,   # category sizes
                    n=Adraws             # cards drawn
                    ) 
                print( Probability)
                previous_probability = Combination_probabilities[ hand_drawn_key ]
                #Get the new land drawn amount
                new_total_lands = previous_combination[::]
                #new_total_lands.pop() #remove total non lands
                new_total_lands = [ int(new_total_lands[i])+int(Combination[i]) for i in range( len(new_total_lands ) ) ]
                print( new_total_lands, previous_combination, Combination, "new_total_lands, previous_combination, Combination"  )
                print( [ id(i) for i in [new_total_lands, previous_combination, Combination]], "new_total_lands, previous_combination, Combination"  )

                Is_now_all_types = Check_if_all_land_types(Previous_draw = [], New_draws = new_total_lands)
                print(Is_now_all_types)
                print("\n\n")
                Probability_to_fix_after_draws[Is_now_all_types] = Probability_to_fix_after_draws.get(Is_now_all_types,0) + previous_probability * Probability
                #sys.exit()
                #Add the combinations
                #Check_if_all_land_types(Previous_draw = [], New_draws = Combination)
            print("SCHLEIFE Ende")
    #Probability_to_fix_after_draws

#Need to simplifiy by making probability calculaiton into a function
#Then making the first and second combinatorics calculations summarized into their own functions.





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
        #print(i)
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
                
    for ele in List_of_Combinations:
        total = sum(ele)
        if total <= Sample_Size and total >= at_least:
            Combinatorics.append(ele)
    print(Combinatorics, "Finished counting combinations")

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