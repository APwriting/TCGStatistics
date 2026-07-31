#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);
library(geomtextpath);

#Own Libraries
library(AnaMTG);


#read deck lists
current_path = getwd();
path_to_examples = "C:/Users/falkn/Documents/Projects/Magic_Deck_building_Statistics/Data/004_example_deck_lists_mana_curve_commander_influence";
setwd(path_to_examples);

deck_lists = read_archidekt_export(path_to_examples);
path = path_to_examples;

current_path = getwd();
if (0){
  setwd(path);
}
decks = list();
deck_list_paths = list.files( path = path,pattern = "\\.csv$",full.names = TRUE);
for (deck_path in deck_list_paths){
  print(deck_path);
  #current_deck = read_archidekt_export(deck_path);
  Commander.deck.df <- read.csv(file   = deck_path);
  lines <- readLines(deck_path);
  #print(lines);
  # Remove one leading and one trailing quote from each line
  lines <- sub('^"', "", lines);
  lines <- sub('"$', "", lines);
  
  # Convert doubled quotes ("") back to single quotes (")
  lines <- gsub('""', '"', lines);
  Commander.deck.df <- read.csv(text = lines, stringsAsFactors = FALSE);
#Problem hier wegen Sachen, Commas in last column Card text!, muss das wohl exportieren ohne.
  
  
  
  
  #print(current_deck);
  Commander.deck.df = remove_maybe_and_sideboard(Commander.deck.df);
  decks[[length(decks) + 1]] <- Commander.deck.df
  
}

#Generate Plots

Mana_curves = list();
for (Commander.deck.df in decks){
  #Remove lands
  
  #Get Commander
  commander.df = Commander.deck.df[which(Commander.deck.df$Category=="Commander"),];
  title = commander.df$Name;
  commander_mv = commander.df$Mana.Value;
  
  #Creat count data 
  mana_values = Commander.deck.df[which(Commander.deck.df$Types!="Land"),];
  mana_values = mana_values$Mana.Value;
  mv.df = return_mv_count( mana_values );
  mv.df;
  mv.df$mana_values = as.integer(as.character(mv.df$mana_values));
  
  
  #Plot data
  Curve_plot = Create_Mana_curve_plot(mv.df, title);
  Curve_plot = Curve_plot +   geom_vline( xintercept = commander_mv)+
   geom_textvline(label = "CMV",xintercept = commander_mv, vjust = -0.4, hjust = 0.8);
  
  #urve_plot;
  Mana_curves[[length(Mana_curves) + 1]] = Curve_plot;

}


Whole_mv_plot = plot_grid(plotlist = Mana_curves);
Whole_mv_plot;


data.df = decks[1];


#Saving
setwd(current_path);
plot_name = paste("Chapter_5_2_1_mv_commander_plot__", Sys.Date()  ,".png");
ggsave(plot_name, plot = Whole_mv_plot, 
       width =10, height =10, dpi = 300);


