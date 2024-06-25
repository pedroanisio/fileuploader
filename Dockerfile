# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Copy and run the script to generate the .env file
COPY generate_secret.sh .
RUN chmod +x generate_secret.sh && ./generate_secret.sh

# Make port 3010 available to the world outside this container
EXPOSE 3010

# Run app.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3010", "app:app"]
