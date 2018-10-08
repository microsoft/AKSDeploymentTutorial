# ---
# jupyter:
#   anaconda-cloud: {}
#   jupytext_format_version: '1.3'
#   jupytext_formats: py:light
#   kernelspec:
#     display_name: Python [conda env:AKSDeploymentPytorch]
#     language: python
#     name: conda-env-AKSDeploymentPytorch-py
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
# ---

# ### Deploy Web App on Azure Container Services (AKS)
# In this notebook, we will set up an Azure Container Service which will be managed by Kubernetes. We will then take the Docker image we created earlier that contains our app and deploy it to the AKS cluster. Then, we will check everything is working by sending an image to it and getting it scored.
#     
# The process is split into the following steps:
# * [Define our resource names](#section1)
# * [Login to Azure](#section2)
# * [Create resource group and create AKS](#section3)
# * [Connect to AKS](#section4)
# * [Deploy our app](#section5)
#
# This guide assumes is designed to be run on linux and requires that the Azure CLI is installed.

import json
from testing_utilities import write_json_to_file
from dotenv import set_key, get_key, find_dotenv

# <a id='section1'></a>
# ## Setup
# Below are the various name definitions for the resources needed to setup AKS.

env_path = find_dotenv(raise_error_if_not_found=True)

set_key(env_path, 'selected_subscription', 'Team Danielle Internal')
set_key(env_path, 'resource_group', 'msaksrg')
set_key(env_path, 'aks_name', 'msaks')
set_key(env_path, 'location', 'eastus')

image_name = get_key(env_path, 'docker_login') + '/' +get_key(env_path, 'image_repo') 

# <a id='section2'></a>
# ## Azure account login
# If you are not already logged in to an Azure account, the command below will initiate a login. It will pop up a browser where you can select an Azure account.

# + {"active": "ipynb"}
# list=`az account list -o table`
# if [ "$list" == '[]' ] || [ "$list" == '' ]; then 
#   az login -o table
# else
#   az account list -o table 
# fi
# -

!az account set --subscription "{get_key(env_path, 'selected_subscription')}"

!az account show

!az provider register -n Microsoft.ContainerService

!az provider show -n Microsoft.ContainerService

# <a id='section3'></a>
# ## Create resource group and create AKS

# ### Create resource group
# Azure encourages the use of groups to organise all the Azure components you deploy. That way it is easier to find them but also we can deleted a number of resources simply by deleting the group.

!az group create --name {get_key(env_path, 'resource_group')} \
                 --location {get_key(env_path, 'location')}

# Below, we create the AKS cluster in the resource group we created earlier. This can take up to 15 minutes.

!az aks create --resource-group {get_key(env_path, 'resource_group')}  \
               --name {get_key(env_path, 'aks_name')} \
               --node-count 1 \
               --generate-ssh-keys \
               -s Standard_NC6

# ### Install kubectl CLI
#
# To connect to the Kubernetes cluster, we will use kubectl, the Kubernetes command-line client. To install, run the following:

!sudo az aks install-cli

# <a id='section4'></a>
# ## Connect to AKS cluster
#
# To configure kubectl to connect to the Kubernetes cluster, run the following command:

!az aks get-credentials --resource-group {get_key(env_path, 'resource_group')}\
                        --name {get_key(env_path, 'aks_name')}

# Let's verify connection by listing the nodes.

!kubectl get nodes

# Let's check the pods on our cluster.

!kubectl get pods --all-namespaces

# <a id='section5'></a>
# ## Deploy application
#
# Below we define our Kubernetes manifest file for our service and load balancer. Note that we have to specify the volume mounts to the drivers that are located on the node.
#

# +
app_template = {
  "apiVersion": "apps/v1beta1",
  "kind": "Deployment",
  "metadata": {
      "name": "azure-dl"
  },
  "spec":{
      "replicas":1,
      "template":{
          "metadata":{
              "labels":{
                  "app":"azure-dl"
              }
          },
          "spec":{
              "containers":[
                  {
                      "name": "azure-dl",
                      "image": image_name,
                      "env":[
                          {
                              "name": "LD_LIBRARY_PATH",
                              "value": "$LD_LIBRARY_PATH:/usr/local/nvidia/lib64:/opt/conda/envs/py3.6/lib"
                          }
                      ],
                      "ports":[
                          {
                              "containerPort":80,
                              "name":"model"
                          }
                      ],
                      "volumeMounts":[
                          {
                            "mountPath": "/usr/local/nvidia",
                            "name": "nvidia"
                          }
                      ],
                      "resources":{
                           "requests":{
                               "alpha.kubernetes.io/nvidia-gpu": 1
                           },
                           "limits":{
                               "alpha.kubernetes.io/nvidia-gpu": 1
                           }
                       }  
                  }
              ],
              "volumes":[
                  {
                      "name": "nvidia",
                      "hostPath":{
                          "path":"/usr/local/nvidia"
                      },
                  },
              ]
          }
      }
  }
}

service_temp = {
  "apiVersion": "v1",
  "kind": "Service",
  "metadata": {
      "name": "azure-dl"
  },
  "spec":{
      "type": "LoadBalancer",
      "ports":[
          {
              "port":80
          }
      ],
      "selector":{
            "app":"azure-dl"
      }
   }
}
# -

write_json_to_file(app_template, 'az-dl.json') # We write the service template to the json file

write_json_to_file(service_temp, 'az-dl.json', mode='a') # We add the loadbelanacer template to the json file

# Let's check the manifest created.

!cat az-dl.json

# Next, we will use kubectl create command to deploy our application.

!kubectl create -f az-dl.json

# Let's check if the pod is deployed.

!kubectl get pods --all-namespaces

# If anything goes wrong you can use the commands below to observe the events on the node as well as review the logs.

!kubectl get events

pod_json = !kubectl get pods -o json
pod_dict = json.loads(''.join(pod_json))
!kubectl logs {pod_dict['items'][0]['metadata']['name']}

# It can take a few minutes for the service to populate the EXTERNAL-IP field. This will be the IP you use to call the service. You can also specify an IP to use please see the AKS documentation for further details.

!kubectl get service azure-dl

# Next, we will [test our web application](05_TestWebApp.ipynb) deployed on AKS. 
