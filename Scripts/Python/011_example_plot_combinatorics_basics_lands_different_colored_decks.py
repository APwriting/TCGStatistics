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
    Basic_lands_present, Combination_probabilities = Combinatorics_Probabilities_Basics( Combinatorics, Basic_count, previous_draw = [] )
    print(Basic_lands_present)
    
    Probability_results =  Add_up_combinations( Basic_lands_present, Combination_probabilities  )
    
    
    #print(land_combinations)

    #print( Cumulative_basic_present )
    #After_sh_prob = dict()
    #Get the combinatoric for the draws until turn 5, no extra draws
    Combinatorics_after_SH = Get_combinations( Sample_Size = Adraws, at_least = 0 )[::]
    print( "\n\n\n\n\n\nCombinatorics_after_SH#############", Combinatorics_after_SH )
    #sys.exit()
    starting_hand_combinations = list([keys for keys in Combination_probabilities.keys()])
    print( "starting_hand_combinations", starting_hand_combinations )
    #proxy = input()
    Probability_results_after_draw = dict()
    Truth_keys = list(Probability_results.keys())
    print( "Truth_keys", Truth_keys )
    #proxy = input()
    Counter = 0
    # After the draw probability to get basic lands yes or no
    Draw_into_land_colors_probability = dict()


    for hand_drawn_key in starting_hand_combinations:
        Counter+=1
        #print("Counter",Counter, hand_drawn_key, "hand_drawn_key")
        #proxy = input()

        if not Basic_lands_present[ hand_drawn_key ]:   #Checks wheter the first draw had all basic lands
            #print( hand_drawn_key )
            #proxy = input()
            #print( hand_drawn_key, Combination_probabilities[ hand_drawn_key ], Basic_lands_present[ hand_drawn_key ] )
            #for Combinatorics in Combinatorics_after_SH:
            #proxy = input()
            #print(Combinatorics,"FFFFFFFFFFFFFFFFFFFF",Combinatorics_after_SH)
            #print("\n\n")
            #proxy = input()
            #print(Basic_count, "Basic_count", hand_drawn_key)
            #proxy = input()


            #Define probabilities
            Combinations_to_use = Combinatorics_after_SH[::][:]
            #print("This mistake: Combinations_to_use", Combinations_to_use)
            #proxy = input()

            #Calculate the Probabilites for draws, after adjusting for cards already drawn.
            #After double checking some spot check, these calculation seem to be correct.
            Adjusted_Basic_lands_present, Adjusted_Combination_probabilities = Combinatorics_Probabilities_Basics( Combinations_to_use, Basic_count, Sample_Size = Adraws, previous_draw = hand_drawn_key.split("_") )
            #print( hand_drawn_key, "Adjusted_Basic_lands_present, Adjusted_Combination_probabilities",Adjusted_Basic_lands_present, Adjusted_Combination_probabilities)
            #proxy = input()
            #Adjusted_Probability_results =  Add_up_combinations( Adjusted_Basic_lands_present, Adjusted_Combination_probabilities  )
            #    sys.exit()
            #print( "Adjusted_Probability_results", Adjusted_Probability_results)
            #proxy = input()
            Draw_into_land_colors_probability[ hand_drawn_key ] = ( Adjusted_Basic_lands_present, Adjusted_Combination_probabilities  )
            #print( Draw_into_land_colors_probability, "Draw_into_land_colors_probability" )
            #proxy = input()
        else:
            pass
            Draw_into_land_colors_probability[hand_drawn_key] = False#Simplifying later calls.
            #print("Is true: ", hand_drawn_key, "hand_drawn_key")
            #proxy = input()
    print("Now starting testerf or all value", hand_drawn_key, "hand_drawn_key")
    #proxy = input()
    Probability_sum_after_missed_colors = 0
    for hand_drawn_key in starting_hand_combinations:
        Probabiliy_of_drawing_into_all_basics_after_missed_in_hand = 0
        if Draw_into_land_colors_probability[hand_drawn_key]:
            print( Draw_into_land_colors_probability[ hand_drawn_key ]  )
            Adjusted_Basic_lands_present, Adjusted_Combination_probabilities =  Draw_into_land_colors_probability[ hand_drawn_key ] 
            secondary_keys = list( Adjusted_Basic_lands_present.keys() )
            print(secondary_keys)
            

            for sec_key in secondary_keys:
                print( secondary_keys )
                print( Adjusted_Basic_lands_present )
                #proxy = input()
                All_basics_present_after_draw = Adjusted_Basic_lands_present[sec_key]
                if All_basics_present_after_draw:
                    print( "All_basics_present_after_draw",All_basics_present_after_draw )
                    Probability_of_draws = Adjusted_Combination_probabilities[sec_key]
                    print(Probability_of_draws, "Probability_of_draws")
                    Probability_of_initial_hand = Combination_probabilities[hand_drawn_key]
                    print(Probability_of_initial_hand, "Probability_of_initial_hand")
                    Probability_factor = Probability_of_initial_hand*Probability_of_draws
                    Probabiliy_of_drawing_into_all_basics_after_missed_in_hand +=Probability_factor
                    print( "Probabiliy_of_drawing_into_all_basics_after_missed_in_hand", Probabiliy_of_drawing_into_all_basics_after_missed_in_hand)
                    
                    #print( "Combination_probabilities[hand_drawn_key]",Combination_probabilities[hand_drawn_key])
            Probability_sum_after_missed_colors += Probabiliy_of_drawing_into_all_basics_after_missed_in_hand
                    #proxy = input()
            print("Probability_sum_after_missed_colors", hand_drawn_key, Probability_sum_after_missed_colors )
            #proxy = input()
            print( "Probabiliy_of_drawing_into_all_basics_after_missed_in_hand", Probabiliy_of_drawing_into_all_basics_after_missed_in_hand)
            #proxy = input()
            #print( hand_drawn_key, Draw_into_land_colors_probability[ hand_drawn_key ], id(Draw_into_land_colors_probability[ hand_drawn_key ]), "Draw_into_land_colors_probability" ) 
            #print(  Combination_probabilities[hand_drawn_key], "Combination_probabilities")
            #Probability_sum_after_missed_colors += ( Draw_into_land_colors_probability[ hand_drawn_key ][True] * Combination_probabilities[hand_drawn_key])
            #print( Probability_sum_after_missed_colors, "Probability_sum_after_missed_colors")
            #proxy = input()
    print( "Results:")
    print("\n\nProbability_results initial draw True",Probability_results[True])
    print("\n\nProbability_results initial draw False",Probability_results.get(False,0))
    print("\n\nProbability_results adjustment after first 5 turns", Probability_sum_after_missed_colors )
    print( "Percentage of hands with not thing", Probability_results.get(False,0), "and how many of those this work out", Probability_sum_after_missed_colors)
    return(1)
    sys.exit()


