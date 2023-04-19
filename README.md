# Intelcomp's Evaluation Workbench (EWB)

## Docker Compose Script

The Docker Compose script sets up an environment for the EWB's RESTful API server that relies on a Solr search engine for data storage and retrieval. The script includes several services, including the RESTful API, Solr, Zookeeper, and a custom Solr configuration.

### Description of services

The script consists of four services:

1. ``restapi (ewb-restapi)`` - This service is responsible for running the EWB's RESTful API server. It is built using the Dockerfile located in the ``restapi`` directory. It listens on port 80 and requires the SOLR_URL environment variable to be set to the URL of the Solr server. The service depends on the solr service and uses the ewb-net network. The service requires access to a volume mounted at the ``./data`` directory, which is mapped to the ``/data/source``directory inside the container. This volume is used to access any data needed from the ITMT (i.e., the project folder in which the topic models are saved).

2. ``solr (ewb-solr)`` - This service runs the Solr search engine. It uses the official solr image from Docker Hub and listens on port 8983. It also uses the ewb-net network and depends on the zoo service. The service mounts several volumes, including:

   - the **Solr data directory**, for giving persistence.
   - the **custom Solr plugin** ([``solr-ewb-jensen-shanon-distance-plugin``](https://github.com/Nemesis1303/solr-ewb-jensen-shanon-distance-plugin)) for using the Jensen–Shannon divergence as vector scoring method.
   - the **Solr configuration directory**, to access the specifc EWB's Solr schemas

3. ``zoo (ewb-zoo)`` - This service runs Zookeeper, which is required by Solr to coordinate cluster nodes. It uses the official zookeeper image and listens on ports 2180 and 2181. The service mounts two volumes for data and logs and uses the ewb-net network.

4. ``solr-config (ewb-solr-config)`` - This service is responsible for configuring Solr. It is built using the Dockerfile located in the ``solr_config`` directory. The service uses the ewb-net network and depends on the solr and zoo services. It mounts the Docker socket and the bash_scripts directory, which includes a script for initializing the Solr configuration for the EWB.