#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);
library(geomtextpath);

#Script takes the data from python script 012
current_path = getwd();
setwd("../Python/012_Monte_Carlo_Simulation_Control_basics_lands_different_colored_decks");
data.df = read.table("012_Saved_run_for_plotting__2_colors.txt",sep = "\t", header = 1,
                     nrows = 1000);

#plotting the numbers
Simplot = ggplot( data.df, aes( x = Total_runs, y = Proportion_of_Starting_failure))+
  geom_line(aes(x= Total_runs, y=Proportion_failure_after_draws,color="pink2"))+
  geom_line()+
  scale_x_continuous( name = "Total simulations")+
  scale_y_continuous(limits = c(0,0.3), name = "Proportion of draws without all colors")+
  theme(legend.position = "none");
Simplot;
#Saving the plot

plot_name = paste("Chapter_7_2_1_simulation_plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = Simplot, 
       width =6, height =6, dpi = 300);
