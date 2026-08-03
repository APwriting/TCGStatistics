#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);

#Own Libraries
library(AnaMTG);


#Data creation
#Plot1
data.exact1 <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 20, min_number_in_deck = 1,
                                        deck_size = 99, draws = 8);
data.exact2 <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 20, min_number_in_deck = 1,
                                        deck_size = 99, draws = 9);
data.exact3 <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 20, min_number_in_deck = 1,
                                        deck_size = 99, draws = 10);
data.exact4 <- run_exact_land_base_test(exactX = 1, max_number_in_deck = 20, min_number_in_deck = 1,
                                        deck_size = 99, draws = 11);



Create_part_plots <- function(data.df, turn, draws){
  #script function because the same plot is repeated 4 times below
  Optimization_point = data.df$N[tail(which( data.df$P == max(data.df$P )),1)];
  Opti_label = paste("Optimization point ", as.character(Optimization_point));

  XLabel = paste( "Lands in deck (decksize = 99).", "Turn ", as.character(turn),
  "", as.character(draws), "Draws." );
  
  plot_land_base= ggplot(data.df, aes(x = N, y = P)) +
    geom_line() +
    # theme_minimal()+
    scale_y_continuous(
      name = "Probability exactly 1 land in hand", limits = c(0,0.5)
    )+
    scale_x_continuous(
      name = XLabel
    )+ 
    # theme(legend.position="none")+
    geom_vline( xintercept = Optimization_point)+
    geom_textvline(label = Opti_label, xintercept = Optimization_point, vjust = -0,9);
  plot_land_base;
  
  return(plot_land_base);
  
}


exact1_land_base = Create_part_plots(data.exact1, 1, 8);
exact1_land_base;
exact2_land_base = Create_part_plots(data.exact2, 2, 9);
exact2_land_base;
exact3_land_base = Create_part_plots(data.exact3, 3, 10);
exact3_land_base;
exact4_land_base = Create_part_plots(data.exact4, 4, 11);
exact4_land_base;


Plot_list = list( exact1_land_base, exact2_land_base, exact3_land_base, exact4_land_base);

Comparison_plot_Opti_point = plot_grid(plotlist = Plot_list,labels = c("A","B","C", "D"));
Comparison_plot_Opti_point;


#Saving of Plot
plot_name = paste("Chapter_4_6__Opti_Point_comparison__", Sys.Date()  ,".png")
ggsave(plot_name, plot = Comparison_plot_Opti_point, 
       width = 9, height = 9, dpi = 300);



