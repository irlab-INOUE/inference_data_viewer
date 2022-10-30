import os
import sys
import glob
import json
import pickle
import tensorflow as tf
import numpy as np
import math
import random
from tqdm import tqdm


class InferenceData():
    def __init__(self):
        config_path = 'network/config.txt'
        with open(config_path, 'r') as filename:
            self.config = json.load(filename)

        self.z_min = self.config['z_min']
        self.z_max = self.config['z_max']
        self.Nr = self.config['Nr']
        self.r_min = self.config['r_min']
        self.r_max = self.config['r_max']
        self.r_space = np.linspace(self.r_min, self.r_max, self.Nr+1)
        self.Nt = self.config['Nt']
        self.t_min = self.config['t_min']
        self.t_max = self.config['t_max']
        self.t_space = np.linspace(self.t_min, self.t_max, self.Nt+1)
        self.intensity_max = self.config['intensity_max']

        self.pixel_size = self.config['pixel_size']
        self.height = int(2 * self.r_max / self.pixel_size)  #画像の縦方向（xに対応）
        self.width = int(2 * self.r_max / self.pixel_size)   #画像の横方向（yに対応）

        self.Nr = self.config['Nr']
        self.Nt = self.config['Nt']
        self.label_size = self.config['label_size']

        self.avoid_label = self.config['avoid_label']
        self.avoid_th = self.config['avoid_th']

        self.r_min = self.config['r_min']
        self.r_max = self.config['r_max']
        self.Nr = self.config['Nr']
        self.t_min = self.config['t_min']
        self.t_max = self.config['t_max']
        self.Nt = self.config['Nt']


    def LoadLUT(self):
        LUT = np.load('network/lookup_table.npy')
        return LUT


    def CreateRID(self, LUT, oneshot):
        # 反射強度の上限を制限
        oneshot = oneshot[oneshot[:, 3] < self.intensity_max]

        # 路面データを抽出
        oneshot_2d = oneshot[(self.z_min <= oneshot[:, 2]) & (oneshot[:, 2] <= self.z_max)]
        oneshot_2d_num = len(oneshot_2d)

        # 極座標格子に分割する
        divided_data = [[[] for j in range(self.Nt)] for i in range(self.Nr)]
        for num in range(oneshot_2d_num):
            x = oneshot_2d[num, 0]
            y = oneshot_2d[num, 1]
            v = int(-x / self.pixel_size + self.height/2)
            u = int(-y / self.pixel_size + self.width/2)
            if (0<=v<self.height) and (0<=u<self.width):
                intensity = oneshot_2d[num, 3]
                r_i = int(LUT[v, u, 4])
                t_j = int(LUT[v, u, 5])
                if (r_i != -1) and (t_j != -1):
                    divided_data[r_i][t_j].append(intensity)

        # 反射強度分布に変換する
        rid_data = np.zeros((self.Nr, self.Nt, self.intensity_max))
        for i in range(self.Nr):
            for j in range(self.Nt):
                datanum_on_grid = len(divided_data[i][j])
                if datanum_on_grid != 0:
                    for num in range(datanum_on_grid):
                        intensity = int(divided_data[i][j][num])
                        rid_data[i, j, intensity] += 1
                    rid_data[i, j] = rid_data[i, j] / datanum_on_grid
        return rid_data


    def ShowOneshot(self, oneshot):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        x = oneshot[:, 0]
        y = oneshot[:, 1]
        z = oneshot[:, 2]
        ax.scatter(x, y, z, s=1)
        plt.show()


    def ShowRID(self, RID):
        x = np.arange(self.intensity_max)
        while(True):
            str_Nr = input("Nr = ")
            str_Nt = input("Nt = ")
            # end
            if str_Nr == "" and str_Nt == "":
                break

            Nr_range = [int(str_Nr[0:str_Nr.find()-1])]
            Nt_range = []
            fig, ax = plt.subplots(self.Nr, self.Nt, squeeze=False, tight_layout=True, sharex=True, sharey=True)
            for i in range(self.Nr):
                for j in range(self.Nt):
                    y = RID[i, j]
                    ax[self.Nr-1-i, self.Nt-1-j].bar(x, y)
                    ax[self.Nr-1-i, self.Nt-1-j].set_title("(%d, %d)" % (self.Nr, self.Nt))
            plt.show()
