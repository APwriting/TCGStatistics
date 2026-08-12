#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);

#Own Libraries
library(AnaMTG);

#Setting path
current_directoy = getwd();
setwd("../../")


# Read the data
dual_lands_2color.df <- read.table(
  "Scripts/Python/016__analyse_influence_of_dual_lands/Results/016_analysis_results_2_colors_dual_analysis.txt",
  header = TRUE,
  sep = "\t"
)


dual_lands_3color.df <- read.table(
  "Scripts/Python/016__analyse_influence_of_dual_lands/Results/016_analysis_results_3_colors_dual_analysis.txt",
  header = TRUE,
  sep = "\t"
)


# Create dual_lands by adding columns 1_2 and 1_3
dual_lands_3color.df$dual_lands_combined <- dual_lands_3color.df$X1_2 + dual_lands_3color.df$X1_3



#Plotting





dual2_plot = ggplot(dual_lands_2color.df, aes(x = X1_2, y =  X2.1)) +
  geom_point() +
  labs(
    x = "Dual lands",
    y = "Probability to have all colors in starting hand"
  )
dual2_plot;

























