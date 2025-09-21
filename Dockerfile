FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY data data
ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn","app.api:app","--host","0.0.0.0","--port","8080"]
