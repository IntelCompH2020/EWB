# Base image
FROM ubuntu:22.04

# Set noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install python
# Set noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends tzdata \
    python3.9 \
    python3-distutils \
    python3-pip \
    python3-apt \
    build-essential \
    gcc \
    python3-dev \
    python-is-python3

# Clean up the package cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Java
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install OpenJDK-8
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;
    
# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

WORKDIR /ewb-inferencer

COPY . .

# Download Mallet
RUN wget https://mallet.cs.umass.edu/dist/mallet-2.0.8.zip

# Extract the contents of the zip file
RUN unzip mallet-2.0.8.zip

# Remove the zip file
RUN rm mallet-2.0.8.zip

# Remove old mallet if exists
RUN rm -rf /ewb-inferencer/src/core/models/mallet-2.0.8

# Copy the Mallet's decompressed folder into the Mallet directory
RUN mv mallet-2.0.8 /ewb-inferencer/src/core/models

RUN mkdir -p /data/source
RUN mkdir -p /data/inference

# Install Python packages
RUN pip3 install --upgrade pip setuptools wheel
RUN python3 -m pip install -r requirements.txt 

EXPOSE 90

CMD ["python3", "app.py"]