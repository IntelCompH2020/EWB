# HOW TO GENERATE SPHINX DOCS

To generate Sphinx documentation, follow these steps from the ``doc`` directory:

1. Run the following commands to generate the initial documentation for your project modules:

    ```bash
   sphinx-apidoc -o doc ewb-classifier/
   sphinx-apidoc -o doc ewb-tm/
   sphinx-apidoc -o doc ewb-inferencer/
    ```

2. Then modify the generated ``.rst`` files as desired.

No more actions are needed. HTML files are generated automatically through the Github actions. The deployment branch and other configuration settings on this process can be upadted via the ``.github/workflows/documentation.yaml`` file.