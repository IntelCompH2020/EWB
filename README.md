# Intelcomp's Evaluation Workbench (EWB) Python Dockers

## Overview

The Evaluation Workbench Python Dockers form a multi-container application that includes essential components such as the Solr cluster, RESTful API, and inference service. These Docker containers enable data ingestion, information retrieval, and topic and class inference capabilities within the Evaluation Workbench.

![Python Dockers](https://github.com/IntelCompH2020/EWB/blob/main/static/Images/ewb-python-dockers.png)

## Requirements

- **Python requirements files** ([``ewb-restapi requirements``](https://github.com/IntelCompH2020/EWB/blob/main/restapi/requirements.txt) and [``inferencer requirements``](https://github.com/IntelCompH2020/EWB/blob/main/inferencer/requirements.txt)).

   > *Note that the requirements are directly installed in their respective services at the building-up time.*

- **Mallet package:** It needs to be downloaded from [``Mallet’s official website``](https://github.com/IntelCompH2020/EWB/blob/main/restapi/requirements.txt) into the following route: ```“/inferencer/src/core/models/mallet-2.0.8”```.

## Docker Compose Script

The Docker Compose script sets up an environment for the EWB's RESTful API server that relies on a Solr search engine for data storage and retrieval.

### Description of services

The script builts a multi-container application consising of five services, all of them using the ``ewb-net`` network.

1. ``restapi (ewb-restapi)`` - This service is responsible for running the EWB's RESTful API server. It is built using the Dockerfile located in the ``restapi`` directory. It depends on the Solr service and requires access to the volume mounted at ``"./data/source"``,``"./data/inference"`` and ``"./ewb_config"``. These volumes are used to access any data needed from the ITMT (i.e., the project folder in which the topic models are saved) and to provide the results obtained through the EWB or generated through the Inference service. In addition, the last one host some configuration variables.

2. ``solr (ewb-solr)`` - This service runs the Solr search engine. It uses the official Solr image from Docker Hub and depends on the zoo service. The service mounts several volumes, including:

   - the **Solr data directory**, for giving persistence.
   - the **custom Solr plugin** ([``solr-ewb-jensen-shanon-distance-plugin``](https://github.com/Nemesis1303/solr-ewb-jensen-shanon-distance-plugin)) for using the Jensen–Shannon divergence as vector scoring method.
   - the **Solr configuration directory**, to access the specifc EWB's Solr schemas

3. ``zoo (ewb-zoo)`` - This service runs Zookeeper, which is required by Solr to coordinate cluster nodes. It uses the official zookeeper image. The service mounts two volumes for data and logs.

4. ``solr-config (ewb-solr-config)`` - This service is responsible for configuring Solr. It is built using the Dockerfile located in the ``"solr_config"`` directory. The service uses the ewb-net network and depends on the solr and zoo services. It mounts the Docker socket and the bash_scripts directory, which includes a script for initializing the Solr configuration for the EWB.

5. ``inferencer (ewb-inferencer)``- This service hosts a Topic Model Inferencer. It is built using the Dockerfile located at the ``"inferencer"`` directory and requires acces to the volumes mounted at ``"./data/source"``, ``"./data/inference"`` and ``"./ewb_config"``. 