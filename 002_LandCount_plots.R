#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);

#Own Libraries
library(AnaMTG);



exactX, max_number_in_deck, min_number_in_deck = 1,
deck_size = 99, draws = 7)

#Plot1
data.exact1 <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 50)

#Plot2
data.atleast1 <- run_Atleast_land_base_test(At_least_x = 1, max_number_in_deck = 50)

#Plot3
data.next_draws <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 50, 
                                     deck_size = 92, draws = 1)
data.next_draws$N=data.next_draws$N+1;


data.next_2draws <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 50, 
                                            deck_size = 92, draws = 2)
data.next_2draws$N=data.next_2draws$N+1;


#Plot3B
data.turn2all_draws <- run_Atleast_land_base_test(At_least_x = 1, max_number_in_deck = 50, 
                                                  deck_size = 99, draws = 9)




#
#Plot1
Optimization_point = data.exact1$N[which( data.exact1$P == max(data.exact1$P ))];

exact1_land_base= ggplot(data.exact1, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability exactly 1 land in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 99)",
  )+ 
  theme(legend.position="none")+
  geom_vline( xintercept = Optimization_point)+
  geom_textvline(label = "Optimization point", xintercept = Optimization_point, vjust = -0,9);
exact1_land_base;


data.exact1$N[which( data.exact1$P == max(data.exact1$P ))]

#Plot2
atleast1_land_base= ggplot(data.atleast1, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability AT LEAST 1 land in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 99)",
  )+ 
  theme(legend.position="none");
atleast1_land_base;

# Example: probability of drawing at least 1 copy
probability_at_least(x = 0, draws = 7, y = 37, deck_size = 100)


#Plot3
next_draw_prob_plot= ggplot(data.next_draws, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability next draw a land with 1 land in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 92)",
  )+ 
  theme(legend.position="none");
next_draw_prob_plot;

next_2draw_prob_plot= ggplot(data.next_2draws, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  theme_minimal()+
  scale_y_continuous(
    name = "Probability next draw a land with 1 land in hand",
  )+
  scale_x_continuous(
    name = "Lands in deck (decksize = 92)",
  )+ 
  theme(legend.position="none");
next_2draw_prob_plot;


Plot3_draws = plot_grid( next_draw_prob_plot, next_2draw_prob_plot, labels = c("A", "B"))
Plot3_draws;


  
###
#Saving the plots



ggsave("Chapter_4_3__exact1land_plot__09072026.png", plot = exact1_land_base, 
       width = 6, height = 4, dpi = 300);
ggsave("Chapter_4_3__ATLEAST1land_plot__09072026.png", plot = atleast1_land_base, 
       width = 6, height = 4, dpi = 300);
ggsave("Chapter_4_3__NextDraw1land_plot__09072026.png", plot = Plot3_draws, 
       width = 6, height = 6, dpi = 300);


  
  