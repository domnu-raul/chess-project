FROM node:20.14.0-alpine

WORKDIR /root

COPY package.json .

RUN npm install

COPY . .

EXPOSE 5173
