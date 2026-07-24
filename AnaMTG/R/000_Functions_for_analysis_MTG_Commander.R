#/usr/bin/r

#Loading Libraries

#library(ggplot2);
#library(cowplot);
#theme_set(theme_cowplot());
#library(ggpubr);
#library(geomtextpath);
#library(devtools);

#devtools::create("AnaMTG")
#setwd("C:/Users/falkn/Documents/Projects/Magic_Deck_building_Statistics/AnaMTG");
#devtools::document();

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


##










