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

# ### Test deployed web application
# This notebook pulls some images and tests them against the deployed web application.

import matplotlib.pyplot as plt
import numpy as np
from testing_utilities import img_url_to_json, to_img, plot_predictions
import requests
import json

# %matplotlib inline

# service_json = !kubectl get service azure-dl -o json
service_dict = json.loads("".join(service_json))
app_url = service_dict["status"]["loadBalancer"]["ingress"][0]["ip"]

scoring_url = "http://{}/score".format(app_url)
version_url = "http://{}/version".format(app_url)

# Quickly check the web application is working

!curl $version_url # Reports the Tensorflow Version

# Pull an image of a Lynx to test it

IMAGEURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg"

plt.imshow(to_img(IMAGEURL))

# headers = {'content-type': 'application/json','X-Marathon-App-Id': app_id}
headers = {"content-type": "application/json"}
jsonimg = img_url_to_json(IMAGEURL)
r = requests.post(
    scoring_url, data=jsonimg, headers=headers
)  # Run the request twice since the first time takes a
# little longer due to the loading of the model
# %time r = requests.post(scoring_url, data=jsonimg, headers=headers)
r.json()

# From the results above we can see that the model correctly classifies this as an Lynx.
# The computation took around 70 ms and the whole round trip around 240 ms. The round trip time will depend on where the resuests are being made.

# Lets try a few more images

images = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/3a/Roadster_2.5_windmills_trimmed.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Harmony_of_the_Seas_%28ship%2C_2016%29_001.jpg/1920px-Harmony_of_the_Seas_%28ship%2C_2016%29_001.jpg",
    "http://yourshot.nationalgeographic.com/u/ss/fQYSUbVfts-T7pS2VP2wnKyN8wxywmXtY0-FwsgxpiZv_E9ZfPsNV5B0ER8-bOdruvNfMD5EbP4SznWz4PYn/",
    "https://cdn.arstechnica.net/wp-content/uploads/2012/04/bohol_tarsier_wiki-4f88309-intro.jpg",
    "http://i.telegraph.co.uk/multimedia/archive/03233/BIRDS-ROBIN_3233998b.jpg",
)

results = [
    requests.post(scoring_url, data=img_url_to_json(img), headers=headers)
    for img in images
]

plot_predictions(images, results)

# The labels predicted by our model seem to be consistent with the images supplied.

# Next lets quickly check what the request response performance is for our deployed model.

image_data = list(map(img_url_to_json, images))  # Retrieve the images and data

timer_results = list()
for img in image_data:
    res=%timeit -r 1 -o -q requests.post(scoring_url, data=img, headers=headers)
    timer_results.append(res.best)

timer_results

print("Average time taken: {0:4.2f} ms".format(10 ** 3 * np.mean(timer_results)))

# We have tested that the model works and we can mode on to the [next notebook to get sense of its throughput](06_SpeedTestWebApp.ipynb)
