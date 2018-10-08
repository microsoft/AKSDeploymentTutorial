# ---
# jupyter:
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

# # Tear it all down
# Once you are done with your cluster you can use the following two commands to destroy it all.

from dotenv import get_key, find_dotenv

env_path = find_dotenv(raise_error_if_not_found=True)

# Once you are done with your cluster you can use the following two commands to destroy it all. First, delete the application.

!kubectl delete -f az-dl.json

# Next, you delete the AKS cluster. This step may take a few minutes.

!az aks delete -n {get_key(env_path, 'aks_name')} \
               -g {get_key(env_path, 'resource_group')} \
               -y

# Finally, you should delete the resource group. This also deletes the AKS cluster and can be used instead of the above command if the resource group is only used for this purpose.

!az group delete --name {get_key(env_path, 'resource_group')} -y
