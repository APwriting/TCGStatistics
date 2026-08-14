#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);
library(geomtextpath);
library(dplyr);

#Script takes the data from python script 022
#Loading data
current_path = getwd();
setwd("../Python/022_analysis_turns_until_all_colors/All_color_land_simulation");#
files <- list.files(
  ".",
  pattern = "allcolor_lands__MC_simulation\\.txt$",
  full.names = TRUE
)


data_frames_monte_carlos_all_color = list();
for (file in files){

  data.df = read.table(file,sep = "\t", header = 1);
  data_frames_monte_carlos_all_color <- append(data_frames_monte_carlos_all_color, list(data.df));
}


setwd(current_path);
#Digesting_data
results_all_colors = list()
for (data.df in data_frames_monte_carlos_all_color){
  color = data.df$colors[1];#first get the color ident
  
  result.df <- data.df |>
    group_by(Trial_land_count) |>
    summarise(mean_turns = mean(turns_until_all_colors));
  result.df$color = color;
  
  results_all_colors = append(results_all_colors, list(result.df));
}


data.3color.df = data_frames_monte_carlos_all_color[[2]];
result.starting.df <- data.3color.df |>
  group_by(Trial_land_count) |>
  summarise(
    starting_ava = mean(turns_until_all_colors == 0)
  )
result.starting.df$color = 3;

#Plotting
plot_list = list()
for (result.df in results_all_colors){
  print( result.df[0,]);
  Simplot = ggplot( result.df, aes( x = Trial_land_count, y = mean_turns))+
    geom_line(aes(color="pink2"))+
    scale_x_continuous( name = "Lands with all colors added to mana base.",
                        breaks = seq(0,35,by=5)
                        )+
    scale_y_continuous(limits = c(0, round( max(result.df$mean_turns) )), name = "Average turns until all colors")+
    background_grid()+
    theme(legend.position = "none");
  Simplot;
  plot_list = append( plot_list, Simplot );
  
  
}

All_average_turn_plots = plot_grid(plotlist = plot_list,labels = c("2","3","4", "5"));
All_average_turn_plots;




#Saving the plot

plot_name = paste("Chapter_7_4_1_simulation_average_turns__adding_all_color_lands__plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = All_average_turn_plots, 
       width =10, height =10, dpi = 300);
