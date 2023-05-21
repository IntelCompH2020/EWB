# Ubuntu version: 20.04, 18.04
ARG VARIANT=20.04
FROM ubuntu:${VARIANT}

# Install python
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-distutils \
    python3-pip \
    python3-apt

RUN apt install python-is-python3

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

WORKDIR /inferencer

COPY . .

RUN mkdir -p /data/source
RUN mkdir -p /data/inference

RUN python3 -m pip install -r requirements.txt 

EXPOSE 90

CMD ["python3", "app.py"]