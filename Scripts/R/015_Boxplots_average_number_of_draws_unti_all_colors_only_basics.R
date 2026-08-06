#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);
library(geomtextpath);

#Script takes the data from python script 014
current_path = getwd();
setwd("../Python/014_draws_until_all_colors_present_only_basics");
data.df = read.table("014_Simulations_10000_until_all_colors__maximum_5_colors.txt",sep = "\t", header = 1,
                     
