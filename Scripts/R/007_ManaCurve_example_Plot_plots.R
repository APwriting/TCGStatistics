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


#Load data in data frame from csv
#hitmonkey.df <- read.csv("Data/001_Example_decklist_Hitmonkey/hitmonkey_example_deck.csv",
#                         sep = ",");

#Verify extra layer quotes from archideck export
#By changing the variable below to a variable given by call of the script, one can make an automatic script for mana curves of different decks
commander_csv_export = "Data/001_Example_decklist_Hitmonkey/hitmonkey_example_deck.csv";
cat( readLines(commander_csv_export, n = 3) );

lines <- readLines(commander_csv_export)

# Remove one leading and one trailing quote from each line
lines <- sub('^"', "", lines);
lines <- sub('"$', "", lines);

# Convert doubled quotes ("") back to single quotes (")
lines <- gsub('""', '"', lines);

# Read as CSV
Commander.deck.df <- read.csv(text = lines, stringsAsFactors = FALSE);
Commander.deck.df = Commander.deck.df[ which(Commander.deck.df$Category!="Maybeboard" & Commander.deck.df$Category!="Sideboard"),]; 

#clean up data, cut things down, load counts for each mana value for separate data frame

mana_values = Commander.deck.df[which(Commander.deck.df$Cardtype!="Land"),"Manavalue"];

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

commander.df = hitmonkey.df[which(hitmonkey.df$Category=="Commander"),];

#Loading scryfall API
id <- commander.df$ScryfallCode;
#APIurl <- paste0("https://api.scryfall.com/cards/", id)
#APIurl;
#commander.card <- fromJSON(paste0("https://api.scryfall.com/cards/", id))

commander.card = Load_ScryfallCard(id);

commander_image = commander.card$image_uris$normal;

#Add picture to plot
Mana_value_plot = Mana_value_plot+
  geom_image( data= data.frame(x = 10, y = 20, image = commander_image),
    aes(x = 8, y = 17),
    image = commander_image,
    size = 0.35
  )
Mana_value_plot;

#Plot saving
plot_name = paste("Chapter_5_1__Mana_curve_example_plot__", Sys.Date()  ,".png")
ggsave(plot_name, plot = Mana_value_plot, 
       width = 8, height = 8, dpi = 300);



