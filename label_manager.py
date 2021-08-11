import copy

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage
import common
import numpy as np

class label_manager():
    def __init__(self):
        self.default_path = './_debug'

    def view_original_image(self, label, mat, swap=False):
        if mat is None:
            raise Exception('mat이 비었습니다')
        h, w, c = mat.shape

        new_mat = copy.deepcopy(mat.astype(np.uint8))

        if swap==True:
            img  = QImage(new_mat.data, w, h, w*c, QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(img.rgbSwapped()))
        else:
            img = QImage(new_mat.data, w, h, w*c, QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(img))

        label.show()