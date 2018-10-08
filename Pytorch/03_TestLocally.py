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

# # Test web application locally
#

# This notebook pulls some images and tests them against the local web app running inside the Docker container we made previously.

# %load_ext autoreload
# %autoreload 2
import matplotlib.pyplot as plt
import numpy as np
from testing_utilities import to_img, img_url_to_json, plot_predictions
import requests
from dotenv import get_key

# %matplotlib inline

image_name = get_key(".env", "docker_login") + "/" + get_key(".env", "image_repo")
image_name

# Run the Docker conatainer in the background and open port 80. Notice we are using nvidia-docker and not docker command.

# + {"active": "ipynb", "language": "bash"}
# nvidia-docker run -p 80:80 $1
# -

# Wait a few seconds for the application to spin up and then check that everything works.

!curl 'http://0.0.0.0:80/'

!curl 'http://0.0.0.0:80/version' #reports tensorflow version

# Pull an image of a Lynx to test our local web app with.

IMAGEURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg"

plt.imshow(to_img(IMAGEURL))

jsonimg = img_url_to_json(IMAGEURL)
jsonimg[:100]

headers = {"content-type": "application/json"}
# %time r = requests.post('http://0.0.0.0:80/score', data=jsonimg, headers=headers)
print(r)
r.json()

# Let's try a few more images.

images = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/3a/Roadster_2.5_windmills_trimmed.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Harmony_of_the_Seas_%28ship%2C_2016%29_001.jpg/1920px-Harmony_of_the_Seas_%28ship%2C_2016%29_001.jpg",
    "http://yourshot.nationalgeographic.com/u/ss/fQYSUbVfts-T7pS2VP2wnKyN8wxywmXtY0-FwsgxpiZv_E9ZfPsNV5B0ER8-bOdruvNfMD5EbP4SznWz4PYn/",
    "https://cdn.arstechnica.net/wp-content/uploads/2012/04/bohol_tarsier_wiki-4f88309-intro.jpg",
    "http://i.telegraph.co.uk/multimedia/archive/03233/BIRDS-ROBIN_3233998b.jpg",
)

url = "http://0.0.0.0:80/score"
results = [
    requests.post(url, data=img_url_to_json(img), headers=headers) for img in images
]

plot_predictions(images, results)

# Next let's quickly check what the request response performance is for the locally running Docker container.

image_data = list(map(img_url_to_json, images))  # Retrieve the images and data

timer_results = list()
for img in image_data:
    res=%timeit -r 1 -o -q requests.post(url, data=img, headers=headers)
    timer_results.append(res.best)

timer_results

print("Average time taken: {0:4.2f} ms".format(10 ** 3 * np.mean(timer_results)))

# + {"active": "ipynb", "language": "bash"}
# docker stop $(docker ps -q)
# -

# We can now [deploy our web application on AKS](04_DeployOnAKS.ipynb).
