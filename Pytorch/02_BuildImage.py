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

# # Build Docker image 

# In this notebook, we will build the docker container that contains the ResNet152 model, Flask web application, model driver and all dependencies.
# Make sure you have logged in using docker login.

import os
from os import path
import json
import shutil
from dotenv import set_key, get_key, find_dotenv
from pathlib import Path

# We will be using the following Docker information to push the image to docker hub.

env_path = find_dotenv()
if env_path=='':
    Path('.env').touch()
    env_path = find_dotenv()

# +
# "YOUR_DOCKER_LOGIN"
# -

set_key(env_path, "docker_login", "masalvar")

set_key(env_path, "image_repo", "pytorch-gpu")

!cat .env

os.makedirs("flaskwebapp", exist_ok=True)
os.makedirs(os.path.join("flaskwebapp", "nginx"), exist_ok=True)
os.makedirs(os.path.join("flaskwebapp", "etc"), exist_ok=True)

shutil.copy("synset.txt", "flaskwebapp")
shutil.copy("driver.py", "flaskwebapp")
os.listdir("flaskwebapp")

# Below, we create the module for the Flask web application.

# +
# %%writefile flaskwebapp/app.py

from flask import Flask, request
import logging
import json
import driver

app = Flask(__name__)
predict_for = driver.get_model_api()
 
@app.route("/score", methods = ['POST'])
def scoreRRS():
    """ Endpoint for scoring
    """
    if request.headers['Content-Type'] != 'application/json':
        return Response(json.dumps({}), status= 415, mimetype ='application/json')
    request_input = request.json['input']
    response = predict_for(request_input)
    return json.dumps({'result': response})


@app.route("/")
def healthy():
    return "Healthy"

# Tensorflow Version
@app.route('/version', methods = ['GET'])
def version_request():
    return driver.version()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

# +
# %%writefile flaskwebapp/wsgi.py
from app import app as application

def create():
    print("Initialising")
    application.run(host='127.0.0.1', port=5000)
# -

# Here, we write the configuration for the Nginx which creates a proxy between ports **80** and **5000**.

# %%writefile flaskwebapp/nginx/app
server {
    listen 80;
    server_name _;
 
    location / {
    include proxy_params;
    proxy_pass http://127.0.0.1:5000;
    proxy_connect_timeout 5000s;
    proxy_read_timeout 5000s;
  }
}

# +
# %%writefile flaskwebapp/gunicorn_logging.conf

[loggers]
keys=root, gunicorn.error

[handlers]
keys=console

[formatters]
keys=json

[logger_root]
level=INFO
handlers=console

[logger_gunicorn.error]
level=ERROR
handlers=console
propagate=0
qualname=gunicorn.error

[handler_console]
class=StreamHandler
formatter=json
args=(sys.stdout, )

[formatter_json]
class=jsonlogging.JSONFormatter

# +
# %%writefile flaskwebapp/kill_supervisor.py
import sys
import os
import signal

def write_stdout(s):
    sys.stdout.write(s)
    sys.stdout.flush()

# this function is modified from the code and knowledge found here: http://supervisord.org/events.html#example-event-listener-implementation
def main():
    while 1:
        write_stdout('READY\n')
        # wait for the event on stdin that supervisord will send
        line = sys.stdin.readline()
        write_stdout('Killing supervisor with this event: ' + line);
        try:
            # supervisord writes its pid to its file from which we read it here, see supervisord.conf
            pidfile = open('/tmp/supervisord.pid','r')
            pid = int(pidfile.readline());
            os.kill(pid, signal.SIGQUIT)
        except Exception as e:
            write_stdout('Could not kill supervisor: ' + e.strerror + '\n')
            write_stdout('RESULT 2\nOK')

main()

# +
# %%writefile flaskwebapp/etc/supervisord.conf 
[supervisord]
logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB        ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10           ; (num of main logfile rotation backups;default 10)
loglevel=info                ; (log level;default info; others: debug,warn,trace)
pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=true                ; (start in foreground if true;default false)
minfds=1024                  ; (min. avail startup file descriptors;default 1024)
minprocs=200                 ; (min. avail process descriptors;default 200)

[program:gunicorn]
command=bash -c "gunicorn --workers 1 -m 007 --timeout 100000 --capture-output --error-logfile - --log-level debug --log-config gunicorn_logging.conf \"wsgi:create()\""
directory=/code
redirect_stderr=true
stdout_logfile =/dev/stdout
stdout_logfile_maxbytes=0
startretries=2
startsecs=20

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
startretries=2
startsecs=5
priority=3

[eventlistener:program_exit]
command=python kill_supervisor.py
directory=/code
events=PROCESS_STATE_FATAL
priority=2
# -

# We create a custom image based on the CUDA 9 image from NVIDIA and install all the necessary dependencies. This is in order to try and keep the size of the image as small as possible.

# %%writefile flaskwebapp/requirements.txt
Pillow==5.0.0
click==6.7
configparser==3.5.0
Flask==0.12.2
gunicorn==19.6.0
json-logging-py==0.2
MarkupSafe==1.0
olefile==0.44
requests==2.12.3

# +
# %%writefile flaskwebapp/dockerfile

FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

RUN echo "deb http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list

RUN mkdir /code
WORKDIR /code
ADD . /code/
ADD etc /etc

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        nginx \
        supervisor \
        wget && \
        rm -rf /var/lib/apt/lists/*


ENV PYTHON_VERSION=3.6
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
    chmod +x ~/miniconda.sh && \
    ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda create -y --name py$PYTHON_VERSION python=$PYTHON_VERSION numpy scipy pandas scikit-learn && \
    /opt/conda/bin/conda clean -ya
ENV PATH /opt/conda/envs/py$PYTHON_VERSION/bin:$PATH
ENV LD_LIBRARY_PATH /opt/conda/envs/py$PYTHON_VERSION/lib:/usr/local/cuda/lib64/:$LD_LIBRARY_PATH
ENV PYTHONPATH /code/:$PYTHONPATH

    
RUN rm /etc/nginx/sites-enabled/default && \
    cp /code/nginx/app /etc/nginx/sites-available/ && \
    ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/ && \
    /opt/conda/bin/conda install -c pytorch pytorch==0.4.1 && \
    pip install --upgrade pip && \
    pip install torchvision==0.2.1 && \
    pip install -r /code/requirements.txt && \       
    /opt/conda/bin/conda clean -yt

EXPOSE 80
CMD ["supervisord", "-c", "/code/etc/supervisord.conf"]
# -

# The image name below refers to our dockerhub account. If you wish to push the image to your account make sure you change the docker login.

image_name = get_key(env_path, 'docker_login') + '/' +get_key(env_path, 'image_repo') 
application_path = 'flaskwebapp'
docker_file_location = path.join(application_path, 'dockerfile')

# Next, we build our docker image. The output of this cell is cleared from this notebook as it is quite long due to all the installations required to build the image. However, you should make sure you see 'Successfully built' and 'Successfully tagged' messages in the last line of the output when you run the cell. 

!docker build -t $image_name -f $docker_file_location $application_path

# Below we will push the image created to our dockerhub registry. Make sure you have already logged in to the appropriate dockerhub account using the docker login command. If you haven't loged in to the approrpiate dockerhub account you will get an error.

!docker push $image_name

print('Docker image name {}'.format(image_name))

# We can now [test our image locally](03_TestLocally.ipynb).
