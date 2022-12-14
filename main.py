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
import glob
import matplotlib.pyplot as plt


OS = 'Linux'
if OS =='Apple':
    OS_path = '/Users/senapo/IRLab/log_data'
if OS =='Linux':
    OS_path = '/home/sena/log_data'


from src import inference_data
# Nt = 9
network_path = f'{OS_path}/2022/11/06/network_050942'
# Nt = 27
#network_path = f'{OS_path}/2022/11/06/network_042609'
infe_data = inference_data.InferenceData(network_path)

def scan_viewer():
    # create log dir
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')
    day = datetime.datetime.today().strftime('%d')
    time = datetime.datetime.today().strftime('%H%M%S')
    log_path = f'{OS_path}/{year}/{month}/{day}/scanview_{time}'
    os.makedirs(log_path, exist_ok=True)
    print(f"log directory : {log_path}")

    # make condition file
    condition = {}
    condition['network'] = network_path
    str_location = input("location : ")
    if str_location == "":
        str_location = "none"
    condition['location'] = str_location
    str_weather = input("weather : ")
    if str_weather == "":
        str_weather = "none"
    condition['weather'] = str_weather
    str_temperature = input("temperature : ")
    if str_weather == "":
        str_weather = "none"
    condition['temperature'] = str_temperature
    str_purpose = input("purpose : ")
    if str_purpose == "":
        str_purpose = "none"
    condition['purpose'] = str_purpose
    condition_path = f'{log_path}/condition.txt'
    with open(condition_path, 'w') as filename:
        json.dump(condition, filename, sort_keys=True, indent=4)

    # ZMQ setting
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    print("Start zmq server.\n ----- ")

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
        print(" finish.")

        # create timestamp dir
        time = datetime.datetime.today().strftime('%H%M%S%f')
        timestamp_path = f'{log_path}/{time}'
        os.makedirs(timestamp_path, exist_ok=True)

        # save oneshot data
        oneshot = np.array(oneshot)
        oneshot = oneshot * [1, -1, -1, 1]
        with open(f'{timestamp_path}/oneshot.txt', 'w') as filename:
            np.savetxt(filename, oneshot)

        # show oneshot
        infe_data.ShowOneshot(oneshot, timestamp_path)

        # oneshot -> reflection intensity distribution
        RID, datanum_grid, mu_grid, sigma_grid = infe_data.CreateRID(LUT, oneshot)

        # save rid data
        np.save(f'{timestamp_path}/rid.npy', RID)

        # show rid
        infe_data.ShowRID(RID, datanum_grid, mu_grid, sigma_grid, timestamp_path)


def log_viewer():
    # create log dir
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')
    day = datetime.datetime.today().strftime('%d')
    time = datetime.datetime.today().strftime('%H%M%S')
    log_path = f'{OS_path}/{year}/{month}/{day}/logview_{time}'
    os.makedirs(log_path, exist_ok=True)
    print(f"log directory : {log_path}")

    # load lookup table
    LUT = infe_data.LoadLUT()

    path_list = sorted(glob.glob(f'{OS_path}/2022/11/14/network_172609/*'))
    print(f'{OS_path}/log_data/2022/11/14/network_172609/*')
    data_num = len(path_list)
    print(data_num)
    x = np.arange(1600)
    for num in range(data_num):
        if(".txt" in path_list[num]):
            continue
        if(".png" in path_list[num]):
            continue
        print(path_list[num])
        oneshot = np.loadtxt(f'{path_list[num]}/oneshot.txt')

        # create timestamp dir
        time = datetime.datetime.today().strftime('%H%M%S%f')
        timestamp_path = f'{log_path}/{time}'
        os.makedirs(timestamp_path, exist_ok=True)

        # show oneshot
        infe_data.ShowOneshot(oneshot, timestamp_path)

        # oneshot -> reflection intensity distribution
        RID, datanum_grid, mu_grid, sigma_grid = infe_data.CreateRID(LUT, oneshot)

        # save rid data
        np.save(f'{timestamp_path}/rid.npy', RID)

        # show rid
        infe_data.ShowRID(RID, datanum_grid, mu_grid, sigma_grid, timestamp_path)




if __name__ == "__main__":
    scan_viewer()
    #log_viewer()

