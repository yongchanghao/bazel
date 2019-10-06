# -*- coding:utf-8 -*-

"""
For homework 1
"""

import cv2
import numpy as np

from py.qrcode.QRMatrix import QRMatrix

raw_pic = "py/qrcode/pics/sample0.png"

if __name__ == "__main__":
    img = cv2.imread(raw_pic, 1)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(img_gray, 100, 200)

    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy[0]
    found = []
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c += 1
        if c >= 5:
            found.append(i)
    img_dc = img.copy()
    for i in found:
        cv2.drawContours(img_dc, contours, i, (0, 255, 0), 2)

    draw_img = img.copy()
    boxes = []

    unit_length = 0
    for i in found:
        rect = cv2.minAreaRect(contours[i])
        box = cv2.boxPoints(rect)
        unit_length = (max(map(lambda x: x[0], box)) - min(map(lambda x: x[0], box)) + 1) // 7
        box = np.int0(box)
        cv2.drawContours(draw_img, [box], 0, (0, 0, 255), 2)
        box = map(tuple, box)
        boxes.append(box)

    Xs = []
    Ys = []

    for box in boxes:
        for point in box:
            Xs.append(point[0])
            Ys.append(point[1])

    """
    Get the useful area.
    """
    x1 = min(Xs)
    y1 = min(Ys)
    x2 = max(Xs)
    y2 = max(Ys)

    roi = img_gray[y1:y2, x1:x2]

    """
    Make the image to bitmap, resize the QR code to 1 unit for each binary block.
    FYI, The version of QR code is 17 + {{version}} * 4.
    """
    unit_length = int(unit_length)
    version_size = int(round(roi.shape[0] / unit_length))
    bitmap = np.ndarray((version_size, version_size))
    for i in range(version_size):
        cur_x = i * unit_length + unit_length // 2
        for j in range(version_size):
            cur_y = j * unit_length + unit_length // 2
            bitmap[i, j] = (255 if roi[cur_x][cur_y] >= 127 else 0)
    assert (bitmap.shape[0] - 17) % 4 == 0

    print(QRMatrix("decode", bitmap).decode())
