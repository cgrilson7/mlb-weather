# Import data
library(lubridate)
odds <- readr::read_csv("input/odds.csv",
                 col_types = cols(start_dt = col_datetime(format = "%Y-%m-%d %H:%M:%S%z"))) %>%
  arrange(start_dt, away) %>%
  dplyr::mutate(game_id = row_number(),
         year = year(start_dt),
         hour = round_date(start_dt, "hour"), # could do floor_date 
         hour_idx = 0,
         minute = minute(start_dt),
         total = away_score + home_score,
         over_hit = (total > over_under),
         under_hit = (total < over_under),
         push = (total == over_under))

odds_ <- list()
for(i in 1:4){
  odds_[[i]] <- odds %>%
    mutate(hour = hour + hours(i),
           hour_idx = i)
}
odds_expanded <- bind_rows(odds, bind_rows(odds_))

team_cities <- tribble(
  ~team,                 ~city, # ~from,   ~to,
#---------------------|--------|--------|-------#
"Arizona Diamondbacks", "Phoenix",
"Atlanta Braves",       "Atlanta",
"Baltimore Orioles",    "Baltimore",
"Boston Red Sox",       "Boston",
"Chicago Cubs",         "Chicago",
"Chicago White Sox",    "Chicago",
"Cincinnati Reds",      "Cincinnati",
"Cleveland Indians",    "Cleveland",
"Colorado Rockies",     "Denver",
"Detroit Tigers",       "Detroit",
"Houston Astros",       "Houston",
"Kansas City Royals",   "Kansas City",
"Los Angeles Angels",   "Los Angeles",
"Los Angeles Dodgers",  "Los Angeles",
"Miami Marlins",        "Miami",
"Milwaukee Brewers",    "Milwaukee",
"Minnesota Twins",      "Minneapolis",
"New York Mets",        "New York", 
"New York Yankees",     "New York",
"Oakland Athletics",    "San Francisco", # TODO:for sake of this problem (will change for future work)
"Philadelphia Phillies","Philadelphia",
"Pittsburgh Pirates",   "Pittsburgh",
"San Diego Padres",     "San Diego",
"San Francisco Giants", "San Francisco",
"Seattle Mariners",     "Seattle",
"St. Louis Cardinals",  "Saint Louis",
"Tampa Bay Rays",       "Tampa",
"Texas Rangers",        "Dallas",# TODO:
"Toronto Blue Jays",    "Toronto",
"Washington Nationals", "Washington D.C."
)
# 
# team_abbrevs <- tribble(
#   ~team,                 ~abbrev,  ~from,   ~to,
#   #---------------------|---------|-------|
#   "Arizona Diamondbacks", "ARI",   1998,   NA,
#   "Atlanta Braves",       "ATL",   1966,   NA,
#   "Baltimore Orioles",    "BAL",   1954,   NA,
#   ""
# )
#   
# team_stadiums <- tribble(
#   
# )
# 
# teams <- c("Arizona Diamondbacks")


# library(dplyr)
# odds %>%
#   # Only regular/post season games (earliest start was 3/28/2019, the 87th day of the year)
#   filter(lubridate::yday(start_dt) >= 87) %>%
#   mutate(
#     year = lubridate::year(start_dt),
#     over_hit = (total > over_under),
#     push = (total == over_under),
#     under_hit = (total < over_under)
#   ) %>%
#   group_by(year, over_hit, push, under_hit) %>%
#   summarize(n = n()) %>%
#   group_by(year) %>%
#   mutate(freq = n / sum(n)) %>%
#   select(-n) %>%
#   spread(year, freq)

wind_spd <- read_csv("input/wind_speed.csv",
                     col_types = cols(datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
                     ) %>%
  gather("city", "wind_spd",-datetime)

wind_dir <- read_csv("input/wind_direction.csv",
                     col_types = cols(datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
                     )  %>%
  gather("city", "wind_dir", -datetime)

humidity <- read_csv("input/humidity.csv",
                     col_types = cols(datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
                     ) %>%
  gather("city", "humidity", -datetime)

temperature <- read_csv("input/temperature.csv",
                        col_types = cols(datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
                        ) %>%
  gather("city", "temperature", -datetime)

pressure <- read_csv("input/pressure.csv",
                     col_types = cols(datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
                     ) %>%
  gather("city", "pressure", -datetime)

weather_desc <- read_csv("input/weather_description.csv",
                         col_types = cols(datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
                    ) %>%
  gather("city", "weather", -datetime)

weather <- bind_cols(temperature, humidity[, 3], wind_dir[, 3], wind_spd[, 3], weather_desc[, 3])

# weather <- weather %>% mutate_if(is.numeric, scale)

# write_csv(weather_all, "input/weather_long.csv")

myspread <- function(df, key, value) { # basically pivot_wider()
  # quote key
  keyq <- rlang::enquo(key)
  # break value vector into quotes
  valueq <- rlang::enquo(value)
  s <- rlang::quos(!!valueq)
  df %>% gather(variable, value, !!!s) %>%
    unite(temp, variable, !!keyq) %>%
    spread(temp, value)
}


# The MEGA JOIN -----------------------------------------------------------

odds_weather <- odds_expanded %>%
  filter((home %in% c("Chicago Cubs", "Boston Red Sox"))) %>%
  inner_join(team_cities, by = c("home" = "team")) %>%
  inner_join(weather, by = c("hour" = "datetime", "city" = "city")) %>%
  select(-hour) %>%
  myspread(hour_idx, temperature:weather)

# weather_boston <- weather %>% filter(city == "Boston")

# sox_joined <- odds_expanded %>%
#   filter(home == "Boston Red Sox",
#          !push) %>%
#   left_join(weather_boston, by = c("hour" = "datetime"))
# 
# sox_spread <- sox_joined %>%
#   select(-hour) %>%
#   myspread(hour_idx, temperature:weather)


# Join --------------------------------------------------------------------



# StackOverflow question --------------------------------------------------


## The problem:
## Asked on stackoverflow: https://stackoverflow.com/questions/57463991/how-to-join-a-data-frame-of-keys-and-datetimes-with-a-window-of-values-from-a-ti

# library(lubridate)
# library(tibble)
# 
# concerts <- tibble(venue = c("A", "A", "B", "B"),
#                     start_time = ymd_hm(c("2019-08-09 08:05",
#                                      "2019-08-10 16:07",
#                                      "2019-08-09 09:30",
#                                      "2019-08-10 17:15"))
#                    )
# 
# hourly_weather <- tibble(venue = c(rep("A", 50),
#                                    rep("B", 50)),
#                 datetime = rep(seq(ymd_hm("2019-08-09 00:00"), by = "hour", length.out = 50), 2),
#                 temperature = c(rnorm(50, 60, 5),
#                          rnorm(50, 95, 5))
#                 )
# 
# # Here is my attempt. This works and is what I'd like the result to look like, but would be very expensive for my actual dataset, because I have many more columns than just temperature.
# 
# hourly_weather_lags <- hourly_weather  %>%
#   mutate(temperature_1hr_in = lag(temperature, 1),
#          temperature_2hr_in = lag(temperature, 2),
#          temperature_3hr_in = lag(temperature, 3),
#          temperature_4hr_in = lag(temperature, 4)) %>%
#   rename(temperature_start = temperature)
# 
# weather_over_course_of_concerts <- concerts %>%
#   mutate(start_hour = floor_date(start_time, unit = "hour")) %>%
#   left_join(hourly_weather_lags, by = c("venue" = "venue", "start_hour" = "datetime"))