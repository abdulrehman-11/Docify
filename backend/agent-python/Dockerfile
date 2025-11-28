# Use an official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your backend will run on (not needed for LiveKit agent, but kept for compatibility)
EXPOSE 8000

# Run Alembic migrations before starting the agent
CMD alembic upgrade head && python agent.py start