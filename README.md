### Authors: Mathew Salvaris and Fidan Boylu Uz

# Deploy Deep Learning CNN on Kubernetes Cluster with GPUs
## Overview
In this repository there are a number of tutorials in Jupyter notebooks that have step-by-step instructions on how to deploy a pretrained deep learning model on a GPU enabled Kubernetes cluster. The tutorials cover how to deploy models from the following deep learning frameworks:
* [TensorFlow](Tensorflow)
* [Keras (TensorFlow backend)](Keras_Tensorflow)
* Pytorch (Coming soon)

![alt text](static/example.png "Example Classification")
 
 For each framework, we go through the following steps:
 * Model development where we load the pretrained model and test it by using it to score images
 * Developing the interface our Flask app will use to load and call the model
 * Building the Docker Image with our Flask REST API and model
 * Testing our Docker image before deployment
 * Creating our Kubernetes cluster and deploying our application to it
 * Testing the deployed model
 * Testing the throughput of our model
 * Cleaning up resources
 
The application we will develop is a simple image classification service, where we will submit an image and get back what class the image belongs to. 

If you already have a Docker image that you would like to deploy you can skip the first four notebooks.

**NOTE**: The tutorial goes through step by step how to deploy a deep learning model on Azure it **does** **not** include enterprise best practices such as securing the endpoints and setting up remote logging etc. 

## Prerequisites
* Linux(Ubuntu). The tutorial was developed on an Azure Linux DSVM
* [Docker installed](https://docs.docker.com/v17.12/install/linux/docker-ee/ubuntu/). NOTE: Even with docker installed you may need to set it up so that you don't require sudo to execute docker commands see ["Manage Docker as a non-root user"](https://docs.docker.com/install/linux/linux-postinstall/) 
* [Dockerhub account](https://hub.docker.com/)
* Port 9999 open: Jupyter notebook will use port 9999 so please ensure that it is open. For instructions on how to do that on Azure see [here](https://blogs.msdn.microsoft.com/pkirchner/2016/02/02/allow-incoming-web-traffic-to-web-server-in-azure-vm/)

## Setting Up
1. Clone the repo:
```bash
git clone <repo web URL>
```
2. Login to Docker with your username and password.
```bash
docker login
```
3. Go to the framework folder you would like to run the notebooks for.
4. Create a conda environment:
 ```bash
 conda env create -f environment.yml
 ```
5.  Activate the environment:
 ```bash 
 source activate <environment name>
 ```
6. Run:
```bash
jupyter notebook
```
7. Start the first notebook and make sure the kernel corresponding to the above environment is selected.

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

