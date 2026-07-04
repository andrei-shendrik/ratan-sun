# сборка
FROM node:20-alpine AS builder
WORKDIR /app
# копирование package.json и установка зависимостей
COPY package*.json ./
RUN npm install
# копирование исходного кода и сборка
COPY . .
# Vite соберет оптимизированную статику в папку /app/dist
RUN npm run build

# nginx
FROM nginx:alpine
# копирование конфига nginx для SPA
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
# копирование готовых файлов react из первой стадии
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]