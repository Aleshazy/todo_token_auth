FROM python:3.12-slim

# Working directory inside container.
WORKDIR /app

# Install Python dependencies first (better build cache).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code.
COPY . .

EXPOSE 8000

# Start API server.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]