Modeling high-resolution weather effects on MLB run totals
================

## Developer setup

## R

  - To run the R scripts in this project, first download RStudio. Then,
    clone this repo and open `mlb-weather.Rproj`. This will trigger a
    script (`renv/activate.R`) which installs `renv`, a project-local
    dependency manager. All needed packages and their versions are
    listed in the `renv.lock` file. `renv` will begin installing these
    packages automatically. You can read more about `renv`
    [here](https://rstudio.github.io/renv/articles/renv.html).

## Python

  - First, make a `venv` for this project, and name it `env`:

<!-- end list -->

    cd /path/to/mlb-weather/
    python3 -m venv env

  - Activate it:

<!-- end list -->

    source env/bin/activate

  - Then, install needed libraries:

<!-- end list -->

    pip3 install -r requirements.txt

## Storing your NCDC Climate Data Online API Token

  - To generate your token, go here:
    <https://www.ncdc.noaa.gov/cdo-web/token>

### R

  - First, store your token in your `.Renviron` file, either by running:

<!-- end list -->

    echo NCDC_TOKEN=[your token] >> /path/to/your/.Renviron

or

    Sys.setenv(NCDC_TOKEN="[your token]")

  - Then, restart R and read your `.Renviron` by running
    `readRenviron("/path/to/your/.Renviron")`. You will only need to do
    this once.

### Python

  - Store your token in your `env/bin/activate` script:

<!-- end list -->

    echo export NCDC_TOKEN=[your token] >> env/bin/activate

  - Restart the env, and your token will be loaded as an environment
    variable:

<!-- end list -->

    source env/bin/activate
    echo $NCDC_TOKEN
