import fitz
import re
import os
import cv2
import numpy as np
import shutil


def save_pdf_img(file):
    """
    提取PDF中的图片，并保存在PDF同文件名的文件夹下
    :param file: 需要处理的PDF文件
    """
    # 使用正则表达式来查找图片
    checkXO = r"/Type(?= */XObject)"
    checkIM = r"/Subtype(?= */Image)"
    # 打开pdf
    doc = fitz.open(file)

    save_path = file.replace('.pdf', '')

    if os.path.exists(save_path):
        shutil.rmtree(save_path)

    os.mkdir(save_path)

    # 图片计数
    imgcount = 0
    # 获取对象数量长度
    lenXREF = doc.xref_length()

    # 打印PDF的信息
    print("文件名:{}, 页数: {}, 对象: {}".format(file, len(doc), lenXREF - 1))

    # 遍历每一个图片对象
    for i in range(1, lenXREF):
        # 定义对象字符串
        text = doc.xref_object(i)
        # print(i,text)
        isXObject = re.search(checkXO, text)
        # 使用正则表达式查看是否是图片
        isImage = re.search(checkIM, text)
        # 如果不是对象也不是图片，则continue
        if not isXObject or not isImage:
            continue
        imgcount += 1
        # 根据索引生成图像
        pix = fitz.Pixmap(doc, i)
        # 根据pdf的路径生成图片的名称
        new_name = f'{i}.png'
        # 如果pix.n<5,可以直接存为PNG
        if pix.n < 5:
            pix.save(os.path.join(save_path, new_name))
        # 否则先转换CMYK
        else:
            pix0 = fitz.Pixmap(fitz.csRGB, pix)
            pix0.save(os.path.join(save_path, new_name))
            pix0 = None
        # 释放资源
        pix = None
        print("提取了{}张图片".format(imgcount))


def flip(file):
    """
    将图片水平翻转，并切割为左边、右边两张图片
    :param file: 翻转的图片
    """
    image = cv2.imdecode(np.fromfile(file, dtype=np.uint8), -1)
    # 目前所有的pdf文件中的图片都为水平翻转状态的。
    img = cv2.flip(image, 0)
    # 获取宽高
    height = image.shape[0]
    width = image.shape[1]
    # 获取子图片
    img_left = img[0:height, 0:int(width / 2)]
    img_right = img[0:height, int(width * 0.48):width]
    # 保存
    cv2.imencode('.png', img_left)[1].tofile(file + '-1.png')
    cv2.imencode('.png', img_right)[1].tofile(file + '-2.png')


def step1_pdf_to_image(root_path):
    """
    遍历指定文佳佳，并提取PDF中的图片
    :param root_path: 遍历的文件夹
    """
    for root, dirs, files in os.walk(root_path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            if filename.endswith('.pdf'):
                save_pdf_img(filename)


def step2_image_split(root_path):
    """
    遍历指定文件夹，并将图片切割为左边、右边两张图片
    :param root_path:
    """
    for root, dirs, files in os.walk(root_path, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            if filename.endswith('.png'):
                flip(filename)


if __name__ == '__main__':
    # 指定的文件夹
    root_path = r'..\resources'
    step1_pdf_to_image(root_path)
    step2_image_split(root_path)
