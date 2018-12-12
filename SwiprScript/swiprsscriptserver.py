import os, sys
from pathlib import Path
# import numpy as np
# import torch
# from fastai.conv_learner import tfms_from_model, ImageClassifierData, ConvLearner, resnext50, open_image, transforms_side_on
from fastai.conv_learner import *
import zmq
import argparse
import threading


# Errors
ERROR_UNKNOWN_ERROR = "-1"
ERROR_PATH_DOES_NOT_EXIST = "-2"
ERROR_FAILED_TO_ANALYZE = "-3"
ERROR_FAILED_TO_CONNECT_TO_SOCKET = "-4"

# Environment Variable Fetching
SwiprModelsDir = os.environ.get("Swipr_ModelsPath", "/home/djori/projects/swipr/src/swiprscript/torchthings")
SwiprScriptPort = os.environ.get("Swipr_ScriptPort", "6100")
SwiprScriptUrl = os.environ.get("Swipr_ScriptUrl", "tcp://127.0.0.1")
Swipr_ModelToUse = os.environ.get("Swipr_ModelToUse", "swipr1_3")

# Path setup and model locations
PATH = Path(SwiprModelsDir)
s0 = "swipr1_1e4_1_397"
s1 = "swipr1_1e4_3__1_2_082"
s3 = "swipr1_1e3_3_1_2_358"
s4 = "swipr1_3"


parser = argparse.ArgumentParser(description='zeromq server/client')
parser.add_argument('--compute')

# Main functions

def PredictOnImage(ipath):
    i = open_image(ipath)
    t = tfms_va(i)  
    preds = learn.predict_array(t[None])
    x = np.exp(preds)
    tup = (x[0][0], x[0][1])
    return tup

def LoadLearner():
    print("loading learner")
    global learn, tfms_va
    label_csv = PATH/'test1.csv'
    val_idxs = torch.load(PATH/'val_idxs.pkl')
    sz=224
    arch=resnext50
    bs=24
    tfms_tr, tfms_va = tfms_from_model(arch, sz, aug_tfms=transforms_side_on, max_zoom=1.1)
    data = ImageClassifierData.from_csv('./', './', label_csv, val_idxs=val_idxs, tfms=(tfms_tr, tfms_va), bs=bs)
    learn = ConvLearner.pretrained(arch, data, precompute=False)
    learn.load(Swipr_ModelToUse)
    learn.model.cpu()

def IsMessageValid(msg):
    """
    needs to be a valid path to an existing image
    """
    return os.path.isfile(msg)

def getSockUrl(url=SwiprScriptUrl, port=SwiprScriptPort):
    """
    Gets the socket address for this server. Derives from the following environment variables:

    Swipr_ScriptPort  
    Swipr_ScriptUrl
    """
    s = "{0}:{1}".format(url, port)
    return s

def TransformPrediction(pred):
    """
    Takes the prediction tuple from the model
    and returns a simple string representing the values, i.e.,:  

    "0.7532,0.1122"
    """
    s = "{0},{1}".format(pred[0],pred[1])
    return s

## Section for zMQ

def Kill():
    os._exit(-5)

def main():
    args = parser.parse_args()
    if args.compute:
        try:
            t = threading.Timer(10.0, Kill)
            t.start()
            # client
            #print("compute enaged")
            context = zmq.Context()
            #print("context established")
            socket = context.socket(zmq.REQ)
            socket.connect(getSockUrl())
            socket.send_string(args.compute)
            msg = socket.recv()
            msg = msg.decode("utf-8")
            print(msg)
            t.cancel()
            return 0
        except: 
            return ERROR_FAILED_TO_CONNECT_TO_SOCKET
    else:
        # server
        LoadLearner()
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(getSockUrl())
        print("BOUND")
        while True:
            msg = socket.recv()
            msg = msg.decode("utf-8")
            print("Received compute command for picture path: {0}".format(msg))
            try:
                if not IsMessageValid(msg):
                    print("Was given an invalid path to analyze")
                    socket.send_string(ERROR_PATH_DOES_NOT_EXIST)
                else:
                    result = PredictOnImage(msg)
                    response = TransformPrediction(result)
                    socket.send_string(response)
            except:
                print("Encountered an error while analyzing the image")
                socket.send_string(ERROR_FAILED_TO_ANALYZE)

# main
if __name__ == "__main__":
    sys.exit(main())
