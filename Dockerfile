# Use official lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ ./backend/
COPY ml/ ./ml/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
# Add current directory to PYTHONPATH so backend can import ml
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
