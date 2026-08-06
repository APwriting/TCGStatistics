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
data.df = read.table("014_Simulations_10000_until_all_colors__maximum_5_colors.txt",sep = "\t", 
                     header = 1);

#Create box plots

Complete.plot = ggplot( data.df, aes(x = factor(Color_count), y = Turns))+
  geom_boxplot(fill = "#3a86d4", alpha = 0.7)+
  scale_x_discrete(name = "Number of colors")+
  stat_summary(fun = mean, geom = "point", shape = 20, size = 5, fill = "blue")+
  background_grid();
Complete.plot;

Zoomed.plot = ggplot( data.df, aes(x = factor(Color_count), y = Turns))+
  geom_boxplot(fill = "#3a86d4", alpha = 0.7)+
  scale_x_discrete(name = "Number of colors")+
  scale_y_continuous(limits = c(0,29), name = "Turns")+
  stat_summary(fun = mean, geom = "point", shape = 20, size = 5, fill = "blue")
  background_grid();
Zoomed.plot;

Both.plots = list( Complete.plot, Zoomed.plot);
Comb.plot = plot_grid(plotlist = Both.plots, ncol = 1);
Comb.plot
#Compare median and mean statistic
for (i in 1:5){
  color.mean = mean(  data.df$Turns[which(data.df$Color_count==i)] );
  print( color.mean);
  color.median = median(  data.df$Turns[which(data.df$Color_count==i)] );
  print( color.median);
  
}

#Plot saving
setwd(current_path);
plot_name = paste("Chapter_7_2_2_mv_commander_plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = Comb.plot, 
       width =8, height =10, dpi = 300);
  





                     
                     
                     
                     
                     
                     
                     