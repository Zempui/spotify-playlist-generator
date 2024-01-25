FROM node:20.5.1-alpine3.18

RUN adduser -D pgen
USER pgen
WORKDIR /home/pgen

COPY --chown=pgen:pgen pgen/package.json package.json

RUN npm install

COPY --chown=pgen:pgen pgen .

RUN npm run build

CMD ["npm", "start"]