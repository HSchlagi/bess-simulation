FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp ./mcp
COPY app ./app
COPY .env.example /app/.env.example
CMD ["python", "mcp/server.py"]
