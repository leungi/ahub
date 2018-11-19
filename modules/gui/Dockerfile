FROM rocker/tidyverse

# install R packages
RUN install2.r \
    shiny \
    shinyjs \
    shinydashboard \
    DT \
    rapiclient && \
    R -e 'devtools::install_github("nik01010/dashboardthemes")'

# install shiny server
RUN apt-get update && apt-get install -y \
    sudo \
    gdebi-core \
    pandoc \
    pandoc-citeproc \
    libcurl4-gnutls-dev \
    libcairo2-dev \
    libxt-dev && \
    wget --no-verbose https://download3.rstudio.org/ubuntu-14.04/x86_64/VERSION -O "version.txt" && \
    VERSION=$(cat version.txt)  && \
    wget --no-verbose "https://download3.rstudio.org/ubuntu-14.04/x86_64/shiny-server-$VERSION-amd64.deb" -O ss-latest.deb && \
    gdebi -n ss-latest.deb && \
    rm -f version.txt ss-latest.deb

ADD . /srv/shiny-server
WORKDIR /srv/shiny-server

#ADD . /app
#WORKDIR /app

EXPOSE 3838

CMD shiny-server
#CMD R -e "shiny::runApp(host='0.0.0.0', port=3838)"