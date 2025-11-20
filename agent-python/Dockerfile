# Use an official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your backend will run on
EXPOSE 8000

# Run Alembic migrations before starting the backend
CMD ["sh", "-c", "alembic upgrade head && python agent.py start"]