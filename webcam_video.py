# —*-coding:utf-8 一*一
"""
作者:LegendLeo
日期:2023年12月09日
"""
import cv2
import numpy as np
from urllib import request

url = "http://192.168.43.212:8080/?action=snapshot"

def downloadImg():
    global url
    with request.urlopen(url) as f:
        data = f.read()
        img1 = np.frombuffer(data, np.uint8)
        # print("img1 shape ", img1.shape) # (83653,)
        img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)
        return img_cv

while True:
    # image = downloadImg()
    image = downloadImg()  # cv2.imread('1.jpg') # 根据路径读取一张图片
    cv2.imshow("frame", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
