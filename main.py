# -*- coding: utf-8 -*-
"""
* @Author: ziuno
* @Software: PyCharm
* @Time: 2019/3/24 10:58
"""

from utils.format_conversion import *

if __name__ == '__main__':
    src_dir_path = r"G:\未来杯\dataset\af2019-cv-training-20190312\af2019-cv-training-20190312"
    aim_dir_path = r"G:\未来杯\dataset\VOC_conversion"
    VOC.convert_to_voc(src_dir_path, aim_dir_path)
