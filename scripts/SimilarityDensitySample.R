setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

library(readr)
library(ggplot2)
library(tidyr)
library(tibble)
library(dplyr)

dat <- read_csv("../output/faceMatrix - Combined.csv")

plotDat <- dat %>%
  gather(key, value) %>%
  filter(key != "X1", key %in% sample(colnames(dat)[-1], 9)) %>%
  mutate(value = as.numeric(value))

p1 <- ggplot(plotDat, aes(x = value)) + 
  geom_density(fill = "lightblue") +
  theme_bw() + 
  facet_wrap(~ key) +
  expand_limits(x = c(0, 100))

ggsave("plots/SimilarityDensitySample.png", width = 7, height = 7)
       