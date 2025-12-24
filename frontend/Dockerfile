# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build && npm prune --production

# Production stage
FROM node:20-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 8080
ENV PORT 8080
CMD ["node", "server.js"]   







# syntax = docker/dockerfile:1
# FROM node:22-alpine AS builder
# WORKDIR /app

# COPY package*.json ./
# RUN npm ci

# COPY . .
# RUN npm run build

# FROM node:22-alpine AS runner
# WORKDIR /app

# COPY --from=builder /app ./

# EXPOSE 3000
# CMD ["npm", "start"]   