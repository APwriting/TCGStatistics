#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);

#Own Libraries
library(AnaMTG);


#Create functions

Create_Bar_plot <- function( data.df, title, fill = "darkseagreen1", colour = "darkgreen" ){
  Bar_plot = ggplot(data.df, aes(x=Mana_value, y=Count))+
    geom_col(fill = fill, colour = colour)+
    ggtitle(title)+
    scale_x_continuous( name = "Mana values", labels  = 1:max(data.df$Mana_value),
                        breaks = 1:max(data.df$Mana_value));
  return(Bar_plot)
}


#Loading data.

mana_curve_examples_csv_export = "Data/003_Example_curves_by_format/003_Example_curves_by_format.xlsx";

mv_example.df <- read_excel(path =  mana_curve_examples_csv_export);

#Plot data

Curve_types = unique(mv_example.df$Mana_curve_type);
Curve_types

Curve_plots = list()

for (type in Curve_types){
  print(type);
  Bar_plot_per_type = Create_Bar_plot( data.df = mv_example.df[which(mv_example.df$Mana_curve_type == type),],
                                       title = type);
  Curve_plots = append(Curve_plots,Bar_plot_per_type);
}

Bar_plot_per_type;

Complete_Plot = plot_grid(plotlist = Curve_plots, nrow = 1);
Complete_Plot;
#Save Plot

plot_name = paste("Chapter_5_1_3__Mana_curve_by_format_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = Complete_Plot, 
       width = 8, height = 4, dpi = 300);
