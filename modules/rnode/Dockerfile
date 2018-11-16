FROM rocker/r-base

# dependencies for plumber
RUN apt-get update -qq && apt-get install -y \
  git-core \
  libssl-dev \
  libcurl4-gnutls-dev && \
  apt-get clean

# additional R packages
RUN install2.r plumber devtools

RUN R -e "devtools::install_github('qunis/ahub', 'dev', 'packages/ahubr')"

EXPOSE 8000

COPY *.R /app/
WORKDIR /app

ENTRYPOINT ["Rscript"]
CMD ["run_api.R"]
