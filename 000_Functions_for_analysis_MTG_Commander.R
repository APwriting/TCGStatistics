#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);
library(devtools);

devtools::create("AnaMTG")



#Hypergeometric base functions
probability_exact <- function(x, draws, y, deck_size) {
  #Calculates exact hypergeometric values
  dhyper(x, y, deck_size - y, draws)
}
probability_at_least <- function(x, draws, y, deck_size) {
  #Calculate values for at least x successes from the hypergeometric function
  1 - phyper(x - 1, y, deck_size - y, draws)
}


##










