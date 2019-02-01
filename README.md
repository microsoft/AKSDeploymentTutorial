# This repo is no longer actively maintained, please see newer version available using Azure Machine Learning [here](https://github.com/Microsoft/AKSDeploymentTutorial_AML).

### Authors: Mathew Salvaris and Fidan Boylu Uz

# Deploy Deep Learning CNN on Kubernetes Cluster with GPUs
## Overview
In this repository there are a number of tutorials in Jupyter notebooks that have step-by-step instructions on how to deploy a pretrained deep learning model on a GPU enabled Kubernetes cluster. The tutorials cover how to deploy models from the following deep learning frameworks:
* [TensorFlow](Tensorflow)
* [Keras (TensorFlow backend)](Keras_Tensorflow)
* [Pytorch](Pytorch)

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
 
## Design
![alt text](static/Design.png "Design")

The application we will develop is a simple image classification service, where we will submit an image and get back what class the image belongs to. The application flow for the deep learning model is as follows:
1)	The client sends a HTTP POST request with the encoded image data.
2)	The Flask app extracts the image from the request.
3)	The image is then appropriately preprocessed and sent to the model for scoring.
4)	The scoring result is then piped into a JSON object and returned to the client.

If you already have a Docker image that you would like to deploy you can skip the first four notebooks.

**NOTE**: The tutorial goes through step by step how to deploy a deep learning model on Azure; it **does** **not** include enterprise best practices such as securing the endpoints and setting up remote logging etc. 

**Deploying with GPUS:** For a detailed comparison of the deployments of various deep learning models, see the blog post [here](https://azure.microsoft.com/en-us/blog/gpus-vs-cpus-for-deployment-of-deep-learning-models/) which provides evidence that, at least in the scenarios tested, GPUs provide better throughput and stability at a lower cost.

## Prerequisites
* Linux(Ubuntu). The tutorial was developed on an Azure Linux DSVM
* [Docker installed](https://docs.docker.com/v17.12/install/linux/docker-ee/ubuntu/). NOTE: Even with docker installed you may need to set it up so that you don't require sudo to execute docker commands see ["Manage Docker as a non-root user"](https://docs.docker.com/install/linux/linux-postinstall/) 
* [Dockerhub account](https://hub.docker.com/)
* Port 9999 open: Jupyter notebook will use port 9999 so please ensure that it is open. For instructions on how to do that on Azure see [here](https://blogs.msdn.microsoft.com/pkirchner/2016/02/02/allow-incoming-web-traffic-to-web-server-in-azure-vm/)

## Setup
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

## Steps
After following the setup instructions above, run the Jupyter notebooks in order. The same basic steps are followed for each deep learning framework.

## Cleaning up
To remove the conda environment created see [here](https://conda.io/docs/commands/env/conda-env-remove.html). The last Jupyter notebook within each folder also gives details on deleting Azure resources associated with this repo.

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

