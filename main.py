import numpy as np
import math
import random
import zmq
import time
import cv2
import yaml
import struct

import os
import struct
import datetime
import json

from src import inference_data
infe_data = inference_data.InferenceData()


def start_server():
    # create log dir
    log_path = '/home/sena/log_data/%s/%s/%s/%s' % ( datetime.datetime.today().strftime('%Y')\
                                                            , datetime.datetime.today().strftime('%m')\
                                                            , datetime.datetime.today().strftime('%d')\
                                                            , datetime.datetime.today().strftime('%H%M%S') )
    print("log directory : %s" % log_path)
    os.makedirs(log_path, exist_ok=True)

    # make condition file
    condition = {}
    condition_path = "%s/condition.txt" % log_path
    str_location = input("location : ")
    if str_location == "":
        str_location = "none"
    condition['location'] = str_location
    str_weather = input("weather : ")
    if str_weather == "":
        str_weather = "none"
    condition['weather'] = str_weather
    str_purpose = input("purpose : ")
    if str_purpose == "":
        str_purpose = "none"
    condition['purpose'] = str_purpose
    with open(condition_path, 'w') as filename:
        json.dump(condition, filename, sort_keys=True, indent=4)

    # ZMQ setting
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    # load lookup table
    LUT = infe_data.LoadLUT()

    while True:
        # receive LiDAR data
        print("Recieving LiDAR data...", flush=True, end='')
        data = socket.recv()
        size_of_data = struct.unpack('N', data)
        size_of_data = size_of_data[0]
        socket.send(str(size_of_data).encode())
        oneshot = []
        for i in range(0, size_of_data):
            data = socket.recv()
            point = struct.unpack('ddddddd', data)
            _point = [point[0], point[1], point[2], point[6]]
            oneshot.append(_point)
            rpl = "done"
            socket.send((rpl.encode()))
        print("done")

        # create timestamp dir
        timestamp_path = "%s/%s" % ( log_path, datetime.datetime.today().strftime('%H%M%S%f') )
        os.makedirs(timestamp_path, exist_ok=True)

        # save oneshot data
        oneshot = np.array(oneshot)
        oneshot = oneshot * [1, -1, -1, 1]
        oneshot_path = "%s/oneshot.txt" % timestamp_path
        with open(data_path, 'w') as filename:
            np.savetxt(filename, oneshot)

        # show oneshot
        infe_data.ShowOneshot(oneshot)

        # oneshot -> reflection intensity distribution
        RID = infe_data.CreateRID(LUT, oneshot)

        # save rid data
        rid_path = "%s/rid.npy" % timestamp_path
        np.save(rid_path, RID)

        # show rid
        infe_data.ShowRID(RID)
        


if __name__ == "__main__":
    start_server()

