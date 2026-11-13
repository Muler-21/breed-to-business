# Module 1 in R: alpha-lattice design and teff multi-environment analysis
# Packages: install.packages(c("agricolae", "lme4", "lmerTest", "metan", "dplyr"))
# NOTE: written to mirror run.py; run it on your machine and report any error.

library(agricolae); library(lme4); library(lmerTest); library(metan); library(dplyr)

## 1. Design: 60 entries, blocks of 6, 3 replicates (one randomisation per site-year)
entries <- c(sprintf("TF%02d", 1:58), "Check-Quncho", "Check-Tsedey")
des <- design.alpha(trt = entries, k = 6, r = 3, serie = 2, seed = 2024)
head(des$book)                       # plots, replication, block, entry
write.csv(des$book, "fieldbook_R_example.csv", row.names = FALSE)

## 2. Data: the CSV made by run.py (or your own with the same columns)
d <- read.csv("../data/teff_met_simulated.csv")
d <- d %>% mutate(across(c(env, location, year, rep, block, entry), as.factor),
                  blk = interaction(env, rep, block))

## 3. One site: alpha-lattice ANOVA (genotype adjusted for blocks)
one <- droplevels(subset(d, env == levels(d$env)[1]))
m1 <- lm(yield_t_ha ~ rep + rep:block + entry, data = one)
anova(m1)                                       # sequential: entry is adjusted for blocks
m1r <- lmer(yield_t_ha ~ entry + rep + (1 | rep:block), data = one)
emm <- emmeans::emmeans(m1r, "entry")          # adjusted means

## 4. Combined: random locations and years, fixed genotypes
m2 <- lmer(yield_t_ha ~ entry + (1 | year) + (1 | location) + (1 | location:year) +
             (1 | location:year:rep) + (1 | blk) +
             (1 | entry:location) + (1 | entry:year), data = d)
summary(m2)$varcor                              # variance components
anova(m2)                                       # test of genotypes

## 5. Genotype-by-environment means, AMMI, GGE, stability (metan)
ge <- d %>% group_by(env, entry, rep) %>% summarise(GY = mean(yield_t_ha), .groups = "drop")
am <- performs_ammi(ge, env, entry, rep, GY)
plot_scores(am, type = 1)                       # AMMI1
gg <- gge(ge, env, entry, GY)
plot(gg, type = 3)                              # which-won-where
st <- ge_reg(ge, env, entry, rep, GY)          # Eberhart-Russell / Finlay-Wilkinson
ammi_indexes(am)                                # ASV and yield-stability index
