FROM python:3.9

RUN apt-get update

# Define timezone
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install jre
RUN apt install -y default-jre

# Install wget and unzip
RUN apt-get update && apt-get install -y wget unzip

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
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

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 90

CMD ["python3", "app.py"]