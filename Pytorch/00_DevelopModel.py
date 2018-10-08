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

# # Develop Model

# In this noteook, we will go through the steps to load the ResNet152 model, pre-process the images to the required format and call the model to find the top predictions.

# +
import PIL
import numpy as np
import torch
import torch.nn as nn
import torchvision
import wget
from PIL import Image
from torchvision import models, transforms

# -

print(torch.__version__)
print(torchvision.__version__)

!wget "http://data.dmlc.ml/mxnet/models/imagenet/synset.txt"

# We first load the model which we imported from the resnet152 module. This can take about 10s.

# %%time
model = models.resnet152(pretrained=True)

# You can print the summary of the model in the below cell. We cleared the output here for brevity. When you run the cell you should see a list of the layers and the size of the model in terms of number of parameters at the bottom of the output.

model=model.cuda()

print(model)

# Let's test our model with an image of a Lynx.

wget.download('https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Lynx_lynx_poing.jpg/220px-Lynx_lynx_poing.jpg')

img_path = '220px-Lynx_lynx_poing.jpg'
print(Image.open(img_path).size)
Image.open(img_path)

# Below, we load the image by resizing to (224, 224) and then preprocessing using the methods from keras preprocessing and imagenet utilities.

img = Image.open(img_path).convert('RGB')

preprocess_input = transforms.Compose([
    torchvision.transforms.Resize((224, 224), interpolation=PIL.Image.BICUBIC),
     transforms.ToTensor(),
     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

img = Image.open(img_path)
img = preprocess_input(img)

# Now, let's call the model on our image to predict the top 3 labels. This will take a few seconds.

def create_label_lookup():
    with open('synset.txt', 'r') as f:
        label_list = [l.rstrip() for l in f]
    def _label_lookup(*label_locks):
        return [label_list[l] for l in label_locks]
    return _label_lookup

label_lookup = create_label_lookup()

softmax = nn.Softmax(dim=1).cuda()

model = model.eval()

# %%time
with torch.no_grad():
    img = img.expand(1,3,224,224)
    image_gpu = img.type(torch.float).cuda()
    outputs = model(image_gpu)
    probabilities = softmax(outputs)

label_lookup = create_label_lookup()

probabilities_numpy = probabilities.cpu().numpy().squeeze()

top_results = np.flip(np.sort(probabilities_numpy), 0)[:3]

labels = label_lookup(*np.flip(probabilities_numpy.argsort(),0)[:3])

dict(zip(labels, top_results))

# The top guess is Lynx with probability about 99%. We can now move on to [developing the model api for our model](01_DevelopModelDriver.ipynb).
