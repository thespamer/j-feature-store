# Build stage
FROM node:18-alpine

WORKDIR /app

# Limpar cache e instalar dependências
COPY package*.json ./
RUN npm cache clean --force && \
    npm install --legacy-peer-deps

# Copiar código fonte
COPY . .

ENV NODE_ENV=development
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "start"]
