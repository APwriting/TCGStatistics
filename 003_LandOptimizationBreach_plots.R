#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);
library(reshape);

#Functions
#These are not needed here but will be kept
probability_exact <- function(x, draws, y, deck_size) {
  dhyper(x, y, deck_size - y, draws)
}
probability_at_least <- function(x, draws, y, deck_size) {
  1 - phyper(x - 1, y, deck_size - y, draws)
}

#Function to have the test with at least amount
run_exact_land_base_test <- function(exactX, max_number_in_deck, 
                                     deck_size = 99, draws = 7) {
  num = c()
  Probability_X = c()
  Variation = c()
  
  for (at_least_so_many in 1:exactX){
    
    
    for (number_in_deck in 1:max_number_in_deck) {
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


#Generate the data

#Plot 1 Data 1
data.df = run_exact_land_base_test(exactX = 7, max_number_in_deck = 50, 
                                    deck_size = 99, draws = 7);
data.df = data.df[ which(data.df$V>1  & data.df$N>=27  & data.df$N<=45), ];

#Plot 2 data 2
data.df = run_exact_land_base_test(exactX = 7, max_number_in_deck = 50, 
                                   deck_size = 99, draws = 7);
Exact2_data.df = data.df[ which(data.df$V==2  & data.df$N>=20  & data.df$N<=49), ];
Exact3_data.df = data.df[ which(data.df$V==3  & data.df$N>=20  & data.df$N<=49), ];

Exact_2_3_combined_data.df = Exact3_data.df[,];
Exact_2_3_combined_data.df$V = c("2 and 3 combined");
Exact_2_3_combined_data.df$P = Exact2_data.df$P + Exact3_data.df$P;
df.list = list( Exact2_data.df, Exact3_data.df, Exact_2_3_combined_data.df );
Exact_2_3_combined_data.df <- merge_recurse(df.list);



#Plot
exact_ALL_land_base= ggplot(data.df, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  geom_point(aes(color = V)) +
  theme_minimal()+
  scale_color_discrete(name = "Lands")+
  scale_y_continuous(
    name = "Probability exactly X land in starting hand",
  )+
  scale_x_continuous(breaks = c(27, 30, 32, 35, 37, 40, 42, 45),
    name = "Lands in deck (decksize = 99)",
  );
exact_ALL_land_base;

#Plot 2
Optimization_point = Exact_2_3_combined_data.df$N[which( Exact_2_3_combined_data.df$P == max(Exact_2_3_combined_data.df$P ))];
exact_2and3_land_base= ggplot(Exact_2_3_combined_data.df, aes(x = N, y = P, group = V)) +
  geom_line(aes(color = V)) +
  geom_point(aes(color = V)) +
  theme_minimal()+
  scale_color_discrete(name = "Lands")+
  scale_y_continuous(
    name = "Probability exactly X land in starting hand",
  )+
  scale_x_continuous(breaks = c(20, 22,25, 27, 30, 32, 35, 37, 40, 42, 45, 47, 50),
                     name = "Lands in deck (decksize = 99)",
  )+
  geom_vline( xintercept = Optimization_point)+
  geom_textvline(label = "Optimization point", xintercept = Optimization_point, vjust = -0.4, hjust = 0.8);
exact_2and3_land_base;


#Saving
plot_name = paste("Chapter_4_4__exactALLland_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = exact_ALL_land_base, 
       width = 6, height = 4, dpi = 300);
plot_name = paste("Chapter_4_4__exactALLland_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = exact_2and3_land_base, 
       width = 6, height = 4, dpi = 300);

