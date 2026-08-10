#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);

#Own Libraries
library(AnaMTG);


#Plot1
data.atleast2 <- run_Atleast_land_base_test(At_least_x = 2, max_number_in_deck = 50);

#Plot2
data.atleast3 <- run_Atleast_land_base_test(At_least_x = 3, max_number_in_deck = 50);

data.atleast3$Mulligan = data.atleast3$P+(1-data.atleast3$P)*data.atleast3$P;

#Plotting



#Plot1
atleast2_land_base= ggplot(data.atleast2, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability AT LEAST 2 land in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 99)",
  )+ 
  theme(legend.position="none");
atleast2_land_base;


#Plot2
atleast3_land_base= ggplot(data.atleast3, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability AT LEAST X lands in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 99)",
  )+ 
   labs(color = "At least x lands",)+
  theme(legend.position = "bottom")+
  ggtitle("Before Mulligan");
atleast3_land_base;


#Plot3
atleast3_land_base.Mulligan= ggplot(data.atleast3, aes(x = N, y = Mulligan, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability AT LEAST X lands in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 99)",
  )+ 
  labs(color = "At least x lands",)+
  theme(legend.position = "bottom")+
  ggtitle("After Mulligan");
atleast3_land_base.Mulligan;

Plot_list = list(atleast3_land_base, atleast3_land_base.Mulligan);

combined.plot = plot_grid(plotlist = Plot_list);
combined.plot;
###
#Saving the plots


plot_name = paste("Chapter_6_2_1__at_least_x_lands_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = combined.plot, 
       width = 6, height = 4, dpi = 300);




