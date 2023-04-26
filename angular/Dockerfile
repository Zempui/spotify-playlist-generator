FROM node:20.0.0-alpine3.17
WORKDIR /app
COPY . /app
RUN apk add git #For development
RUN npm install -g @angular/cli
RUN ng build --configuration production
RUN npm install
