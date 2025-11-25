FROM node:20-bookworm as frontend

ADD . /js
WORKDIR /js
RUN npm install -g @quasar/cli yarn
RUN npm install
RUN NODE_OPTIONS=--max_old_space_size=8192 npm run build

FROM nginx:latest
COPY --from=frontend /js/dist/spa /usr/share/nginx/html
