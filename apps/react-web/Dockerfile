# сборка
FROM node:20-alpine as builder
WORKDIR /app
# копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm install
# копируем весь исходный код и собираем
COPY . .
# Vite соберет оптимизированную статику в папку /app/dist
RUN npm run build

# nginx
FROM nginx:alpine
# копируем конфиг Nginx для SPA
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
# копируем готовые файлы React из первой стадии
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]