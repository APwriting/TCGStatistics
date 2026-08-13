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
dual_lands_3color.df$dual_lands_combined <- dual_lands_3color.df$X1_2 + dual_lands_3color.df$X1_3 +  dual_lands_3color.df$X2_3


#Stats

average_change_2_color <- mean(diff(dual_lands_2color.df$X2.1  ))
average_change_2_color;


average_change_2_color_first_10 <- mean(diff(dual_lands_2color.df$X2.1[1:10]  ))
average_change_2_color_first_10;

diffs_2_color = diff(dual_lands_2color.df$X2.1  );
diffs_2_color_perc = diffs_2_color[-1] / diffs_2_color[-length(diffs_2_color)];
diffs_2_color_perc;

dual_lands_3color.df

average_change_3_color <- mean(diff(dual_lands_3color.df$X3.1  ))
average_change_3_color;


average_change_3_color_first_10 <- mean(diff(dual_lands_3color.df$X3.1[1:10]  ))
average_change_3_color_first_10;

diffs_3_color = diff(dual_lands_3color.df$X3.1  );
diffs_3_color_perc = diffs_3_color[-1] / diffs_3_color[-length(diffs_3_color)];
diffs_3_color_perc;

#Plotting





dual2_plot = ggplot(dual_lands_2color.df, aes(x = X1_2, y =  X2.1)) +
  geom_line()+
  geom_point(color="brown2") +
  labs(
    x = "Dual lands replacing basics (40 lands)",
    y = "Probability to have all 2 colors\nin starting hand"
  )+
  #ggtitle("2 color deck improvement by adding dual lands:")+
  background_grid(major = "y", minor = "y");
dual2_plot;


dual3_plot = ggplot(dual_lands_3color.df, aes(x = dual_lands_combined, y =  X3.1)) +
  geom_line()+
  geom_point(color="brown2") +
  labs(
    x = "Dual lands replacing basics (40 lands)",
    y = "Probability to have all 3 colors\nin starting hand"
  )+
  #ggtitle("2 color deck improvement by adding dual lands:")+
  background_grid(major = "y", minor = "y");
dual3_plot;








###
#Saving the plots


plot_name = paste("Chapter_7_3_1__dual_land_increase_2_color__", Sys.Date()  ,".png")
ggsave(plot_name, plot = dual2_plot, 
       width = 6, height = 4, dpi = 300);

plot_name = paste("Chapter_7_3_2__dual_land_increase_3_color__", Sys.Date()  ,".png")
ggsave(plot_name, plot = dual3_plot, 
       width = 6, height = 4, dpi = 300);











