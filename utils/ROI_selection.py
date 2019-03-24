# -*- coding: utf-8 -*-
"""
* @Author: ziuno
* @Software: PyCharm
* @Time: 2019/3/24 10:44
"""
import csv


def roi_selection(src_file_path, aim_file_path, x_bias=8, y_bias=8):
    info = []
    with open(src_file_path, 'r') as f:
        reader = csv.reader(f)
        for i, item in enumerate(reader):
            if i == 0:
                continue
            x = int(item[1])
            y = int(item[2])
            tmp_item = [item[0], x - x_bias, y - y_bias, x + x_bias, y + y_bias, item[3]]
            info.append(tmp_item)
    with open(aim_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([['jpg', 'xmin', 'ymin', 'xmax', 'ymax', 'judge']])
        writer.writerows(info)
