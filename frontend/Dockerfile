# Build stage
FROM node:18-alpine

WORKDIR /app

# Instalar dependências em duas etapas
COPY package*.json ./

# Primeira etapa: instalar ajv explicitamente
RUN npm install ajv@8.12.0

# Segunda etapa: instalar o resto das dependências
RUN npm install --legacy-peer-deps

# Copiar código fonte
COPY . .

ENV NODE_ENV=development
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "start"]
