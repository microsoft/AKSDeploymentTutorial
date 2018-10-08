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

# ### Load Test deployed web application
# This notebook pulls some images and tests them against the deployed web application. We submit requests asychronously which should reduce the contribution of latency.

# +
import asyncio
import json
import urllib.request
from timeit import default_timer

import aiohttp
import matplotlib.pyplot as plt
from testing_utilities import to_img, gen_variations_of_one_image
from tqdm import tqdm

# %matplotlib inline
# -

print(aiohttp.__version__)

# We will test our deployed service with 100 calls. We will only have 4 requests concurrently at any time. We have only deployed one pod on one node and increasing the number of concurrent calls does not really increase throughput. Feel free to try different values and see how the service responds.

NUMBER_OF_REQUESTS = 100  # Total number of requests
CONCURRENT_REQUESTS = 4   # Number of requests at a time

# Get the IP address of our service

service_json = !kubectl get service azure-dl -o json
service_dict = json.loads(''.join(service_json))
app_url = service_dict['status']['loadBalancer']['ingress'][0]['ip']

scoring_url = 'http://{}/score'.format(app_url)
version_url = 'http://{}/version'.format(app_url)

!curl $version_url # Reports the Tensorflow Version

IMAGEURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg"
plt.imshow(to_img(IMAGEURL))

# Here, we use varitions of the same image to test the service.

url_list = [[scoring_url, jsonimg] for jsonimg in gen_variations_of_one_image(IMAGEURL, NUMBER_OF_REQUESTS)]

def decode(result):
    return json.loads(result.decode("utf-8"))

async def fetch(url, session, data, headers):
    start_time = default_timer()
    async with session.request('post', url, data=data, headers=headers) as response:
        resp = await response.read()
        elapsed = default_timer() - start_time
        return resp, elapsed

async def bound_fetch(sem, url, session, data, headers):
    # Getter function with semaphore.
    async with sem:
        return await fetch(url, session, data, headers)

async def await_with_progress(coros):
    results=[]
    for f in tqdm(asyncio.as_completed(coros), total=len(coros)):
        result = await f
        results.append((decode(result[0]),result[1]))
    return results

async def run(url_list, num_concurrent=CONCURRENT_REQUESTS):
    headers = {'content-type': 'application/json'}
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(num_concurrent)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with aiohttp.ClientSession() as session:
        for url, data in url_list:
            # pass Semaphore and session to every POST request
            task = asyncio.ensure_future(bound_fetch(sem, url, session, data, headers))
            tasks.append(task)
        return await await_with_progress(tasks)

# Below we run the 100 requests against our deployed service

loop = asyncio.get_event_loop()
start_time = default_timer()
complete_responses = loop.run_until_complete(asyncio.ensure_future(run(url_list, num_concurrent=CONCURRENT_REQUESTS)))
elapsed = default_timer() - start_time
print('Total Elapsed {}'.format(elapsed))
print('Avg time taken {0:4.2f} ms'.format(1000*elapsed/len(url_list)))

# Below we can see the output of some of our calls

complete_responses[:3]

num_succesful=[i[0]['result'][0]['image'][0][0] for i in complete_responses].count('n02127052 lynx, catamount')
print('Succesful {} out of {}'.format(num_succesful, len(url_list)))

# Example response
plt.imshow(to_img(IMAGEURL))
complete_responses[0]

# To tear down the cluster and all related resources go to the  [tear down the cluster](07_TearDown.ipynb) notebook.
