# Use an official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --without dev

# Copy the application code
COPY . .

# Expose the backend port (from .env)
EXPOSE 8000

# Run the FastAPI application
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
