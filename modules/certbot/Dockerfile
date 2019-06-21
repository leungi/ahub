# Use an official Python runtime as a parent image
FROM python:3.7.1-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN apt-get update && apt-get install -y openssl
# Make port 8000 available to the world outside this container
EXPOSE 8000 80

# Copy the current directory contents into the container at /app
ADD config.yaml /app
ADD *.py /app/


# Run app.py when the container launches
CMD ["python", "app.py"]