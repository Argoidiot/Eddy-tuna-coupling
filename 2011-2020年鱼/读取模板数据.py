# -*- coding: utf-8 -*-
import pickle
import numpy as np
import datetime
from tqdm import tqdm
import pandas as pd


# YFT
catches = [54.5315, 48.7215, 49.2949, 50.7352, 48.4934, 45.5411, 39.7621, 31.3742, 35.2306, 34.1980, 39.1933, 42.3385]
# catches = [45.7955, 46.7453, 47.9314, 46.7377, 46.3505, 51.0697, 32.0372, 24.2733, 32.2780, 24.8824, 34.7185, 40.7572]  ##[-10, -5]U[5, 10]
# SKJ
# catches = [36.4767, 53.8722, 57.2145, 48.7866, 46.0068, 56.9374, 70.1377, 59.2468, 42.4397, 56.0008, 63.5559, 72.6750]
# catches = [35.5798, 37.5817, 55.9285, 38.4789, 41.5634, 37.2758, 66.3759, 44.2204, 39.7605, 56.0009, 54.1372, 55.0368]
# BET
# catches = [18.7330, 15.5428, 16.5687, 14.4545, 15.7749, 15.3304, 13.2484, 13.4780, 15.8345, 14.2082, 16.2080, 14.0724]
# catches = [18.8041, 14.5642, 17.9088, 14.2260, 15.4044, 15.3596, 15.2433, 14.6067, 15.1546, 13.6431, 16.4356, 13.9023]  ##[-10, -5]U[5, 10]
catch_max = max(catches)
catches = [u / catch_max for u in catches]
years = range(2010, 2022)

lats_0 = np.concatenate((np.arange(-30, -5+0.1), np.arange(5, 45.1)), axis=0)
lons_0 = np.arange(-150, -70)
lons, lats = np.meshgrid(lons_0, lats_0)
lats_1 = lats.flatten()
lons_1 = lons.flatten()

result = np.empty((0, 12))
s = 'SKJ'
for year in tqdm(range(2010, 2022)):
    days = (datetime.datetime(year+1, 1, 1) - datetime.datetime(year, 1, 1)).days
    # res = np.empty((0, 12))
    h = years.index(year)
    scale = catches[h]
    for month in tqdm(range(1, 13)):
        # data_month = np.zeros((10, len(lats_0), len(lons_0)))
        # data_month[0, :, :] = lats
        # data_month[cata1, :, :] = lons

        if month < 10:
            str_month = '0' + str(month)
        else:
            str_month = str(month)

        # 读取csv数据，并选择指定行
        file_fish = 'F:\\Data\\Fish Data\\PublicPSTuna\\PublicPSTunaFlag.csv'
        df0 = pd.read_csv(file_fish, usecols=['Year', 'Month', 'LatC1', 'LonC1', s],)
        # 筛选出年份为year，月份为month, 且渔获数据不为0的数据
        df0 = df0[(df0['Year'] == year) & (df0['Month'] == month) & (df0[s] > 0)]
        df = df0.groupby(['Year', 'Month', 'LatC1', 'LonC1'])[s].sum().reset_index()
        catch = []
        for index, row in df.iterrows():
            lat_skj = row['LatC1']
            lon_skj = row['LonC1']
            skj = row[s]
            catch.append([lat_skj, lon_skj, skj/scale, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # 获取这个月的日期
        if month < 12:
            date_range = (datetime.datetime(year, month+1, 1) - datetime.datetime(year, month, 1)).days
        else:
            date_range = (datetime.datetime(year+1, 1, 1) - datetime.datetime(year, month, 1)).days
        dates = [datetime.datetime(year, month, 1) + datetime.timedelta(days=r) for r in range(date_range)]

        for date in dates:
            date0 = date.strftime('%Y-%m-%d')
            file_bin = 'F:\\研究方向\\2011-2020匹配\\模板/' + date0 + '_bin.pkl'
            with open(file_bin, 'rb') as f:
                data_bin = pickle.load(f)  # 纬度、经度、相对半径、方位角

            # 匹配
            for catch_one in catch:
                lat = catch_one[0]
                lon = catch_one[1]
                i, j = np.where((np.around(data_bin[0, :, :], 2) == (lat-0.5)) & (np.around(data_bin[1, :, :], 2) == (lon-0.5)))
                if len(i) == 0 and len(j) == 0:
                    continue
                data_bin_box = data_bin[2, i[0]:i[0]+5, j[0]:j[0]+5]

                catch_one[3] += np.count_nonzero((0 < data_bin_box) & (data_bin_box <= 0.5))
                catch_one[4] += np.count_nonzero((0.5 < data_bin_box) & (data_bin_box <= 1))
                catch_one[5] += np.count_nonzero((1 < data_bin_box) & (data_bin_box <= 1.5))
                catch_one[6] += np.count_nonzero((1.5 < data_bin_box) & (data_bin_box <= 2))

                catch_one[7] += np.count_nonzero((-0.5 <= data_bin_box) & (data_bin_box <= 0))
                catch_one[8] += np.count_nonzero((-1 <= data_bin_box) & (data_bin_box < -0.5))
                catch_one[9] += np.count_nonzero((-1.5 <= data_bin_box) & (data_bin_box < -1))
                catch_one[10] += np.count_nonzero((-2 <= data_bin_box) & (data_bin_box <= -1.5))

                catch_one[11] += np.count_nonzero(np.isnan(data_bin_box))

        # 把每天的数据叠加在一块
        if len(catch) > 0:
            result = np.concatenate((result, np.array(catch)), axis=0)
        else:
            continue
# 由于在统计渔业数据时未去除（-10，10）的数据，因此需要在这去掉
# result = result[((result[:, 0] < -5) & (result[:, 0] > -10)) | ((result[:, 0] > 5) & (result[:, 0] < 10))]
result = result[(result[:, 0] > 10) | (result[:, 0] < -10)]

result[:, 3:] *= (12100/25)
A = result[:, 3:]
# A1 = np.hstack((A, np.ones(result.shape[0]).reshape(-1, 1)))
b = result[:, 2]
# 最小二乘法：x为解，resid是残差的平方和，rank是系数矩阵的秩，s为奇异值
x, resid, rank, s = np.linalg.lstsq(A, b)
x = np.round(x, decimals=7)
b_mean = np.mean(b)
b_new = [(x[0] * A[m][0] + x[1] * A[m][1] + x[2] * A[m][2] + x[3] * A[m][3] + x[4] * A[m][4] + x[5] * A[m][5] + x[6] *
          A[m][6] + x[7] * A[m][7] + x[8] * A[m][8]) for m in range(len(A))]
sst = sum([(b[m] - b_mean) ** 2 for m in range(len(b))])
sse = resid
r2 = 1 - sse / sst
print(x)