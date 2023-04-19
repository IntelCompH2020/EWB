# Intelcomp's Evaluation Workbench (EWB)

## Docker Compose Script

The Docker Compose script sets up an environment for the EWB's RESTful API server that relies on a Solr search engine for data storage and retrieval. The script includes several services, including the RESTful API, Solr, Zookeeper, and a custom Solr configuration.

### Description of services

The script consists of four services, all of them using the ``ewb-net`` network.

1. ``restapi (ewb-restapi)`` - This service is responsible for running the EWB's RESTful API server. It is built using the Dockerfile located in the ``restapi`` directory. It depends on the Solr service and requires access to two volumes mounted at the ``./data/source`` and ``./data/results`` directories, which are mapped to the directories of the same name inside the container. These volumes are used to access any data needed from the ITMT (i.e., the project folder in which the topic models are saved) and to provide the results obtained through the EWB.

2. ``solr (ewb-solr)`` - This service runs the Solr search engine. It uses the official Solr image from Docker Hub and depends on the zoo service. The service mounts several volumes, including:

   - the **Solr data directory**, for giving persistence.
   - the **custom Solr plugin** ([``solr-ewb-jensen-shanon-distance-plugin``](https://github.com/Nemesis1303/solr-ewb-jensen-shanon-distance-plugin)) for using the Jensen–Shannon divergence as vector scoring method.
   - the **Solr configuration directory**, to access the specifc EWB's Solr schemas

3. ``zoo (ewb-zoo)`` - This service runs Zookeeper, which is required by Solr to coordinate cluster nodes. It uses the official zookeeper image. The service mounts two volumes for data and logs.

4. ``solr-config (ewb-solr-config)`` - This service is responsible for configuring Solr. It is built using the Dockerfile located in the ``solr_config`` directory. The service uses the ewb-net network and depends on the solr and zoo services. It mounts the Docker socket and the bash_scripts directory, which includes a script for initializing the Solr configuration for the EWB.