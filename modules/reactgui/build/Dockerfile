FROM node:8.14-alpine

RUN npm install -g serve

ADD . /app/
WORKDIR /app

EXPOSE 8000

CMD serve -l 8000 