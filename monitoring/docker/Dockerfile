# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /data

# Copy the requirements file into the container and install dependencies
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the script source code into the container
COPY expeca-exporter.py /app

# Specify the command to run when the container starts
CMD ["python", "expeca-exporter.py"]

# Build the image with
#     docker build -t expeca-exporter .

# Upload the image to Docker hub
#     docker image tag expeca-exporter sman4ever/expeca-exporter:latest
#     docker image push sman4ever/expeca-exporter:latest

# Run the container with
#     docker run -t -d -v /home/expeca/exporter:/data -p 9000:9000 --name expeca_exporter sman4ever/expeca-exporter
#     docker run -d -v /home/expeca/exporter:/data -p 9000:9000 --name expeca_exporter sman4ever/expeca-exporter
#     docker run -d --restart always -v /home/expeca/exporter:/data -p 9000:9000 --name expeca_exporter sman4ever/expeca-exporter
