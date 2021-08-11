import sys
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
        super().__init__()
        self.setupUi(self)

        self.cap = None
        self.lm = lm.label_manager()
        self.log = log_manager.log_manager()

        
        self.BTN_OPEN.clicked.connect(self.btnOpenClicked)
        self.BTN_CAPTURE.clicked.connect(self.btnCaptureClicked)
        self.BTN_THUMBNAIL.clicked.connect(self.btnFolderOpenClicked)
        self.BTN_BINARY.clicked.connect(self.btnBinaryClicked)
        self.BTN_EDGE.clicked.connect(self.btnEdgeClicked)
               
        
        
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


        self.handleFullScreen()
        self.btnOpenClicked()


    def cam_timer_timeout(self):
        _, frame = self.cap.read()
        
        if self.binary_flag:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, bin = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            bin = cv2.cvtColor(bin, cv2.COLOR_GRAY2BGR)
            self.lm.view_original_image(self.LABEL_IMAGE_VIEW, bin, True)
        if self.edge_flag:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edge = cv2.Canny(gray, 150, 200)
            edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
            self.lm.view_original_image(self.LABEL_IMAGE_VIEW, edge, True)
        try:
            self.lm.view_original_image(self.LABEL_LIVE_IMAGE_VIEW, frame, True)
            
        except Exception as error:
            self.log.print_log(str(error), self.TE_LOG, 'red')    
        
    
    def handleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self.changeTabSize(self.VIEW_TAB)
        # self.changeTabSize(self.WORK_TAB)
        # self.changeLabelSize(self.WORK_TAB,self.LABEL_IMAGE_VIEW)


    def changeLabelText(self, label, text):
        label.setText(text)

    def btnFolderOpenClicked(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.zc.default_path))
    
    def btnBinaryClicked(self):
        print(self.binary_flag)
        if not self.binary_flag:
            self.BTN_BINARY.setStyleSheet('QPushButton{background-color:#FA4F41;border-radius:5px;\
                                        font: bold 10pt "Noto Sans KR"; color:white;}\
                                        QPushButton:hover{background-color:rgba(250, 155, 155,100);}\
                                        QPushButton:pressed{background-color:rgba(250, 155, 155,150);}')  
            self.binary_flag = True
        else:
            self.BTN_BINARY.setStyleSheet('QPushButton{background-color:#24ACAC;border-radius:5px;\
                                        font: bold 10pt "Noto Sans KR"; color:white;}\
                                        QPushButton:hover{background-color:rgba(135, 194, 221, 100);}\
                                        QPushButton:pressed{background-color:rgba(135, 194, 221, 150);}')  
            self.binary_flag = False
    
    def btnEdgeClicked(self):
        if not self.edge_flag:
            self.BTN_EDGE.setStyleSheet('QPushButton{background-color:#FA4F41;border-radius:5px;\
                                    font: bold 10pt "Noto Sans KR"; color:white;}\
                                    QPushButton:hover{background-color:rgba(250, 155, 155,100);}\
                                    QPushButton:pressed{background-color:rgba(250, 155, 155,150);}')  
            self.edge_flag = True                                    
        else:
            self.BTN_EDGE.setStyleSheet('QPushButton{background-color:#24ACAC;border-radius:5px;\
                                        font: bold 10pt "Noto Sans KR"; color:white;}\
                                        QPushButton:hover{background-color:rgba(135, 194, 221, 100);}\
                                        QPushButton:pressed{background-color:rgba(135, 194, 221, 150);}')  
            self.edge_flag = False                                        
        


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
        file_name = f'{now.tm_year:02d}{now.tm_mon:02d}{now.tm_mday:02d}-{now.tm_hour:02d}{now.tm_min:02d}{now.tm_sec:02d}'
        self.zc.capture(file_name)
        color_img = self.zc.get_color_img()
        color_depth, real_depth = self.zc.get_depth_img()
        self.lm.view_original_image(self.LABEL_LIVE_IMAGE_VIEW, color_img)
        self.lm.view_original_image(self.LABEL_LIVE_DEPTH_VIEW, color_depth)
        cv2.imwrite(f'./_capture/{file_name}-x.tiff', real_depth[:,:,0])
        cv2.imwrite(f'./_capture/{file_name}-y.tiff', real_depth[:,:,1])
        cv2.imwrite(f'./_capture/{file_name}-z.tiff', real_depth[:,:,2])


        color_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(f'./_capture/{file_name}-color.png', color_img)

        self.log.print_log('캡쳐되었습니다', self.TE_LOG)
        self.zc.visualizer.run()
        self.zc.visualizer.destroy_window()

    

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





