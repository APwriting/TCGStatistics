#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);
library(reshape);

#Own Libraries
library(AnaMTG);



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














