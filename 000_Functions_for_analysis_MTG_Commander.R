#/usr/bin/r

#Loading Libraries

#library(ggplot2);
#library(cowplot);
#theme_set(theme_cowplot());
#library(ggpubr);
#library(geomtextpath);
#library(devtools);

#remove.packages("AnaMTG");
#devtools::create("AnaMTG");
#file.copy("000_Functions_for_analysis_MTG_Commander.R","AnaMTG/R");
#setwd("C:/Users/falkn/Documents/Projects/Magic_Deck_building_Statistics/AnaMTG");
#devtools::document();
#devtools::install(".");

#' Exact hypergeometric probability
#'
#'
#' @param X, draws, y and deck size which is the population site
#' @return A probabiity
#' @export
probability_exact <- function(x, draws, y, deck_size) {
  #Calculates exact hypergeometric values
  dhyper(x, y, deck_size - y, draws)
}
#' @export
probability_at_least <- function(x, draws, y, deck_size) {
  #Calculate values for at least x successes from the hypergeometric function
  1 - phyper(x - 1, y, deck_size - y, draws)
}

#' hypergeometric variance
#'
#'
#' @param N population size, K is the sample size, n the number of accesses
#' @return Variance of a probability
#' @export
hypergeo_variance <- function(N, K, n) {
  #mean <- n * K / N

  variance <- n * (K / N) * (1 - K / N) * ((N - n) / (N - 1))
}


##
#Functions for hypergeometric data creation


#' Hypergeoemtric data gathering function. Exact probabilities
#'
#'
#' @param X, max number in deck, min number in deck, deck or population size, draws or sample size
#' @return A database of probabilities
#' @export
run_exact_land_base_test <- function(exactX, max_number_in_deck, min_number_in_deck = 1,
                                     deck_size = 99, draws = 7) {
  num = c()
  Probability_X = c()
  Variation = c()

  for (at_least_so_many in 1:exactX){


    for (number_in_deck in min_number_in_deck:max_number_in_deck) {
      prob_result <-
        probability_exact(
          x = at_least_so_many,
          draws = draws,
          y = number_in_deck,
          deck_size = deck_size
        )
      Probability_X = c(Probability_X, prob_result)
      Variation = c(Variation, as.character(at_least_so_many))
      num = c(num, number_in_deck)
    }

    #data.df[[paste0("col", at_least_so_many)]] = Probability_X
  }
  data.df = data.frame(N=num, P=Probability_X, V=Variation)

  return(data.df)
}


##
#Functions for hypergeometric data creation
#' Hypergeoemtric data gathering function. At least so many probabilities
#'
#'
#' @param X, max number in deck, min number in deck, deck or population size, draws or sample size
#' @return A database of probabilities
#' @export
run_Atleast_land_base_test <- function(At_least_x, max_number_in_deck, min_number_in_deck = 1,
                                       deck_size = 99, draws = 7) {
  num = c()
  Probability_X = c()
  Variation = c()

  for (at_least_so_many in 1:At_least_x){


    for (number_in_deck in min_number_in_deck:max_number_in_deck) {
      prob_result <-
        probability_at_least(
          x = at_least_so_many,
          draws = draws,
          y = number_in_deck,
          deck_size = deck_size
        )
      Probability_X = c(Probability_X, prob_result)
      Variation = c(Variation, as.character(at_least_so_many))
      num = c(num, number_in_deck)
    }

    #data.df[[paste0("col", at_least_so_many)]] = Probability_X
  }
  data.df = data.frame(N=num, P=Probability_X, V=Variation)

  return(data.df)
}







#Functions for analyzing specific magic data


#' Functions to return mana value distribution from individual values
#'
#'
#' @param vector of mana values
#' @return A database of mana value counts
#' @export
return_mv_count <- function( mana_values ){
  return( as.data.frame( table(mana_values) ) )
}




##Function for plotting data
#' FFunctions for plotting mana curves
#'
#'
#' @param data base, title, fill, color, and y limites
#' @return A mana value plot
#' @export
Create_Mana_curve_plot <- function( data.df, title, fill = "darkseagreen1", colour = "darkgreen",
                                    ylimitlow = 0, ylimhigh = 35){
  
  Bar_plot = ggplot(data.df, aes(x=mana_values,y=Freq))+
    geom_col(fill = fill, colour = colour)+
    ggtitle(title)+
    scale_x_continuous( name = "Mana values", labels  = 1:max(mv.df$mana_values),
                        breaks = 1:max(mv.df$mana_values   ))+
    scale_y_continuous(limits = c(ylimitlow,ylimhigh), name = "Count");
  return(Bar_plot)
}



#Scryfall tools
#' Function loads the JSON card data from Scryfall
#'
#'
#' @param scryfall ID
#' @return a list derived from the JSON given by the Scryfall API that represents a single card
#' @export
Load_ScryfallCard <- function( id ){
  APIurl <- paste0("https://api.scryfall.com/cards/", id)
  APIurl;

  commander.card <- jsonlite::fromJSON(paste0("https://api.scryfall.com/cards/", id))
  return(commander.card);
}

#' Function tom combine to scryfall images, for example two commander pairs for plotting
#'
#'
#' @param scryfall links
#' @return a combined picture
#' @export
combine_images <- function(img1_url, img2_url, output_file = "combined.png") {
  
  # Read images from URLs
  img1 <- magick::image_read(img1_url)
  img2 <- magick::image_read(img2_url)
  
  # Resize to same height
  height <- min(image_info(img1)$height, image_info(img2)$height)
  
  img1 <- magick::image_resize(img1, paste0("x", height))
  img2 <- magick::image_resize(img2, paste0("x", height))
  
  # Append horizontally
  combined <- magick::image_append(c(img1, img2))
  
  # Save
  magick::image_write(combined, output_file)
  
  return(output_file)
}



##Load deck data

#' remove Maybeboard and Sideboard from loaded deck.df
#'
#'
#' @param data base with deck data
#' @return same data abse without Maybeboard and Sideboard
#' @export
remove_maybe_and_sideboard <-function(Commander.deck.df){
  Commander.deck.df = Commander.deck.df[ which(Commander.deck.df$Category!="Maybeboard" & Commander.deck.df$Category!="Sideboard"),]; 
  return(Commander.deck.df)
}

#' Function reads allarchidekt export csv file in a folder
#'
#'
#' @param reads csv data from archidekt, considers the quotation marks it exports with. 
#' @return Commander data base, note that the header may not be the right one and needs to be edited in file. There is a python script for this.
#' @export
read_archidekt_export <-function(path){
  
  
  decks = list();
  deck_list_paths = list.files( path = path,pattern = "\\.csv$",full.names = TRUE);
  for (deck_path in deck_list_paths){
    Commander.deck.df <- read.csv(file   = deck_path);
    decks = append(decks, Commander.deck.df);
  }
  
  return(decks)
}




