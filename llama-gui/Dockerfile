# syntax=docker/dockerfile:1
FROM node:18-bullseye

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ENV PORT=3000
EXPOSE 3000

CMD ["npm", "run", "start:react"]
