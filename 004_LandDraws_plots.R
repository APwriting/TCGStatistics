#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);
library(reshape);

#Functions

#Functions
#These are not needed here but will be kept
probability_exact <- function(x, draws, y, deck_size) {
  dhyper(x, y, deck_size - y, draws)
}
probability_at_least <- function(x, draws, y, deck_size) {
  1 - phyper(x - 1, y, deck_size - y, draws)
}

hypergeo_variance <- function(N, K, n) {
  #mean <- n * K / N
  
  variance <- n * (K / N) * (1 - K / N) * ((N - n) / (N - 1))
}

#Function to have the test with at least amount
run_exact_land_base_test <- function(exactX, max_number_in_deck, 
                                     deck_size = 99, draws = 7) {
  num = c()
  Probability_X = c()
  Variation = c()
  
  for (at_least_so_many in 0:exactX){
    
    
    for (number_in_deck in 34:max_number_in_deck) {
      prob_result <-
        probability_exact(
          x = at_least_so_many,
          draws = draws,
          y = number_in_deck,
          deck_size = deck_size
        )
      Probability_X = c(Probability_X, prob_result)
      Variation = c(Variation, as.character(at_least_so_many))
      num = c(num, number_in_deck)
    }
    
    #data.df[[paste0("col", at_least_so_many)]] = Probability_X
  }
  data.df = data.frame(N=num, P=Probability_X, V=Variation)
  
  return(data.df)
}

max_drawn = 11;

num = c()
Probability_X = c()
Variation = c()
cards_drawn_count = c()

cards_draw_list = c();
land_counts = c();
Mean_expected_draw = c();
SD_expected_draw = c();

for (cards_drawn in 7:max_drawn){
  #print(cards_drawn);
  for (number_in_deck in 35:42) {
    #print(number_in_deck);
    chance_dep_lands = number_in_deck/99;
    mean_lands_drawn = cards_drawn*chance_dep_lands;
    print( mean_lands_drawn);
    Draw_variance = hypergeo_variance(N = 99, K = number_in_deck, n = cards_drawn);
    Draw_SD = sqrt(Draw_variance);
    
    cards_draw_list = c(cards_draw_list, cards_drawn);
    land_counts = c(land_counts, number_in_deck);
    Mean_expected_draw = c(Mean_expected_draw, mean_lands_drawn);
    SD_expected_draw = c(SD_expected_draw, Draw_SD);
    
    
  }
}
mean_draw_data.df = data.frame( drawn = cards_draw_list, lands = as.character(land_counts), 
                                mean = Mean_expected_draw,  SD = SD_expected_draw );




#Plot



exact_draw_sim_plot= ggplot(mean_draw_data.df, aes(x = drawn, y = mean, group = lands)) +
  geom_line(aes(color = lands)) +
  geom_point(aes(color = lands)) +
  theme_minimal()+
  scale_color_discrete(name = "Land count")+
  scale_y_continuous(
    name = "Mean expected draw"
  )+
  scale_x_continuous(
    name = "Number of cards drawn",
  );
exact_draw_sim_plot;

#Plot focusing on 35 with SD

plot_list = list()
i=1
used_examples = c(35, 37, 39, 41);
for (examples in used_examples){
  SDdata.df = mean_draw_data.df[which(mean_draw_data.df$lands==examples),];
  SDexact_draw_sim_plot= ggplot(SDdata.df, aes(x = drawn, y = mean)) +
    geom_line() +
    geom_point() +
    theme_minimal()+
    scale_y_continuous(
      name = "Mean expected draw",limits = c(1,6.5)
    )+
    scale_x_continuous(
      name = "Number of cards drawn",
    )+
    geom_errorbar(aes(ymin=mean-SD, ymax=mean+SD));
  plot_list[[i]] <- SDexact_draw_sim_plot;
  i <- i + 1
}
SD_whole_plot = plot_grid(plotlist = plot_list, labels = paste( "lands ", as.character(used_examples)));
SD_whole_plot;
#Saving Plot

plot_name = paste("Chapter_4_5__mean_drawn_dep_land_plot", Sys.Date()  ,".png")
ggsave(plot_name, plot = exact_draw_sim_plot, 
       width = 6, height = 4, dpi = 300);
plot_name = paste("Chapter_4_5__mean_drawn_SD_dep_land_plot", Sys.Date()  ,".png")
ggsave(plot_name, plot = SD_whole_plot, 
       width = 6, height = 4, dpi = 300);













#Dumpig test ground


for (cards_drawn in 7:max_drawn){
  
  data.df = run_exact_land_base_test(exactX = cards_drawn, max_number_in_deck = 43, 
                                     deck_size = 99, draws = cards_drawn);
  Probability_X = c(Probability_X, data.df$P);
  Variation = c(Variation, as.integer(data.df$V));
  num = c(num, data.df$N);
  
  #Calculate average statistic
  
  Unique_land_counts = unique(num);
  for (land_count in Unique_land_counts){
    data_land_count_based.df = data.df[which(data.df$N ==land_count),];
    average_draw_chance = as.double(data_land_count_based.df$P) * as.double(data_land_count_based.df$V);
    data_land_count_based.df$average = average_draw_chance;
    
    
    mean(average_draw_chance);
    mean(data_land_count_based.df$P);
    sd(average_draw_chance);
    
  }
  
  cards_drawn_count = c( cards_drawn_count, rep(cards_drawn, times = length(data.df$P)));
  
}

cardsD.df = data.frame(N=num, P=Probability_X, V=Variation, drawn = cards_drawn_count);



sum( data_land_count_based.df$P);
ggplot( data_land_count_based.df, aes(x = V, y = P))+geom_point();


exact_draw_sim_plot= ggplot(cardsD.df, aes(x = N, y = P, group = drawn)) +
  geom_line(aes(color = drawn)) +
  geom_point(aes(color = drawn)) +
  theme_minimal()+
  scale_color_discrete(name = "Lands")+
  scale_y_continuous(
    name = "Probability exactly X land in starting hand",
  )+
  scale_x_continuous(breaks = c(20, 22,25, 27, 30, 32, 35, 37, 40, 42, 45, 47, 50),
                     name = "Lands in deck (decksize = 99)",
  );
exact_draw_sim_plot;




