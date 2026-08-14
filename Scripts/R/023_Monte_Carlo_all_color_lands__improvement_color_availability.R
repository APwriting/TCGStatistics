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
  data.df = data.df[which(data.df$Mulligan=="False"),];
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
result.df = results_all_colors[[1]];


#Averages and proportion of all colors in starting hand.

data.2color.df = data_frames_monte_carlos_all_color[[1]];
result.starting.2.df <- data.2color.df |>
  group_by(Trial_land_count) |>
  summarise(
    starting_ava = mean(turns_until_all_colors == 0)
  )
result.starting.2.df$color = 2;

data.3color.df = data_frames_monte_carlos_all_color[[2]];
result.starting.3.df <- data.3color.df |>
  group_by(Trial_land_count) |>
  summarise(
    starting_ava = mean(turns_until_all_colors == 0)
  )
result.starting.3.df$color = 3;

data.4color.df = data_frames_monte_carlos_all_color[[3]];
result.starting.4.df <- data.4color.df |>
  group_by(Trial_land_count) |>
  summarise(
    starting_ava = mean(turns_until_all_colors == 0)
  )
result.starting.4.df$color = 4;

data.5color.df = data_frames_monte_carlos_all_color[[4]];
result.starting.5.df <- data.5color.df |>
  group_by(Trial_land_count) |>
  summarise(
    starting_ava = mean(turns_until_all_colors == 0)
  )
result.starting.5.df$color = 5;

mean(diff(result.starting.2.df$starting_ava[1:10]*100));
mean(diff(result.starting.3.df$starting_ava[1:10]*100));
mean(diff(result.starting.3.df$starting_ava*100));
mean(diff(result.starting.4.df$starting_ava[1:10]*100));
mean(diff(result.starting.5.df$starting_ava[1:10]*100));

positions <- c(0, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35);

comparisons.df <- do.call(rbind, lapply(results_all_colors, function(df) {
  df[positions + 1, 1]
}))

comparisons.df <- do.call(rbind, lapply(results_all_colors, function(df) {
  df[positions + 1, c("Trial_land_count", "color", "mean_turns")]
}))

write.table(
  comparisons.df,
  "7_4_1_table_results_average_turns.txt",
  sep = "\t",
  row.names = FALSE,
  quote = FALSE,dec = ","
)














#Plotting
plot_list = list()
for (result.df in results_all_colors){
  print( result.df[0,]);
  Simplot = ggplot( result.df, aes( x = Trial_land_count, y = mean_turns))+
    geom_line(aes(color="pink2"))+
    scale_x_continuous( name = "Lands with all colors added to mana base.",
                        breaks = seq(0,35,by=5)
                        )+
    scale_y_continuous(limits = c(0, ceiling( max(result.df$mean_turns) )), name = "Average turns until all colors")+
    background_grid()+
    theme(legend.position = "none");
  Simplot;
  plot_list = append( plot_list, Simplot );
  
  
}

All_average_turn_plots = plot_grid(plotlist = plot_list,labels = c("2","3","4", "5"));
All_average_turn_plots;


color.3.starting.hand.plot = ggplot(result.starting.3.df, aes(x = Trial_land_count, y=starting_ava))+
  geom_line()+
  scale_x_continuous( name = "Lands with all colors added to mana base.",
                      breaks = seq(0,35,by=5)
  )+
  scale_y_continuous(name = "Average percentage of hands with all colors.")+
  background_grid()+
  theme(legend.position = "none");
color.3.starting.hand.plot;


#Saving the plot

plot_name = paste("Chapter_7_4_1_simulation_average_turns__adding_all_color_lands__plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = All_average_turn_plots, 
       width =10, height =10, dpi = 300);


plot_name = paste("Chapter_7_4_2__3_color_improvement_starting_colors__plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = color.3.starting.hand.plot, 
       width =6, height =6, dpi = 300);
