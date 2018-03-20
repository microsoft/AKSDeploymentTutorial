
from resnet152 import ResNet152
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input, decode_predictions

import numpy as np
import timeit as t
import base64
import json
from PIL import Image, ImageOps
from io import BytesIO

def init():
    """ Initialize ResNet 152 Model 
    """
    global model    
    print("Executing init() method...")
    
    start = t.default_timer()
    model = ResNet152(weights='imagenet')
    end = t.default_timer()
    print("Model loading time: {} ms".format(round((end-start)*1000, 2)))

def run(inputString):
    """ Classify the input using the loaded model
    """
    start = t.default_timer()
    
    responses = []
    base64Dict = json.loads(inputString) 
    for k, v in base64Dict.items():
        img_file_name, base64Img = k, v 
    decoded_img = base64.b64decode(base64Img)
    img_buffer = BytesIO(decoded_img)
    imageData = Image.open(img_buffer).convert("RGB")
    img = ImageOps.fit(imageData, (224, 224), Image.ANTIALIAS)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    preds = decode_predictions(preds, top=3)[0]
    resp = {img_file_name: preds}
    responses.append(resp)
    
    end = t.default_timer()
    
    return (responses, "Predictions took {0} ms".format(round((end-start)*1000, 2)))

def img_to_json(img_path):
    with open(img_path, 'rb') as file:
        encoded = base64.b64encode(file.read())
    img_dict = {img_path: encoded.decode('utf-8')}
    body = json.dumps(img_dict)
    return body

if __name__ == "__main__":
    init()
    img_path = 'elephant.jpg'
    body = img_to_json(img_path)
    resp = run(body)
    print(resp)