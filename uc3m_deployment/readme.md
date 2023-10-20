# UC3M DEPLOYMENT

For UC3M internal deployment, minimal changes have been carried out into the docker-compose files so the external volumes are mounted into a directory that is accessible by different UC3M users.

In particular, the changes to the affected volumes performed are listed below:

1. ``tm`` and ``inferencer`` services:

    Change from:

    ```docker
    - ./data/source:/data/source
    - ./data/inference:/data/inference
    ```

    To:

    ```docker
    - ../../data/source:/data/source
    - ../../data/inference:/data/inference
    ```

2. ``classifier`` service:

    Change from:

    ```docker
    - ./data/classifier:/data/classifier
    ```

    To:

    ```docker
    - ../../data/classifier:/data/classifier
    ```

3. ``classifier`` service:
4. ``solr-initializer`` service:
5. ``solr`` service:
6. ``zoo`` service:
7. ``solr_config`` service:
