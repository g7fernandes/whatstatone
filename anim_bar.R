# install.packages("ggplot2")
# install.packages("gganimate")

library(readr)
library(gganimate)

df_zap <- read_csv("./database4R_men_per_month.csv")


staticplot = ggplot(df_zap, aes(index, group = name, 
                                   fill = as.factor(name), color = as.factor(name))) +
  geom_tile(aes(y = value/2,
                height = value,
                width = 0.9), alpha = 0.8, color = NA) +
  geom_text(aes(y = 0, label = paste(name, " ")), vjust = 0.2, hjust = 1) +
  geom_text(aes(y=value,label = value, hjust=0)) +
  coord_flip(clip = "off", expand = FALSE) +
  scale_y_continuous(labels = scales::comma) +
  scale_x_reverse() +
  guides(color = FALSE, fill = FALSE) +
  theme(axis.line=element_blank(),
        axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        axis.title.x=element_blank(),
        axis.title.y=element_blank(),
        legend.position="none",
        panel.background=element_rect(colour = "lightcyan1"),
        panel.border=element_blank(),
        panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),
        panel.grid.major.x = element_line( size=.1, color="grey" ),
        panel.grid.minor.x = element_line( size=.1, color="grey" ),
        plot.title=element_text(size=25, hjust=0.5, face="bold", colour="grey", vjust=-1),
        plot.subtitle=element_text(size=18, hjust=0.5, face="italic", color="grey"),
        plot.caption =element_text(size=12, hjust=0.5, face="italic", color="grey"),
        plot.background=element_blank(),
        plot.margin = margin(2 ,8, 2, 4, "cm"))



anim = staticplot + transition_states(date, transition_length = 4, state_length = 1) +
  view_follow(fixed_x = TRUE)  +
  labs(title = 'Data : {closest_state}',  
       subtitle  =  "Mensagens por mês",
       caption  = "Top 10 envios nos 30 dias passados")


# install.packages("gifski_renderer")\

# animate(anim, 400, fps = 20,  width = 1200, height = 800, 
#         renderer = gifski_renderer("spotify_usa.gif"))

animate(anim, 2400, fps = 20,  width = 1200, height = 1000, renderer = ffmpeg_renderer()) -> for_mp4
anim_save("animation_per_month.mp4", animation = for_mp4 )