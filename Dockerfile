# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create the directory for secrets to be mounted into
RUN mkdir -p /app/secure

# Copy the rest of the application's source code
COPY . .

# Define the command to run your app
CMD ["python", "main.py"]