# -*- coding: utf-8 -*-

import sys
# from typing_extensions import ParamSpecKwargs
import resource_rc
import time
import log_manager
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import common
import label_manager as lm
import json
import cv2



form_class = uic.loadUiType("mainwindow.ui")[0]

class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        w = int(self.width()/self.count())
        return QSize(w, size.height())

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super(MyWindow, self).__init__() 
        # super().__init__()
        self.setupUi(self)

        self.cap = None
        self.lm = lm.label_manager()
        self.log = log_manager.log_manager()

        
        self.BTN_OPEN.clicked.connect(self.btnOpenClicked)
        self.BTN_CAPTURE.clicked.connect(self.btnCaptureClicked)
        self.BTN_THUMBNAIL.clicked.connect(self.btnFolderOpenClicked)
        
        self.RADIO_ORIGINAL.clicked.connect(self.radioOperation)
        self.RADIO_BINARY.clicked.connect(self.radioOperation)
        self.RADIO_EDGE.clicked.connect(self.radioOperation)

        self.SLIDER_BIN_TH.valueChanged.connect(self.valueCahnaged)
        self.SLIDER_EDGE_TH1.valueChanged.connect(self.valueCahnaged)
        self.SLIDER_EDGE_TH2.valueChanged.connect(self.valueCahnaged)



        ###캠 타이머 설정         
        self.cam_timer = QTimer()
        self.cam_timer.timeout.connect(self.cam_timer_timeout)

        ###숏컷 설정            
        self.shortcutCamOpen = QShortcut(self)
        self.shortcutCamOpen.setKey(QKeySequence('F2'))
        self.shortcutCamOpen.setContext(Qt.ApplicationShortcut)
        self.shortcutCamOpen.activated.connect(self.btnCaptureClicked)

        self.shortcutFull = QShortcut(self)
        self.shortcutFull.setKey(QKeySequence('F11'))
        self.shortcutFull.setContext(Qt.ApplicationShortcut)
        self.shortcutFull.activated.connect(self.handleFullScreen)

        self.binary_flag = False
        self.edge_flag = False
        self.original_flag = False

        self.operation_type =0
        
        self.threshold_value = self.SLIDER_BIN_TH.value()
        self.edge_th1 = self.SLIDER_EDGE_TH1.value()
        self.edge_th2 = self.SLIDER_EDGE_TH2.value()


        self.handleFullScreen()
        self.btnOpenClicked()


    def cam_timer_timeout(self):
        _, frame = self.cap.read()

        if self.operation_type==0:
            try:
                self.lm.view_original_image(self.LABEL_IMAGE_VIEW, frame, True)
            
            except Exception as error:
                self.log.print_log(str(error), self.TE_LOG, 'red') 

        elif self.operation_type==1:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, bin = cv2.threshold(gray, self.threshold_value, 255, cv2.THRESH_BINARY)
            bin = cv2.cvtColor(bin, cv2.COLOR_GRAY2BGR)
            self.lm.view_original_image(self.LABEL_IMAGE_VIEW, bin, True)

        elif self.operation_type==2:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edge = cv2.Canny(gray, self.edge_th1, self.edge_th2)
            edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
            self.lm.view_original_image(self.LABEL_IMAGE_VIEW, edge, True)


    def handleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


    def changeLabelText(self, label, text):
        label.setText(text)

    def btnFolderOpenClicked(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.zc.default_path))
    
   
    def radioOperation(self):
        if self.RADIO_ORIGINAL.isChecked():
            self.operation_type=0
            self.SLIDER_BIN_TH.setEnabled(False)
            self.SLIDER_EDGE_TH1.setEnabled(False)
            self.SLIDER_EDGE_TH2.setEnabled(False)
        elif self.RADIO_BINARY.isChecked():
            self.operation_type=1
            self.SLIDER_BIN_TH.setEnabled(True)
            self.SLIDER_EDGE_TH1.setEnabled(False)
            self.SLIDER_EDGE_TH2.setEnabled(False)
        elif self.RADIO_EDGE.isChecked():
            self.operation_type=2
            self.SLIDER_BIN_TH.setEnabled(False)
            self.SLIDER_EDGE_TH1.setEnabled(True)
            self.SLIDER_EDGE_TH2.setEnabled(True)

    def valueCahnaged(self):
        self.threshold_value = self.SLIDER_BIN_TH.value()
        self.edge_th1 = self.SLIDER_EDGE_TH1.value()
        self.edge_th2 = self.SLIDER_EDGE_TH2.value()
        pass


    def btnOpenClicked(self):
        if not self.cam_timer.isActive():
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    self.log.print_log('카메라 연결 실패', self.TE_LOG, 'red')
                else:
                    self.cam_timer.start(50)
                    self.BTN_OPEN.setStyleSheet("QPushButton{image:url(:/icon/icon/lidar-selected.jpg); border:0px;}")
                    self.log.print_log('카메라 연결', self.TE_LOG)
            except Exception as error:
                self.log.print_log(str(error), self.TE_LOG, 'red')
        else:
            self.BTN_OPEN.setStyleSheet(
                "QPushButton{image:url(:/icon/icon/lidar-normal.jpg); border:0px}; QPushButton:hover{image:url(:/icon/icon/lidar-over.jpg); border:0px;}")

    def btnCaptureClicked(self):
        now = time.localtime()
        file_name = 'test'
        # file_name = f'{now.tm_year:02d}{now.tm_mon:02d}{now.tm_mday:02d}-{now.tm_hour:02d}{now.tm_min:02d}{now.tm_sec:02d}'

        # cv2.imwrite(f'./_capture/{file_name}-x.tiff', real_depth[:,:,0])
        # cv2.imwrite(f'./_capture/{file_name}-y.tiff', real_depth[:,:,1])
        # cv2.imwrite(f'./_capture/{file_name}-z.tiff', real_depth[:,:,2])


        color_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
        # cv2.imwrite(f'./_capture/{file_name}-color.png', color_img)

        self.log.print_log('캡쳐되었습니다', self.TE_LOG)


    

    def changeTabSize(self, tab):
        width = tab.width();
        tabCount =tab.count();
        tabWidth = width / tabCount -3

        style = """QTabBar::tab
        {
            background:rgb(59, 65, 89);
            color: #7F7F7F;
        	font: bold 11pt  "Noto Sans KR";
            min-height: 25px;
            margin-left: 2px;
            margin-right: 1px;
        	border-bottom: 5px solid rgba(255, 255, 255,20);"""

        style+='width:%ipx;}' % tabWidth

        style+="""QTabWidget::pane {
            border: 2px solid #393F4D;}
            QTabBar::tab:selected
        {
	        font: bold 11pt  "Noto Sans KR";
	        border-bottom: 5px solid #24ACAC;
            color: white;
        }
        QTabBar::tab:hover:!selected
        {
            background:rgb(69, 75, 99);
            color: white;
	        font: bold 11pt  "Noto Sans KR";
	        border-bottom: 5px solid rgba(255, 255, 255,20);
        }

        QTabBar::tab:pressed
        {
            font: 11pt  "Noto Sans KR Black";
            border-bottom: 5px solid rgb(119, 199, 200);
            color: white;
            background:rgb(89, 95, 119);

        }"""


        tab.setStyleSheet(style)

        print('self.tab.width(): ', self.tab.width())

    def changeLabelSize(self, tab, label):
        defalut_width = 640
        defalut_height = 480

        width = tab.width()-13

        rate = width/defalut_width

        label.move(5,5)
        label.setFixedWidth(defalut_width*rate)
        label.setFixedHeight(defalut_height*rate)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()





