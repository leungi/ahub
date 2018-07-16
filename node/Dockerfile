FROM trestletech/plumber

#COPY requirements.txt /app/
#RUN cat /app/requirements.txt | install2.r

RUN install2.r future futile.logger rredis

COPY *.R /app/
WORKDIR /app

ENTRYPOINT ["Rscript"]
CMD ["startapi.R"]
