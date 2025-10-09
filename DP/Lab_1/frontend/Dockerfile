FROM node:20-slim

WORKDIR /app

COPY . /app

RUN echo "Installing http-server..." && npm install -g http-server && echo "http-server installed."

EXPOSE 3000

CMD ["sh", "-c", "echo 'Starting frontend http-server...' && http-server -p 3000"]