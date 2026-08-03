#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);

#Own Libraries
library(AnaMTG);


# Generating or loading plot data

data.df = data()

turn = c(0);
lands_played = c(0);
cards_drawn = c(7);

for (i in 1:20) {
  turn = c(turn, turn[i]+1);
  lands_played = c(lands_played, lands_played[i]+1);
  cards_drawn = c(cards_drawn, cards_drawn[i]+1);
}

data.df <- data.frame(
  turn = turn,
  lands_played = lands_played,
  Mana = lands_played,
  cards_drawn = cards_drawn
)
##life point plot
life.df = data()

turn = c(0);
life = c(40);


for (i in 1:20) {
  turn = c(turn, turn[i]+1);
  life = c( life, 40 );
}

life.df <- data.frame(
  turn = turn,
  life = life
)


#Creating Plots
Base_plot = ggplot(data.df, aes(x=turn, y=lands_played)) +
  geom_line(color = "darkgreen")+
  geom_point()+
  scale_x_continuous( name = "Turn in game")+
  scale_y_continuous(
    
    # Features of the first axis
    name = "Lands played",
    breaks = lands_played,
    
    # Add a second axis and specify its features
    sec.axis = sec_axis( trans=~.*1, breaks = lands_played, 
                         labels =cards_drawn, name="Cards drawn")
  )+
  background_grid();
Base_plot;


Life_plot = ggplot(life.df, aes(x=turn, y=life)) +
  geom_line(color = "darkgrey")+
  geom_point()+
  scale_x_continuous( name = "Turn in game")+
  scale_y_continuous(
    
    # Features of the first axis
    name = "Life points",
    breaks  = c(0,10,20,30,40,50),
    limits  = c(0,50),
    labels = c(0,10,20,30,40,50)
    );
Life_plot;


#Saving plots and/or data if necessary

ggsave("Chapter_4_1__Baseline_plot__06072026.png", plot = Base_plot, 
       width = 6, height = 4, dpi = 300);
ggsave("Chapter_4_1__Lifeline_plot__06072026.png", plot = Life_plot, 
       width = 6, height = 4, dpi = 300);








