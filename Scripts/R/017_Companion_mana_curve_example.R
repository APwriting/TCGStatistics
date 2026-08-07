#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
#library(ggpubr);
#library(geomtextpath);
library(ggimage);

library(jsonlite)

#Own Libraries
library(AnaMTG);

#prepping directory
current_directoy = getwd();
setwd("../../..");#Adjust if needed

#Load data in data frame from csv

#Verify extra layer quotes from decklist export
#By changing the variable below to a variable given by call of the script, one can make an automatic script for mana curves of different decks


commander_csv_export = "Data/005_Companion_example_mana_curve/planechaseimic.csv";
cat( readLines(commander_csv_export, n = 3) );

lines <- readLines(commander_csv_export)

# Remove one leading and one trailing quote from each line
lines <- sub('^"', "", lines);
lines <- sub('"$', "", lines);

# Convert doubled quotes ("") back to single quotes (")
lines <- gsub('""', '"', lines);
#Correct lines for mana cost that is included by spells for some reason always.
corrected.lines = c();
for (line in lines){
  print(line);
  v <- strsplit(line, ",")[[1]]
  print( length(v) );
  if (length(v) >= 7) {
    v <- v[-length(v)]
  }
  v = paste(v, collapse = ",")
  corrected.lines <- c(corrected.lines,
                       v);
  print(v);
}


# Read as CSV
Commander.deck.df <- read.csv(text = lines, stringsAsFactors = FALSE,header = 1);
Commander.deck.df = Commander.deck.df[ which(Commander.deck.df$Category!="Maybeboard" & Commander.deck.df$Category!="Sideboard"),]; 
Commander.deck.df = Commander.deck.df[ which(Commander.deck.df$Category!="Land" ),]; 
Commander.deck.df <- Commander.deck.df[!is.na(Commander.deck.df$Mana.Value), ];


#clean up data, cut things down, load counts for each mana value for separate data frame

mana_values = Commander.deck.df[which(Commander.deck.df$Types!="Land"),"Mana.Value"];

mv.df = return_mv_count( mana_values );
mv.df;
mv.df$mana_values = as.integer(as.character(mv.df$mana_values));

#This is wrong

max_mana_value = max(as.integer(mv.df$mana_values));
mv.df;
for (i in 1:max_mana_value){
  #print(i);
  if (!(i %in% mv.df$mana_values)){
    mv.df[(nrow(mv.df) + 1),] = c(i,0);
  }
  #print(mv.df);
}
mv.df;
#Plot data


Mana_value_plot = ggplot(mv.df,aes(x=mana_values, y=Freq))+
  geom_col( fill = "darkseagreen1", color = "darkgreen")+
  scale_x_continuous( name = "Mana values", labels = seq_len(max(mana_values)), 
                      breaks = seq_len(max(mana_values)))+
  scale_y_continuous(name = "Count")+
  geom_text(aes(label = Freq),
            vjust = -0.5)+
  theme_cowplot() +
  background_grid(major = "y", minor = "y");
Mana_value_plot;

#Load_picture

commander.df = Commander.deck.df[which(Commander.deck.df$Category=="Commander"),];
commander.df;
#Loading scryfall API
ids <- commander.df$Scryfall.ID;
ids;


scryfall_links = c()
for (id in ids){
  commander.card = Load_ScryfallCard(id);
  commander_image = commander.card$image_uris$normal;
  scryfall_links = c(scryfall_links, commander_image);
}
scryfall_links;

combine_images(scryfall_links[1], scryfall_links[2], output_file = "combined.png");

#Add picture to plot
Mana_value_plot.commander = Mana_value_plot+
  geom_image( data= data.frame(x = 10, y = 20, image = "combined.png"),
              aes(x = 6.7, y = 10),
              image = "combined.png",
              size = 0.35
  )
Mana_value_plot.commander;


file.remove("combined.png");
#Plot saving
plot_name = paste("Chapter_5_8_1__Mana_curve_companion_example_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = Mana_value_plot.commander, 
       width = 8, height = 6, dpi = 300);