#Need to simplifiy by making probability calculaiton into a function
#Then making the first and second combinatorics calculations summarized into their own functions.


def Add_up_combinations( Basic_lands_present, Combination_probabilities  ):
    #Function for adding the single probabilites of each key pair from Combinatorics_Probabilities_Basics
    Cumulative_basic_present = dict()
    combination_keys = list(Basic_lands_present.keys())
    for hand_drawn_key in combination_keys:
        Probability = Combination_probabilities[ hand_drawn_key ]
        Cumulative_basic_present[ Basic_lands_present[ hand_drawn_key ] ] = Cumulative_basic_present.get(Basic_lands_present[ hand_drawn_key ],0)+Probability
    return( Cumulative_basic_present )


    #Basic_count = define_basic_land_count( colors )
def Combinatorics_Probabilities_Basics( Combinatorics, Basic_count, Sample_Size = 7 , previous_draw = [] ):
    #first get the basic land combinations with all non lands
    #global Decksize


    land_combinations = return_basicland_combinations( Basic_count, Population = Decksize, Land_count = Lands, previous_draw = previous_draw )
    if previous_draw:
        print("land_combinations", land_combinations, Combinatorics, Basic_count)
        #proxy = input()
    #Define deictionary to give back later
    Basic_lands_present = dict()
    basic_keys = list()
    Combination_probabilities = dict()
    
    for ele in Combinatorics:
        Combination = ele[:]    #making sure that this is its own object
        #print()
        leftover_sample = Sample_Size - sum(Combination) #adds the amount of non lands
        Combination.append(leftover_sample)#adds the amount of non lands (non-defined category) to sample
        if previous_draw:
            print("Combination", Combination )
            #proxy = input()
        #Create Key to identify each pair
        hand_drawn_key = "_".join([ str(i) for i in Combination])
        basic_keys.append(hand_drawn_key)
        #Create a check whether all colors are represented in combinatorics sample
        Basic_lands_present[ hand_drawn_key ] = Check_if_all_land_types(Previous_draw = previous_draw, New_draws = Combination)


            #print( "previous_draw",previous_draw, land_combinations, Basic_lands_present[ hand_drawn_key ], hand_drawn_key )
            #sys.exit()
        print(Combination)
        print(land_combinations)
        print(Sample_Size)
        if previous_draw:
            print("Testing_probability now:" )
            #proxy = input()
        Probability  = multivariate_hypergeom.pmf(
            x=Combination,      # drawn from each category
            m=land_combinations,   # category sizes
            n=Sample_Size             # cards drawn
            ) 
        if previous_draw:
            print("Testing_probability now:", Probability )
            #proxy = input()

        #sys.exit()
        Combination_probabilities[ hand_drawn_key ] = Probability


        #print(hand_drawn_key, Basic_lands_present[ hand_drawn_key ], Combination_probabilities[ hand_drawn_key ] )

    return( Basic_lands_present, Combination_probabilities )


