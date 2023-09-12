# Intelcomp's Evaluation Workbench (EWB) API Dockers

- [Intelcomp's Evaluation Workbench (EWB) API Dockers](#intelcomps-evaluation-workbench-ewb-api-dockers)
  - [Overview](#overview)
  - [Main components](#main-components)
    - [Topic Modeling Service](#topic-modeling-service)
    - [Inference Service](#inference-service)
    - [Classification Service](#classification-service)
  - [Requirements](#requirements)
  - [Sample data to start using the EWB API Dockers](#sample-data-to-start-using-the-ewb-api-dockers)

## Overview

The Evaluation Workbench (EWB) API Dockers comprise a multi-container application that includes essential components like the Solr cluster and REST APIs for Topic Modeling, Inference, and Classification services. This multi-container application is orchestrated using a docker-compose script, connecting all services through the `ewb-net` network.

![Python Dockers](https://github.com/IntelCompH2020/EWB/blob/development/static/Images/ewb-architecture2.png)

## Main components

### Topic Modeling Service

This service comprises a RESTful API that utilizes the Solr search engine for data storage and retrieval. It enables the indexing of logical corpora and associated topic models, formatted according to the specifications provided by the [``topicmodeler``](https://github.com/IntelCompH2020/topicmodeler). Additionally, it facilitates information retrieval through a set of queries.

![EWB's TM Api](https://github.com/IntelCompH2020/EWB/blob/development/static/Images/tm_api.png)

This system relies on the following services:

1. **ewb-tm**: This service hosts the Topic Modeling's RESTful API server. It is constructed using the Dockerfile located in the ``ewb-tm`` directory. It has dependencies on the Solr service and requires access to the following mounted volumes: ``./data/source``, ``./data/inference``, and ``./ewb_config``. These volumes are crucial for accessing necessary data from the ITMT (the project folder containing the topic models) and for delivering results obtained through the EWB or generated via the Inference service. The ``ewb_config`` volume also houses some important configuration variables.

2. **ewb-solr**: This service operates the Solr search engine. It employs the official Solr image from Docker Hub and relies on the zoo service. The service mounts several volumes, including:

   - The **Solr data directory** (``./db/data/solr:/var/solr``) for data persistence.
   - Two **custom Solr plugins**:
     - [solr-ewb-jensen-shanon-distance-plugin](https://github.com/Nemesis1303/solr-ewb-jensen-shanon-distance-plugin) for utilizing the Jensen–Shannon divergence as a vector scoring method.
     - [solr-ewb-jensen-sims](https://github.com/IntelCompH2020/solr-ewb-sims) for retrieving documents with similarities within a specified range.
   - The **Solr configuration directory** (``./solr_config:/opt/solr/server/solr``) to access the specific Solr schemas for EWB.

3. **ewb-solr-initializer**: This service is temporary and serves the sole purpose of initializing the mounted volume ``/db/data`` with the necessary permissions required by Solr.

4. **ewb-zoo**: This service runs Zookeeper, which is essential for Solr to coordinate cluster nodes. It employs the official zookeeper image and mounts two volumes for data and logs.

5. **ewb-solr-config**: This service handles Solr configuration. It is constructed using the Dockerfile located in the ``solr_config`` directory. This service has dependencies on the Solr and zoo services and mounts the Docker socket and the ``bash_scripts`` directory, which contains a script for initializing the Solr configuration for EWB.

### Inference Service

This service serves as a Topic Model Inferencer, constructed using the Dockerfile found in the ``ewb-inferencer`` directory. It relies on access to mounted volumes at ``./data/source``, ``./data/inference``, and ``./ewb_config``.

![EWB's TM Api](https://github.com/IntelCompH2020/EWB/blob/development/static/Images/inferencer_api.png)

Its primary purpose is to be used internally by the Topic Modeling Service, although it can also function as a standalone component.

### Classification Service

This service serves as an inference system for hierarchical classification, built on top of the [``clf-inference-intelcomp``](https://pypi.org/project/clf-inference-intelcomp/) library, that allows to classify texts based on a given hierarchy of language models. It relies on access to mounted volumes at ``./data/classifier`` and ``./ewb_config``.

![EWB's Classifier Api](https://github.com/IntelCompH2020/EWB/blob/development/static/Images/classifier_api.png)

## Requirements

**Python requirements files** ([``ewb-tm``](https://github.com/IntelCompH2020/EWB/blob/main/restapi/requirements.txt), [``ewb-inferencer``](https://github.com/IntelCompH2020/EWB/blob/main/inferencer/requirements.txt) and [``ewb-classifier``](https://github.com/IntelCompH2020/EWB/blob/development/classifier/requirements.txt)).

> *Note that the requirements are directly installed in their respective services at the building-up time.*

## Sample data to start using the EWB API Dockers