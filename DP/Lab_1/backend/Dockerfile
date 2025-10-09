FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN echo "Installing Python dependencies..." \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && echo "Dependencies installed."

COPY . /app
RUN echo "Backend files copied."

EXPOSE 8000

CMD ["sh", "-c", "echo 'Starting FastAPI backend...' && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1"]