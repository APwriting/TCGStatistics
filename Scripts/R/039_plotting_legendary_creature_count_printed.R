#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(readxl);
library(geomtextpath);

legendary.df = read.table(file="../../Data/008_Commander_per_year/Commanders_by_years.txt",
                          header=1)


legendary.plot = ggplot(legendary.df,aes(x=Year,y=Count))+
  geom_point()+
  geom_line()+
  scale_y_continuous(limits = c(0,1000))+
  ggtitle("Commanders printed in each year.")+
  theme(
    plot.title = element_text(hjust = 0.5)
  );
legendary.plot;







plot_name = paste("Chapter_2_legendary_creatur_count__plot__", Sys.Date()  ,".png",sep = "");
ggsave(plot_name, plot = legendary.plot, 
       width =4, height =3, dpi = 300);
