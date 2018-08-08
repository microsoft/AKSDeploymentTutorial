
# Deploy ResNet 152  model on GPU enaled Kubernetes cluster using Keras with Tensorflow

In this folder are the tutorials for deploying a Keras model (with Tensorflow backend) on a Kubernetes cluster.

The tutorial is made up of the following notebooks:
 * [Model development](00_DevelopModel.ipynb) where we load the pretrained model and test it by using it to score images
 * [Developing the interface](01_DevelopModelDriver.ipynb) our Flask app will use to load and call the model
 * [Building the Docker Image](02_BuildImage.ipynb) with our Flask REST API and model
 * [Testing our Docker image](03_TestLocally.ipynb) before deployment
 * [Creating our Kubernetes cluster](04_DeployOnAKS.ipynb) and deploying our application to it
 * [Testing the deployed model](05_TestWebApp.ipynb)
 * [Testing the throughput](06_SpeedTestWebApp.ipynb) of our model
 * [Cleaning the resources](07_TearDown.ipynb) used

