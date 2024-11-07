# Use an official Python image as a base image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# install needed packages 
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run the Flask app
CMD ["python", "app.py"]
