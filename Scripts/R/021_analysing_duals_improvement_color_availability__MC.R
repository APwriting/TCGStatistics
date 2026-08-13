#/usr/bin/r

#Loading Libraries

library(ggplot2);
library(cowplot);
theme_set(theme_cowplot());
library(ggpubr);
library(geomtextpath);

library(dplyr)

#Own Libraries
library(AnaMTG);

#Setting path
current_directoy = getwd();
setwd("../../")


# Read the data
data.df <- read.table(
  "Scripts/Python/020_analysis_draws_dual_lands_MC/020_Saved_run_for_plotting__2_colors.txt",
  header = TRUE,
  sep = "\t"
)

data.df = data.df[which(data.df$Color_Counts!="Mulligan"),];


digested_2_color_duals.df <- data.df %>%
  group_by(Dual_land) %>%
  mutate(
    dual_sum = sum(Color_Counts_during_trials)
  ) %>%
  slice_max(
    order_by = Color_Counts_during_trials,
    n = 1,
    with_ties = FALSE
  ) %>%
  mutate(
    proportion = Color_Counts_during_trials / dual_sum
  ) %>%
  ungroup()


# Read the data
data.df <- read.table(
  "Scripts/Python/020_analysis_draws_dual_lands_MC/020_Saved_run_for_plotting__3_colors.txt",
  header = TRUE,
  sep = "\t"
)

data.df = data.df[which(data.df$Color_Counts!="Mulligan"),];


digested_3_color_duals.df <- data.df %>%
  group_by(Dual_land) %>%
  mutate(
    dual_sum = sum(Color_Counts_during_trials)
  ) %>%
  slice_max(
    order_by = Color_Counts,
    n = 1,
    with_ties = FALSE
  ) %>%
  mutate(
    proportion = Color_Counts_during_trials / dual_sum
  ) %>%
  ungroup()
digested_3_color_duals.df;

# Read the data
data.df <- read.table(
  "Scripts/Python/020_analysis_draws_dual_lands_MC/020_Saved_run_for_plotting__4_colors.txt",
  header = TRUE,
  sep = "\t"
)

data.df = data.df[which(data.df$Color_Counts!="Mulligan"),];


digested_4_color_duals.df <- data.df %>%
  group_by(Dual_land) %>%
  mutate(
    dual_sum = sum(Color_Counts_during_trials)
  ) %>%
  slice_max(
    order_by = Color_Counts,
    n = 1,
    with_ties = FALSE
  ) %>%
  mutate(
    proportion = Color_Counts_during_trials / dual_sum
  ) %>%
  ungroup()
digested_4_color_duals.df;


# Read the data
data.df <- read.table(
  "Scripts/Python/020_analysis_draws_dual_lands_MC/020_Saved_run_for_plotting__5_colors.txt",
  header = TRUE,
  sep = "\t"
)

data.df = data.df[which(data.df$Color_Counts!="Mulligan"),];


digested_5_color_duals.df <- data.df %>%
  group_by(Dual_land) %>%
  mutate(
    dual_sum = sum(Color_Counts_during_trials)
  ) %>%
  slice_max(
    order_by = Color_Counts,
    n = 1,
    with_ties = FALSE
  ) %>%
  mutate(
    proportion = Color_Counts_during_trials / dual_sum
  ) %>%
  ungroup()
digested_5_color_duals.df;


#Analysis

#4 color
average_change_4_color <- mean(diff(digested_4_color_duals.df$proportion  ))
average_change_4_color;


average_change_4_color_first_10 <- mean(diff(digested_4_color_duals.df$proportion[1:10]  ))
average_change_4_color_first_10;

diffs_4_color = diff(digested_4_color_duals.df$proportion  );
diffs_4_color_perc = diffs_4_color[-1] / diffs_4_color[-length(diffs_4_color)];
diffs_4_color_perc;

#5 color
average_change_5_color <- mean(diff(digested_5_color_duals.df$proportion  ))
average_change_5_color;


average_change_5_color_first_10 <- mean(diff(digested_5_color_duals.df$proportion[1:10]  ))
average_change_5_color_first_10;

diffs_5_color = diff(digested_5_color_duals.df$proportion  );
diffs_5_color_perc = diffs_5_color[-1] / diffs_5_color[-length(diffs_5_color)];
diffs_5_color_perc;



