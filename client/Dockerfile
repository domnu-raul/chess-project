FROM node:20.14.0-alpine

ENV APP_HOME /root

COPY package.json .

RUN npm install

WORKDIR $APP_HOME

COPY . $APP_HOME

EXPOSE 5173