def return_basicland_combinations( Basic_count, Population = Decksize , Land_count = Lands, previous_draw = [] ):
    #returns the combination distribution of basic lands, given how many colors are there.
    #Adds all the non lands at the end
    #Adjusts for previous draw combinations
    
    if previous_draw:
        if "_".join(previous_draw) == "0_3_4":
            print( "Basic_count ", Basic_count )
            #sys.exit()
    Basics = [ category for category in sorted(list(Basic_count.keys()))]
   #print( Basics, Basic_count )
    #sys.exit()
    if previous_draw:
        if "_".join(previous_draw) == "0_3_4":
            print( "Basics ", Basics )
            #sys.exit()
    if previous_draw:
        if "_".join(previous_draw) == "0_3_4":
            #non_lands_previous_draw = int(previous_draw.pop())
            #lands_in_previous_draw = sum([int(ele) for ele in previous_draw ])
            #print( "non_lands_previous_draw ", non_lands_previous_draw, lands_in_previous_draw )
            #sys.exit("What")
            pass
        print(previous_draw)
        if "_".join(previous_draw) == "0_3_4":
            pass
            #non_lands_previous_draw = int(previous_draw.pop())
            #sys.exit("This")
        non_lands_previous_draw = int(previous_draw.pop())

        lands_in_previous_draw = sum([int(ele) for ele in previous_draw ])
        #print( "previous_draw",previous_draw,non_lands_previous_draw, lands_in_previous_draw  )

        Land_count -= lands_in_previous_draw #redunant but good for understanding
        Population -= (non_lands_previous_draw + lands_in_previous_draw)
        
        land_combinations = [ Basic_count[land+1]-int( previous_draw[land]) for land in range(len(Basics))]#dictionary Basiccount starts with 1
        #print( Basic_count, land_combinations)
        
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
    #print("ENTER")
    #print(list_of_lists)
    #print(id(list_of_lists))
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
        print("Temp",temp_list)
        temp_list_list = list()
        #Extend current list
        new_temp = fill_in_space( list_of_lists = temp_list, max_range = Sample_Size, pos = i)
        print("new_temp",new_temp)
        #proxy = input()
        List_of_Combinations = new_temp[::]
        print( "Reality2", List_of_Combinations)
        #proxy = input()
                
    for ele in List_of_Combinations:
        total = sum(ele)
        if total <= Sample_Size and total >= at_least:
            Combinatorics.append(ele)
    print(Combinatorics, "Finished counting combinations")

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