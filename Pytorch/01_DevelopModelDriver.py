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

# # Develop Model Driver

# In this notebook, we will develop the API that will call our model. This module initializes the model, transforms the input so that it is in the appropriate format and defines the scoring method that will produce the predictions. The API will expect the input to be in JSON format. Once  a request is received, the API will convert the json encoded request body into the image format. There are two main functions in the API. The first function loads the model and returns a scoring function. The second function process the images and uses the first function to score them.

import logging
from testing_utilities import img_url_to_json

# We use the writefile magic to write the contents of the below cell to driver.py which includes the driver methods.

# +
# %%writefile driver.py
import base64
import json
import logging
import os
import timeit as t
from io import BytesIO
from pprint import pprint
import numpy as np
import torch
import torch.nn as nn
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import PIL
from PIL import Image, ImageOps

_LABEL_FILE = os.getenv('LABEL_FILE', "synset.txt")
_NUMBER_RESULTS = 3


def _create_label_lookup(label_path):
    with open(label_path, 'r') as f:
        label_list = [l.rstrip() for l in f]
        
    def _label_lookup(*label_locks):
        return [label_list[l] for l in label_locks]
    
    return _label_lookup


def _load_model():
    # Load the model
    model = models.resnet152(pretrained=True)
    model = model.cuda()
    softmax = nn.Softmax(dim=1).cuda()
    model = model.eval()
    
    preprocess_input = transforms.Compose([
        torchvision.transforms.Resize((224, 224), interpolation=PIL.Image.BICUBIC),
         transforms.ToTensor(),
         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    def predict_for(image):
        image = preprocess_input(image)
        with torch.no_grad():
            image = image.expand(1,3,224,224)
            image_gpu = image.type(torch.float).cuda()
            outputs = model(image_gpu)
            pred_proba = softmax(outputs)
        return pred_proba.cpu().numpy().squeeze()
    
    return predict_for


def _base64img_to_pil_image(base64_img_string):
    if base64_img_string.startswith('b\''):
        base64_img_string = base64_img_string[2:-1]
    base64Img = base64_img_string.encode('utf-8')

    # Preprocess the input data 
    startPreprocess = t.default_timer()
    decoded_img = base64.b64decode(base64Img)
    img_buffer = BytesIO(decoded_img)

    # Load image with PIL (RGB)
    pil_img = Image.open(img_buffer).convert('RGB')
    return pil_img


def create_scoring_func(label_path=_LABEL_FILE):
    logger = logging.getLogger("model_driver")
    
    start = t.default_timer()
    labels_for = _create_label_lookup(label_path)
    predict_for = _load_model()
    end = t.default_timer()

    loadTimeMsg = "Model loading time: {0} ms".format(round((end-start)*1000, 2))
    logger.info(loadTimeMsg)
    
    def call_model(image, number_results=_NUMBER_RESULTS):
        pred_proba = predict_for(image).squeeze()
        selected_results = np.flip(np.argsort(pred_proba), 0)[:number_results]
        labels = labels_for(*selected_results)
        return list(zip(labels, pred_proba[selected_results].astype(np.float64)))
    return call_model


def get_model_api():
    logger = logging.getLogger("model_driver")
    scoring_func = create_scoring_func()
    
    def process_and_score(images_dict, number_results=_NUMBER_RESULTS):
        start = t.default_timer()

        results = {}
        for key, base64_img_string in images_dict.items():
            rgb_image = _base64img_to_pil_image(base64_img_string)
            results[key]=scoring_func(rgb_image, number_results=_NUMBER_RESULTS)
        
        end = t.default_timer()

        logger.info("Predictions: {0}".format(results))
        logger.info("Predictions took {0} ms".format(round((end-start)*1000, 2)))
        return (results, 'Computed in {0} ms'.format(round((end-start)*1000, 2)))
    return process_and_score

def version():
    return torch.__version__
# -

# Let's test the module.

logging.basicConfig(level=logging.DEBUG)

# We run the file driver.py which will bring everything into the context of the notebook.

# %run driver.py

# We will use the same Lynx image we used ealier to check that our driver works as expected.

IMAGEURL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg"

predict_for = get_model_api()

jsonimg = img_url_to_json(IMAGEURL)
json_load_img = json.loads(jsonimg)
body = json_load_img['input']
resp = predict_for(body)

pprint(resp[0])

# Next, we can move on to [building our docker image](02_BuildImage.ipynb).
