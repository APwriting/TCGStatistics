#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);
library(geomtextpath);
library(dplyr);


current_path = getwd();
setwd("../Python/028_pipped_analysis_scryfall_seach");#

all_counted_pips.df = read.table("028_results_colored_pips_scryfall_search.txt",sep = "\t", header = 1);

all_counted_pips.df$Color <- factor(all_counted_pips.df$Color, levels = c("W", "U", "B", "R", "G"))
all_counted_pips.df$Pips <- factor(all_counted_pips.df$Pips, levels = c("2", "3", "4", "5", "6"))

yearly_pips.df = read.table("028_results__by_year__colored_pips_scryfall_search.txt",sep = "\t", header = 1);
yearly_pips.df = yearly_pips.df[which(yearly_pips.df$Year!=2026),];
yearly_pips.df$Pips = factor(yearly_pips.df$Pips, levels = c("2", "3", "4", "5", "6"));


#yearly_pips.df$Year
setwd(current_path);

#Defining color selection
wubrg_colors <- c(
  W = "#F9FAF4",  # White
  U = "#0E68AB",  # Blue
  B = "#150B00",  # Black
  R = "#D3202A",  # Red
  G = "#00733E"   # Green
)
wubrg_colors <- c(
  W = "#E8E2C4", # White
  U = "#2490D0",# Blue
  B = "#222222",# Black
  R = "#D92B2B",# Red
  G = "#16833B" # Green
)
wubrg_colors <- c(
  W = "#F9F6E8",  # White
  U = "#2490D0",  # Blue
  B = "#171717",  # Black
  R = "#D92B2B",  # Red
  G = "#16833B"   # Green
)
wubrg_colors <- c(
  W = "#E8E2C4", # White
  U = "#2490D0",# Blue
  B = "#2B2523",  # Black
  R = "#D64A2E",  # Red
  G = "#4F8A3A"   # Green
)

#Plotting data

Two_pips.plot = ggplot( all_counted_pips.df[which(all_counted_pips.df$Pips==2),],aes( x=Pips, y=results, fill=Color ) )+
  geom_col(position = "dodge", color="grey")+
  scale_fill_manual(values = wubrg_colors)+
  scale_x_discrete( name = "Number of Pips",
                      breaks = c(2), labels = c(2)
  )+   theme(legend.position = "none")+
  scale_y_continuous(name="Number of all cards");
Two_pips.plot;

Three_pips.plot = ggplot( all_counted_pips.df[which(all_counted_pips.df$Pips==3),],aes( x=Pips, y=results, fill=Color ) )+
  geom_col(position = "dodge", color="grey")+
  scale_fill_manual(values = wubrg_colors)+
  scale_x_discrete( name = "Number of Pips",
                    breaks = c(3), labels = c(3)
  )+   theme(legend.position = "none")+
  scale_y_continuous(name="Number of all cards");
Three_pips.plot;

More4_pips.plot = ggplot( all_counted_pips.df[all_counted_pips.df$Pips %in% c(4), ],aes( x=Pips, y=results, fill=Color ) )+
  geom_col(position = "dodge", color="grey")+
  scale_fill_manual(values = wubrg_colors)+
  scale_x_discrete( name = "Number of Pips",
                    breaks = c(4,5), labels = c(4,5)
  )+   theme(legend.position = "none")+
  scale_y_continuous(name="Number of all cards",limits = c(0,10));
More4_pips.plot;

More5_pips.plot = ggplot( all_counted_pips.df[all_counted_pips.df$Pips %in% c(5), ],aes( x=Pips, y=results, fill=Color ) )+
  geom_col(position = "dodge", color="grey")+
  scale_fill_manual(values = wubrg_colors)+
  scale_x_discrete( name = "Number of Pips",
                    breaks = c(4,5), labels = c(4,5)
  )+

  scale_y_continuous(name="Number of all cards",limits = c(0,10));
More5_pips.plot;

plot_list = list(Two_pips.plot, Three_pips.plot, More4_pips.plot, More5_pips.plot);

all_pips.plot = plot_grid(plotlist = plot_list);
all_pips.plot;

#Plotting the time of the general colors of the last 10 years.


yearly.2pips.plot = ggplot( yearly_pips.df[which(yearly_pips.df$Pips==2),], aes(x=Year, y=results))+
  geom_point()+
  geom_line()+
scale_x_continuous( name = "Year")+
  scale_y_continuous(name="Number of all cards")+
  ggtitle(label = "2 pips")+
  theme(
    plot.title = element_text(hjust = 0.5)
  );
yearly.2pips.plot;

yearly.3pips.plot = ggplot( yearly_pips.df[which(yearly_pips.df$Pips==3),], aes(x=Year, y=results))+
  geom_point()+
  geom_line()+
  scale_x_continuous( name = "Year")+
  scale_y_continuous(name="Number of all cards")+
  ggtitle(label = "3 pips")+
  theme(
    plot.title = element_text(hjust = 0.5)
  );
yearly.3pips.plot;

yearly.4pips.plot = ggplot( yearly_pips.df[which(yearly_pips.df$Pips==4),], aes(x=Year, y=results))+
  geom_point()+
  geom_line()+
  scale_x_continuous( name = "Year")+
  scale_y_continuous(name="Number of all cards")+
  ggtitle(label = "4 pips")+
  theme(
    plot.title = element_text(hjust = 0.5)
  );
yearly.4pips.plot;

yearly.5pips.plot = ggplot( yearly_pips.df[which(yearly_pips.df$Pips==5),], aes(x=Year, y=results))+
  geom_point()+
  geom_line()+
  scale_x_continuous( name = "Year")+
  scale_y_continuous(name="Number of all cards")+
  ggtitle(label = "5 pips")+
  theme(
    plot.title = element_text(hjust = 0.5)
  );
yearly.5pips.plot;


yearly.plot_list = list(yearly.2pips.plot, yearly.3pips.plot, yearly.4pips.plot, yearly.5pips.plot);

yearly.all_pips.plot = plot_grid(plotlist = yearly.plot_list);
yearly.all_pips.plot;


#

#Saving the plot

plot_name = paste("Chapter_8_7_1_number_all_cards_multi_pips__plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = all_pips.plot, 
       width =8, height =9, dpi = 300);


plot_name = paste("Chapter_8_7_2__number_printed_multipip_per_year__plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = yearly.all_pips.plot, 
       width =8, height =8, dpi = 300);


