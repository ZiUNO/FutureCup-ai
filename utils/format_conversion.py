# -*- coding: utf-8 -*-
"""
* @Author: ziuno
* @Software: PyCharm
* @Time: 2019/3/24 10:35
"""

import os
import csv
import threading
import time
import xml.etree.ElementTree as ET

from PIL import Image
from multiprocessing.dummy import Pool as ThreadPool

from utils.ROI_selection import roi_selection

THREAD_COUNT = 128


class VOC(object):
    @staticmethod
    def convert_to_voc(src_dir_path, aim_dir_path):
        """
        指定数据集文件夹和目的文件夹，生成VOC格式数据集
        :param src_dir_path: 源文件夹路径
        :param aim_dir_path: 目的文件夹路径
        """
        # 新建所需的新文件夹
        annotations_dir_path = os.path.join(aim_dir_path, 'Annotations')
        imagesets_dir_path = os.path.join(aim_dir_path, 'ImageSets')
        jpegimages_dir_path = os.path.join(aim_dir_path, 'JPEGImages')
        imagesets_main_dir_path = os.path.join(imagesets_dir_path, 'Main')
        new_dirs = [aim_dir_path, annotations_dir_path, imagesets_dir_path, jpegimages_dir_path,
                    imagesets_main_dir_path]
        _ = [os.makedirs(new_dir) for new_dir in new_dirs if not os.path.exists(new_dir)]
        # 读取csv数据并保存在info中
        info_path = 0
        for i in os.listdir(src_dir_path):
            if i.endswith(".csv"):
                info_path = os.path.join(src_dir_path, i)
        old_info = []
        with open(info_path) as f:
            reader = csv.reader(f)
            for i, item in enumerate(reader):
                if i == 0:
                    continue
                old_info.append([os.path.sep.join([src_dir_path, item[0][:2], item[0] + '_a.jpg'])] + item[1:])
        # 图片重命名并转存在相应的文件夹
        start_time = time.time()
        print('正在进行图片转存&重命名...', end='')
        new_info = []
        for i, item in enumerate(old_info):
            image_new_path = os.path.join(jpegimages_dir_path, '%06d.jpg' % i)
            new_info.append([image_new_path] + item[1:])
            if os.path.exists(image_new_path):
                continue
            image_old_path = item[0]
            image = Image.open(image_old_path)
            image.save(image_new_path)
        print('cost %d s' % (time.time() - start_time))
        # 将重命名后的生数据保存，用于ROI确定感兴趣区域
        tmp_raw_info_file_name = 'tmp_raw_info.csv'
        tmp_raw_info_file_path = os.path.join(aim_dir_path, tmp_raw_info_file_name)
        with open(tmp_raw_info_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows([['jpg', 'x', 'y', 'judge']])
            writer.writerows(new_info)
        del old_info
        del new_info
        # 读取生数据生成ROI数据csv文件
        tmp_roi_info_file_name = 'tmp_roi_info.csv'
        tmp_roi_info_file_path = os.path.join(aim_dir_path, tmp_roi_info_file_name)
        start_time = time.time()
        print('正在框定ROI...', end='')
        roi_selection(tmp_raw_info_file_path, tmp_roi_info_file_path)
        print('cost %d s' % (time.time() - start_time))
        os.remove(tmp_raw_info_file_path)  # 注释该行可保留生数据
        # 根据roi数据生成xml和txt文件
        tmp_xml_info_dir = annotations_dir_path
        t1 = threading.Thread(target=XML.convert_to_xml, args=(tmp_roi_info_file_path, tmp_xml_info_dir,))
        t2 = threading.Thread(target=TXT.convert_to_txt, args=(tmp_roi_info_file_path, imagesets_main_dir_path,))
        start_time = time.time()
        print('正在生成xml文件...')
        t1.start()
        print('正在生成txt文件...')
        t2.start()
        t1.join()
        t2.join()
        print('生成xml文件和txt文件--cost %d s' % (time.time() - start_time))
        if os.path.exists(tmp_roi_info_file_path):
            os.remove(tmp_roi_info_file_path)  # 注释该行可保留roi数据


class XML(object):
    __xml_dir_path = 0
    __folder = 0

    @staticmethod
    def convert_to_xml(src_file_path, aim_dir_path):
        XML.__xml_dir_path = aim_dir_path
        XML.__folder = aim_dir_path.split(os.path.sep)[3]
        info = []
        pool = ThreadPool(THREAD_COUNT)
        with open(src_file_path, 'r') as f:
            reader = csv.reader(f)
            for i, item in enumerate(reader):
                if i == 0:
                    continue
                info.append(item)
        pool.map(XML.__save_as_xml, info)
        pool.close()
        pool.join()

    @staticmethod
    def __save_as_xml(item):
        annotation = ET.Element("annotation")
        folder = ET.SubElement(annotation, "folder")
        folder.text = XML.__folder
        filename = ET.SubElement(annotation, "filename")
        filename.text = item[0].split(os.path.sep)[-1]
        save_name = item[0].split(os.path.sep)[-1][:-4] + '.xml'
        source = ET.SubElement(annotation, "source")
        database = ET.SubElement(source, "database")
        database.text = '?'
        annotation_ = ET.SubElement(source, "annotation")
        annotation_.text = '?'
        image = ET.SubElement(source, "image")
        image.text = '?'
        flickrid = ET.SubElement(source, "flickrid")
        flickrid.text = '?'
        owner = ET.SubElement(annotation, "owner")
        flickrid_ = ET.SubElement(owner, "flickrid")
        flickrid_.text = "?"
        size = ET.SubElement(annotation, "size")
        width = ET.SubElement(size, "width")
        height = ET.SubElement(size, "height")
        depth = ET.SubElement(size, "depth")
        depth.text = '1'
        with Image.open(item[0]) as img:
            width.text = str(img.size[0])
            height.text = str(img.size[1])
        segmented = ET.SubElement(annotation, "segmented")
        segmented.text = 0  # 是否用于分割
        object_ = ET.SubElement(annotation, "object")
        name = ET.SubElement(object_, "name")
        name.text = item[5]
        pose = ET.SubElement(object_, "pose")
        pose.text = "Unspecified"
        truncated = ET.SubElement(object_, "truncated")
        truncated.text = 0  # 是否被裁剪，0完整，1不完整
        difficult = ET.SubElement(object_, "difficult")
        difficult.text = 0
        bndbox = ET.SubElement(object_, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = item[1]
        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = item[2]
        xmax = ET.SubElement(bndbox, "xmax")
        xmax.text = item[3]
        ymax = ET.SubElement(bndbox, "ymax")
        ymax.text = item[4]
        et = ET.ElementTree(annotation)
        save_path = os.path.join(XML.__xml_dir_path, save_name)
        et.write(save_path, encoding='utf-8', xml_declaration=True)


class TXT(object):
    @staticmethod
    def convert_to_txt(src_file_path, aim_dir, train_trainval_test_val_scale="1:1:1:1"):
        pass
