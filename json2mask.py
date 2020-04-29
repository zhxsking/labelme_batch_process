# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 19:35:17 2018
@author: zhxsking

弹出对话框选择json文件夹批量将文件夹下json文件转换为mask图像，参考了labelme的json_to_dataset.py
json文件所在文件夹同级目录下需有img文件夹保存原图像
文件夹结构前后为：
    +-- json         -->    +-- json
    |   +-- *.json          |   +-- *.json
    +-- img                 +-- img
    |   +-- *.jpg           |   +-- *.jpg
                            +-- mask
                                +-- *.jpg
"""


import base64
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog
import numpy as np
from labelme import utils
from labelme.utils.draw import label_colormap
import PIL.Image
from tqdm import tqdm


MODE = 'BW' # 保存的mask图片类型，二值图为BW，彩图为RGB

if __name__ == '__main__':
    # 打开json文件夹对话框
    root = tk.Tk()
    json_path = filedialog.askdirectory()
    root.withdraw()
    if not(json_path): sys.exit(0)
    json_names = os.listdir(json_path)

    pbar = tqdm(json_names) # 进度条
    for json_file in pbar:
        pbar.set_description("Processing %s" % json_file)
        # 读取json文件
        data = json.load(open(os.path.join(json_path, json_file)))
        # 读取原图片数据
        if data['imageData']:
            imageData = data['imageData']
        else:
            # 定位到json所在文件夹同级下的img文件夹中的图片
            imagePath = os.path.join(os.path.abspath(os.path.join(json_path,os.path.pardir)), 'img', data['imagePath'])
            with open(imagePath, 'rb') as f:
                imageData = f.read()
                imageData = base64.b64encode(imageData).decode('utf-8')
        img = utils.img_b64_to_arr(imageData)
        # 将标记的json数据转换为图片
        label_name_to_value = {'_background_': 0}
        for shape in sorted(data['shapes'], key=lambda x: x['label']):
            label_name = shape['label']
            if label_name in label_name_to_value:
                label_value = label_name_to_value[label_name]
            else:
                label_value = len(label_name_to_value)
                label_name_to_value[label_name] = label_value
        lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)
        # 保存图片
        out_dir = os.path.join(os.path.abspath(os.path.join(json_path,os.path.pardir)), 'mask')
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        save_name = os.path.join(out_dir, json_file.split('.')[0]+'.jpg')
        if MODE == 'BW':
            lbl_tmp = lbl * 255
            lbl_tmp[lbl_tmp>255] = 255
            lbl_pil = PIL.Image.fromarray(lbl_tmp.astype(np.uint8))
            lbl_pil.convert('1').save(save_name)
        elif MODE == 'RGB':
            lbl_pil = PIL.Image.fromarray(lbl.astype(np.uint8))
            colormap = label_colormap(255)
            lbl_pil.putpalette((colormap * 255).astype(np.uint8).flatten())
            lbl_pil.convert('RGB').save(save_name)
        else:
            print('save mode error!')
            sys.exit(0)

    print('Saved to: %s' % out_dir)

