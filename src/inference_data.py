import numpy as np
import math
import json
import matplotlib.pyplot as plt


class InferenceData():
    def __init__(self, network_path):
        config_path = f'{network_path}/config.txt'
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

        self.label_size = self.config['label_size']

        self.avoid_label = self.config['avoid_label']
        self.avoid_th = self.config['avoid_th']

        self.network_path = network_path


    def LoadLUT(self):
        LUT = np.load(f'{self.network_path}/lookup_table.npy')
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

        # 各格子のデータ数を算出
        datanum_grid = np.empty((self.Nr, self.Nt), dtype='uint64')
        for i in range(self.Nr):
            for j in range(self.Nt):
                datanum_grid[i, j] = len(divided_data[i][j])

        # 各格子の平均(mu)・標準偏差(sigma)を算出
        mu_grid = np.empty((self.Nr, self.Nt))
        for i in range(self.Nr):
            for j in range(self.Nt):
                total = sum(divided_data[i][j])
                num = datanum_grid[i, j]
                if num == 0:
                    mu_grid[i, j] = 0
                else:
                    mu_grid[i, j] = total / num

        sigma_grid = np.empty((self.Nr, self.Nt))
        for i in range(self.Nr):
            for j in range(self.Nt):
                num = datanum_grid[i, j]
                total = 0
                for k in range(num):
                    total += (divided_data[i][j][k] - mu_grid[i,j]) ** 2
                sigma_hat_2 = total / num
                sigma_grid[i, j] = math.sqrt(sigma_hat_2)

        # 反射強度分布に変換する
        rid_data = np.zeros((self.Nr, self.Nt, self.intensity_max))
        for i in range(self.Nr):
            for j in range(self.Nt):
                # データ数が0の格子はスキップ
                if datanum_grid[i, j] == 0:
                    continue
                for num in range(datanum_grid[i, j]):
                    intensity = int( divided_data[i][j][num] )
                    rid_data[i, j, intensity] += 1
                rid_data[i, j] = rid_data[i, j] / datanum_grid[i, j]
        return rid_data, datanum_grid, mu_grid, sigma_grid


    def ShowOneshot(self, oneshot, timestamp_path):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(projection='3d')
        ax.set_xlabel("x-axis")
        ax.set_ylabel("y-axis")
        ax.set_zlabel("z-axis")
        x_min, x_max = -1, 4
        y_min, y_max = -4, 4
        z_min, z_max = -2, 1
        ax.set_xlim3d(x_min, x_max)
        ax.set_ylim3d(y_min, y_max)
        ax.set_zlim3d(z_min, z_max)
        ax.set_box_aspect((x_max - x_min, y_max - y_min, z_max - z_min))
        ax.view_init(elev=20, azim=200)
        x = oneshot[:, 0]
        y = oneshot[:, 1]
        z = oneshot[:, 2]
        ax.scatter(x, y, z, s=1)
        plt.savefig(f'{timestamp_path}/oneshot.pdf')
        plt.show()


    def ShowRID(self, RID, datanum_grid, mu_grid, sigma_grid, timestamp_path):
        x = np.arange(self.intensity_max)
        fig_num = 0
        while(True):
            str_ir = input(f" ir(0~{self.Nr-1}) = ")
            str_jt = input(f" jt(0~{self.Nt-1}) = ")

            # break
            if str_ir == "" and str_jt == "":
                print("-----")
                break

            # continue
            print()
            if str_ir.find(" ") == -1:
                ir_start = int( str_ir )
                ir_end = int( str_ir )
                ir_num = 1
            else:
                ir_start = int( str_ir[0 : str_ir.find(" ")] )
                ir_end = int( str_ir[str_ir.find(" ")+1 : -1] )
                ir_num = ir_end - ir_start + 1

            if str_jt.find(" ") == -1:
                jt_start = int( str_jt )
                jt_end = int( str_jt )
                jt_num = 1
            else:
                jt_start = int( str_jt[0 : str_jt.find(" ")] )
                jt_end = int( str_jt[str_jt.find(" ")+1 : ] )
                jt_num = jt_end - jt_start + 1

            fig, ax = plt.subplots(ir_num, jt_num, squeeze=False, tight_layout=True, sharex=True, sharey=True)
            for i in range(ir_num):
                for j in range(jt_num):
                    # plot RID
                    y = RID[ir_start + i, jt_start + j]
                    ax[ir_num - i - 1, jt_num - j - 1].bar(x, y, color='tab:blue')
                    num = datanum_grid[ir_start, jt_start]
                    ax[ir_num - i - 1, jt_num - j - 1].text(1300, 0.100, f"num={num}", horizontalalignment='left', verticalalignment='top', color='tab:blue')
                    # plot mu
                    mu = int( mu_grid[ir_start + i, jt_start + j] )
                    ax[ir_num - i - 1, jt_num - j - 1].vlines(x=mu,ymin=0, ymax=0.1, ls='-', color='tab:orange')
                    ax[ir_num - i - 1, jt_num - j - 1].text(1300, 0.095, f"mu={mu}", horizontalalignment='left', verticalalignment='top', color='tab:orange')
                    # plot sigma
                    sigma = int( sigma_grid[ir_start + i, jt_start + j] )
                    ax[ir_num - i - 1, jt_num - j - 1].hlines(y=0.09, xmin=mu-(sigma/2), xmax=mu+(sigma/2), ls='-', color='tab:green')
                    ax[ir_num - i - 1, jt_num - j - 1].text(1300, 0.090, f"sigma={sigma}", horizontalalignment='left', verticalalignment='top', color='tab:green')
                    # setting
                    ax[ir_num - i - 1, jt_num - j - 1].set_title(f"({ir_start + i}, {jt_start + j}), {datanum_grid[ir_start + i, jt_start + j]}")
                    ax[ir_num - i - 1, jt_num - j - 1].set_xlim(0, self.intensity_max)
                    ax[ir_num - i - 1, jt_num - j - 1].set_ylim(0, 0.11)
                    ax[ir_num - i - 1, jt_num - j - 1].set_xlabel("x-axis")
                    ax[ir_num - i - 1, jt_num - j - 1].set_ylabel("y-axis")
            plt.savefig(f'{timestamp_path}/RID_{fig_num}.pdf')
            plt.show()
            fig_num += 1

