#! /usr/bin/env/python3
# -*- coding=utf-8 -*-
"""
======================模块功能描述=========================    
       @File     : 网格-涡旋匹配(多进程).py
       @IDE      : PyCharm
       @Author   : Wukkkkk
       @Date     : 2024/4/15 下午7:29
       @Desc     : 
=========================================================   
"""
import datetime
import pickle
from multiprocessing import Pool
import numpy as np
import xarray as xr
import os
from eddy_shape import cau_r


def process_day(date_str, lat_grid, lon_grid):
    print(date_str)
    file = 'F:\\东太平洋围网金枪鱼数据\\网格-涡旋匹配结果\\' + date_str + '_bin.pkl'
    if os.path.exists(file):
        print(f"File for {date_str} already exists. Skipping...")
        return
    # 创建结果数组
    result = np.zeros((4, lon_grid.shape[0], lon_grid.shape[1]))  # # 第一维存放网格纬度，第二维经度，第三维归一化半径，第四维所匹配的涡旋编号
    result[0] = lat_grid
    result[1] = lon_grid
    result[2:] = np.nan

    # 读取这一天的涡旋数据
    file_ae = 'F:\\Eddy\\Anticyclonic\\' + date_str + '_dir.nc'
    data_ae = xr.open_dataset(file_ae, decode_cf=True)
    file_ce = 'F:\\Eddy\\Cyclonic\\' + date_str + '_dir.nc'
    data_ce = xr.open_dataset(file_ce, decode_cf=True)

    '''开始匹配'''
    for i in range(350):
        for j in range(400):
            lat_g = result[0, i, j]
            lon_g = result[1, i, j] + 360  # 由于涡旋经度为0-360,因此将网格的经度+360便于匹配
            num = 5  # 数字表示搜寻涡旋的范围，多少度

            # 网格附近的AE索引
            lats_ae = np.array(data_ae.latitude_max[:])  # AE涡心纬度
            lons_ae = np.array(data_ae.longitude_max[:])  # AE涡心经度
            index_ae = np.where((lat_g - num <= lats_ae) & (lats_ae <= lat_g + num) &
                                (lon_g - num <= lons_ae) & (lons_ae < lon_g + num))[0]
            # 网格附近的CE索引
            lats_ce = np.array(data_ce.latitude_max[:])  # CE涡心纬度
            lons_ce = np.array(data_ce.longitude_max[:])  # CE涡心经度
            index_ce = np.where((lat_g - num <= lats_ce) & (lats_ce <= lat_g + num) &
                                (lon_g - num <= lons_ce) & (lons_ce < lon_g + num))[0]

            if len(index_ae) == 0 and len(index_ce) == 0:
                continue
            '''分别遍历周围的AE和CE并计算网格与其距离，找出距离最小的放入数组中，并保存其涡旋编号'''

            aes_r = []
            ces_r = []
            aes_track = []
            ces_track = []
            # AE
            for m in index_ae:
                lat = float(data_ae.latitude_max[:][m])  # 涡心纬度
                lon = float(data_ae.longitude_max[:][m])  # 涡心经度
                observation_flag = bool(data_ae.observation_flag[:][m] - 1)  # 涡旋的标志，0是观测的涡旋，1是插值的涡旋
                if not observation_flag:
                    continue
                track = float(data_ae.track[:][m])  # 涡旋编号
                contour_lon = np.array(data_ae.effective_contour_longitude[:][m])  # 涡旋边界经度
                contour_lat = np.array(data_ae.effective_contour_latitude[:][m])  # 涡旋边界纬度
                r_ae = cau_r(contour_lon, contour_lat, lon, lat, lon_g, lat_g)[0]
                if r_ae <= 2:
                    aes_r.append(r_ae)
                    aes_track.append(track)
            # CE
            for m in index_ce:
                lat = float(data_ce.latitude_max[:][m])  # 涡心纬度
                lon = float(data_ce.longitude_max[:][m])  # 涡心经度
                observation_flag = bool(data_ce.observation_flag[:][m] - 1)  # 涡旋的标志，0是观测的涡旋，1是插值的涡旋
                if not observation_flag:
                    continue
                track = float(data_ce.track[:][m])  # 涡旋编号
                contour_lon = np.array(data_ce.effective_contour_longitude[:][m])  # 涡旋边界经度
                contour_lat = np.array(data_ce.effective_contour_latitude[:][m])  # 涡旋边界纬度
                r_ce = cau_r(contour_lon, contour_lat, lon, lat, lon_g, lat_g)[0]
                if r_ce <= 2:
                    ces_r.append(r_ce)
                    ces_track.append(track)

            # 找出AE和CE两个列表中的距离最小值，记录--有多种情况
            if not aes_r and not ces_r:  # AE和CE都为空列表
                continue
            if not aes_r:  # AE空列表
                r_min = min(ces_r)
                min_index = ces_r.index(r_min)
                track_min = ces_track[min_index]
                result[2, i, j] = -r_min  # 用正负表示所匹配到的涡旋的类型，+为AE，-为CE
                result[3, i, j] = track_min
                continue
            if not ces_r:  # CE空列表
                r_min = min(aes_r)
                min_index = aes_r.index(r_min)
                track_min = aes_track[min_index]
                result[2, i, j] = r_min
                result[3, i, j] = track_min
                continue
            if aes_r and ces_r:  # AE和CE都非空
                r_min_ae = min(aes_r)
                min_index_ae = aes_r.index(r_min_ae)
                track_min_ae = aes_track[min_index_ae]  # 找出AE中的最小r
                r_min_ce = min(ces_r)
                min_index_ce = ces_r.index(r_min_ce)
                track_min_ce = ces_track[min_index_ce]  # 找出CE中的最小r
                if r_min_ae <= r_min_ce:
                    result[2, i, j] = r_min_ae
                    result[3, i, j] = track_min_ae
                    continue
                else:
                    result[2, i, j] = -r_min_ce
                    result[3, i, j] = track_min_ce
                    continue

    out = 'F:\\东太平洋围网金枪鱼数据\\网格-涡旋匹配结果\\' + date_str + '_bin.pkl'
    with open(out, 'wb') as f:
        pickle.dump(result, f)


def main():
    # 首先把经纬度填入网格的前两维
    lon_values = np.around(np.arange(-150, -70, 0.2), decimals=2)
    lat_values = np.around(np.arange(-30, 40, 0.2), decimals=2)
    lon_grid, lat_grid = np.meshgrid(lon_values, lat_values)

    # 构造日期范围
    date_range = [datetime.date(year, 1, 1) + datetime.timedelta(days=day_num)
                  for year in range(2010, 2011)
                  for day_num in range((datetime.date(year + 1, 1, 1) - datetime.date(year, 1, 1)).days)]

    # 创建进程池
    num_processes = 8
    pool = Pool(processes=num_processes)

    # 并行处理每一天的数据
    pool.starmap(process_day, [(date.strftime('%Y-%m-%d'), lat_grid, lon_grid) for date in date_range])

    # 关闭进程池
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
