#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);

#Own Libraries
library(AnaMTG);



# Generating or loading plot data

data.df = data()

turn = c(0);
lands_played = c(0);
cards_drawn = c(7);

break_point = 2;
beakpoint_informaiton = c(0);

lands_count_after_BP = c(NA);

for (i in 1:10) {
  turn = c(turn, turn[i]+1);
  lands_played = c(lands_played, lands_played[i]+1);
  cards_drawn = c(cards_drawn, cards_drawn[i]+1);
  
  if (i < break_point){
    beakpoint_informaiton = c(beakpoint_informaiton,0);
  }else{
    beakpoint_informaiton = c(beakpoint_informaiton,1);
  }
  if (i < break_point){
    lands_count_after_BP = c(lands_count_after_BP,NA);
  }else{
    lands_count_after_BP = c(lands_count_after_BP,lands_played[i]+2);
  }
  
}

data.df <- data.frame(
  turn = turn,
  lands_played = lands_played,
  Mana = lands_played,
#  cards_drawn = cards_drawn,
  BpI = beakpoint_informaiton,
  lc_after = lands_count_after_BP
)



#Creating Plots
Base_break_plot = ggplot(data.df, aes(x=turn, y=lands_played)) +
  
  geom_vline( xintercept = break_point,colour = "lightgrey")+
  geom_textvline(label = "Break point", xintercept = break_point, vjust = -0.4, 
                 hjust = 0.8,colour = "grey")+
  
  geom_line(mapping = aes(colour = BpI))+
  geom_point()+

  geom_line(color = "chartreuse2",mapping = aes( x = turn, y = lc_after))+
  geom_point(mapping = aes( x = turn, y = lc_after))+
  
  scale_x_continuous( name = "Turn in game", labels = c(0,1,2,3,4,5,6,7,8,9,10), 
                      breaks = c(0,1,2,3,4,5,6,7,8,9,10))+
  scale_y_continuous(name = "Lands played", labels = c(0,1,2,3,4,5,6,7,8,9,10), 
                     breaks = c(0,1,2,3,4,5,6,7,8,9,10))+

  geom_segment(aes(x = 2, y = 0, xend = 2, yend = 2.8),colour = "darkgreen",
               arrow = arrow(length = unit(0.3, "cm"), type = "closed")
  )+
  geom_textvline(label = "2 mana ramp", xintercept = break_point, vjust = 1.4, 
                 hjust = 0.04,colour = "darkgreen")+
 theme(legend.position="none")+
  background_grid();
Base_break_plot;

#Saving the plot

plot_name = paste("Chapter_4_7__breakpoint_illustration_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = Base_break_plot, 
       width = 6, height = 6, dpi = 300);
