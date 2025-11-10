FROM node:20-alpine as frontend

ADD ./frontend /js
WORKDIR /js

RUN npm install --loglevel verbose
RUN npm config set timeout 600000
RUN NODE_OPTIONS=--max_old_space_size=4096 npm run build

FROM nginx:latest
COPY --from=frontend /js/dist/spa /usr/share/nginx/html
