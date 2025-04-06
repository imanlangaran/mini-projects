FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

EXPOSE 3002 # or 3003 for users service
CMD ["node", "index.js"]