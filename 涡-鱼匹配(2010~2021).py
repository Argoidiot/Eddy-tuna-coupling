#! /usr/bin/env/python3
# -*- coding=utf-8 -*-
"""
======================模块功能描述=========================    
       @File     : 涡-鱼匹配(2010~2021).py
       @IDE      : PyCharm
       @Author   : Wukkkkk
       @Date     : 2024/7/13 上午10:09
       @Desc     : 2010年~2021年三种金枪鱼与涡旋的匹配结果绘制
=========================================================   
"""
import pickle
from tqdm import tqdm
import numpy as np
import datetime
import pandas as pd

years = range(2010, 2021)
tuna = 'BET'

kArray = np.empty((0, 12))
for year in range(2010, 2022):
    print(year)
    days = (datetime.datetime(year + 1, 1, 1) - datetime.datetime(year, 1, 1)).days  # 这一年的天数
    for month in tqdm(range(1, 13)):
        if month < 10:  # 便于读取网格匹配数据
            str_month = '0' + str(month)
        else:
            str_month = str(month)
        print(str_month)

        catch = []

        # 读取该月份的渔获量数据
        file_tuna = r'G:\科研\金枪鱼\研究方向\Fish Distribution\归一化重构/' + tuna + '归一化渔获量(全区域).csv'
        data_tuna = pd.read_csv(file_tuna, usecols=['Year', 'Month', 'LatC1', 'LonC1', tuna])
        # 筛选该年该月的所有数据
        df_tuna = data_tuna[(data_tuna['Year'] == year) & (data_tuna['Month'] == month)]
        if len(df_tuna) == 0:
            continue
        df_tuna = df_tuna.groupby(['Year', 'Month', 'LatC1', 'LonC1'])[tuna].sum().reset_index()

        for index, row in df_tuna.iterrows():  # 逐次添加该月有渔获的每个网格
            lat_fish = row['LatC1']
            lon_fish = row['LonC1']
            tunaCatch = row[tuna]
            catch.append([lat_fish, lon_fish, tunaCatch, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # 获取该月的日期
        if month < 12:
            date_range = (datetime.datetime(year, month + 1, 1) - datetime.datetime(year, month, 1)).days
        else:
            date_range = (datetime.datetime(year + 1, 1, 1) - datetime.datetime(year, month, 1)).days
        dates = [datetime.datetime(year, month, 1) + datetime.timedelta(days=d) for d in range(date_range)]

        # 读取该月每天的匹配网格数据，并将信息添加到catch中
        for date in dates:
            date0 = date.strftime('%Y-%m-%d')
            print(date0)
            file_bin = r'F:\Data\东太平洋围网金枪鱼数据\网格涡旋匹配结果(旧)/' + date0 + '_bin.pkl'
            with open(file_bin, 'rb') as f:
                data_bin = pickle.load(f)

            for catch_one in catch:

                lat = catch_one[0]
                lon = catch_one[1]
                i, j = np.where(
                    (np.around(data_bin[0, :, :], 2) == (lat - 0.5)) & (np.around(data_bin[1, :, :], 2) == (lon - 0.5)))
                if len(i) == 0 and len(j) == 0:
                    continue
                data_bin_box = data_bin[2, i[0]:i[0] + 5, j[0]:j[0] + 5]

                catch_one[3] += np.count_nonzero((0 < data_bin_box) & (data_bin_box <= 0.5))
                catch_one[4] += np.count_nonzero((0.5 < data_bin_box) & (data_bin_box <= 1))
                catch_one[5] += np.count_nonzero((1 < data_bin_box) & (data_bin_box <= 1.5))
                catch_one[6] += np.count_nonzero((1.5 < data_bin_box) & (data_bin_box <= 2))

                catch_one[7] += np.count_nonzero((-0.5 <= data_bin_box) & (data_bin_box <= 0))
                catch_one[8] += np.count_nonzero((-1 <= data_bin_box) & (data_bin_box < -0.5))
                catch_one[9] += np.count_nonzero((-1.5 <= data_bin_box) & (data_bin_box < -1))
                catch_one[10] += np.count_nonzero((-2 <= data_bin_box) & (data_bin_box <= -1.5))

                catch_one[11] += np.count_nonzero(np.isnan(data_bin_box))

        if len(catch) > 0:
            kArray = np.concatenate((kArray, np.array(catch)), axis=0)
        else:
            continue


result = kArray[(kArray[:, 0] > 10) | (kArray[:, 0] < -10)]
# 将网格面积进行转换
result[:, 3:] *= 12100/25

if len(result) < 9:
    print('拟合方程数量不足，无法求解')
else:
    print(f'拟合方程数量为{len(result)}')
# 最小二乘法求解Ax=b
A = result[:, 3:]  # 系数矩阵
b = result[:, 2]  # 矩阵b
x, resid, rank, s = np.linalg.lstsq(A, b)
x = np.round(x, decimals=7)
# k值结果保存至G:\科研\论文绘图\渔获量系数(2010~2021).xlsx
print(f'系数运算结果为{x}')