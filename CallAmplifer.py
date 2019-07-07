# -*- coding: utf-8 -*-

import sys
from PyQt5.QtGui import *
from Amplifer import *
from Dialog import *
from PyQt5.QtWidgets import *
from stopThreading import StopThreading
import socket
import threading
import webbrowser
import time
import random
import matplotlib
matplotlib.use("Qt5Agg")#声明使用QT5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
font = {'family' : 'MicroSoft YaHei',
              'weight' : 'bold',
              }
# font = {'family':'MicroSoft YaHei',
#         'weight':'bold',
#         'size':'larger'}               # 设置使用的字体（需要显示中文的时候使用）
matplotlib.rc('font',**font)              #设置显示中文，与字体配合使用
matplotlib.rc('font',family='MicroSoft YaHei')              #设置显示中文，与字体配合使用
# matplotlib.rcParams['axes.unicode_minus']=False   #   当坐标轴有负号的时候可以显示负号





class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100, title='title'):
        self.title = title
        fig = Figure(figsize=(width, height), dpi=dpi)#创建一个figure,是matplotlib下的figure,而不是matplotlib.pyplot下的figure
        self.axes = fig.add_subplot(111)##将画布分割成1行1列，图像画在从左到右从上到下的第1块
        fig.suptitle('title')
        # self.axes.axis("equal")

        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()


        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        t = arange(0.0, 10.0, 0.01)
        s = 5*sin(2*pi*t)
        self.axes.plot(t, s)
        # self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Sampling value')
        self.axes.grid(True)
        # plt.savefig("./ti.png")


    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Sampling value')
        self.axes.grid(True)
        self.draw()


##################################################
class MyMainWindow(QMainWindow, Ui_MainWindow):
    signal_write_msg = QtCore.pyqtSignal(str)

    def __init__(self, st,parent=None):
        super(MyMainWindow, self).__init__(parent)
#        设置界面图标----------------2019.4.2
        self.setWindowIcon(QIcon('./imag/13.png'))

        self.setupUi(self)
        self.msg = None
        self.port = None
        self.address = None
        self.link = False
        self.client_th = None
        self.client_socket = None
        self.client_address = None
        self.connect()
        self.st=st

        # 数据解析
        self.TX_BUFSIZE = 150
        self.RX_BUFSIZE = 5000

        self.bSerialTXBuff = ['0'] * 50
        self.bASCIITemp = [0, 0]
        self.bNetworkPortType = 0
        self.wCommReadDataStartAddr = 0
        self.wCommReadDataCount = 0
        self.wDataRam = [0] * 100
        self.wRunState1 = 0
        self.wRunState2 = 0
        self.wFaultState = 0
        self.wCommTXDataAddr = 0

        self.m_wFlutterFrequency = 0
        self.m_wFlutterAmplitude = 0
        self.m_wSignalThreshold = 0
        self.m_wStepSignalA = 0
        self.m_wStepSignalB = 0
        self.m_wReferenceValue1 =0
        self.m_wReferenceValue2= 0
        self.m_wReferenceValue3 = 0
        self.m_wReferenceValue4 = 0
        self.wTempReferenceValue1=0
        self.wTempReferenceValue2 = 0
        self.wTempReferenceValue3=0
        self.wTempReferenceValue4 = 0

        self.m_wReferenceValuePositive =0
        self.wCurrentSignalChannal = 8
        self.m_wCurrentKP = 0
        self.m_wCurrentKI = 0
        self.m_wDisplacementKP = 0
        self.m_wDisplacementKI = 0
        self.m_wDisplacementKD = 0
        self.m_wPistonDisplacementKP=0
        self.m_wPistonDisplacementKI=0
        self.m_wPistonDisplacementKD=0

        # 创建TCP/UDP套接字，AF_INET表示使用IPv4地址，SOCK_STREAM表示socket类型为流格式套接字
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tab_2UI()

    def tab_2UI(self):

        self.main_widget = self.tab_2
        dc = MyDynamicMplCanvas(self.main_widget, width=10, height=3, dpi=100, title='Dynamic tracking curve')

    def connect(self):
        """
        控件信号-槽的设置
        :param : QDialog类创建的对象
        :return: None
        """
        self.signal_write_msg.connect(self.write_msg)
        self.pushButton_ip_connect.clicked.connect(self.click_ip_link)
        self.pushButton_ip_disconnect.clicked.connect(self.click_ip_unlink)
        self.pushButton_stap_read.clicked.connect(self.stap_read)
        self.pushButton_stap_set.clicked.connect(self.stap_set)
        self.pushButton_update_program.clicked.connect(self.click_update_program)
        self.pushButton_input_parameter_read.clicked.connect(self.input_parameter_read)
        self.pushButton_input_parameter_set.clicked.connect(self.input_parameter_set)
        self.pushButton_spool_current_read.clicked.connect(self.spool_current_read)
        self.pushButton_spool_current_set.clicked.connect(self.spool_current_set)
        self.pushButton_piston_displacement_read.clicked.connect(self.piston_displacement_read)
        self.pushButton_piston_displacement_set.clicked.connect(self.piston_displacement_set)
        self.pushButton_spool_displacement_read.clicked.connect(self.spool_displacement_read)
        self.pushButton_spool_displacement_set.clicked.connect(self.spool_displacement_set)


    def click_ip_link(self):
        """
        pushbutton_link控件点击触发的槽
        :return: None
        """
        self.tcp_client_start()
        self.link = True
        self.pushButton_ip_disconnect.setEnabled(True)
        self.pushButton_ip_connect.setEnabled(False)

    def click_ip_unlink(self):
        """
        pushbutton_unlink控件点击触发的槽
        :return: None
        """
        self.close_all()
        self.label_6.setPixmap(QtGui.QPixmap(":/pic/imag/icon_enoff.ICO"))

    def click_update_program(self):
        reply = QMessageBox.information(self, "更新程序", "确定更新程序", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply==16384:
            self.click_clear()
            self.msg = '更新程序ing\n'
            self.signal_write_msg.emit("写入")
            self.wDataRam[40] = 1
            self.DataProduce(6, 40, 1)
            self.tcp_send()
            time.sleep(15)
            webbrowser.open('http://10.13.106.216')


    def click_clear(self):
        """
        pushbutton_clear控件点击触发的槽
        :return: None
        """
        self.textBrowser_recv.clear()

    def write_msg(self):
        """
        功能函数，向接收区写入数据的方法
        信号-槽触发
        tip：PyQt程序的子线程中，使用非规定的语句向主线程的界面传输字符是不允许的
        :return: None
        """
        self.textBrowser_recv.insertPlainText(self.msg)

    def close_all(self):
         """
        功能函数，关闭网络连接的方法
        :return:
        """
        # 连接时根据用户选择的功能调用函数
         self.tcp_close()
         self.reset()

    def reset(self):
        """
        功能函数，将按钮重置为初始状态
        :return:None
        """
        self.link = False
        self.pushButton_ip_disconnect.setEnabled(False)
        self.pushButton_ip_connect.setEnabled(True)

    def tcp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        self.click_clear()
        try:
            self.tcp_socket.close()
            if self.link is True:
               self.msg = '已断开网络\n'
               self.signal_write_msg.emit("写入")
               self.st.stop_thread(self.client_th)
        except Exception as ret:
                pass
        try:
            StopThreading.stop_thread(self.client_th)
        except Exception:
            pass


    def tcp_client_start(self):
        """
        功能函数，TCP客户端连接其他服务端的方法
        :return:
        """
        self.click_clear()
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.address = (str(self.lineEdit_ip.text()), int(self.lineEdit_port.text()))
        except Exception as ret:
            self.msg = '请检查目标IP，目标端口\n'
            self.signal_write_msg.emit("写入")
        else:
            try:
                self.msg = '正在连接目标服务器\n'
                self.signal_write_msg.emit("写入")
                self.tcp_socket.connect(self.address)
            except Exception as ret:
                self.msg = '无法连接目标服务器\n'
                self.signal_write_msg.emit("写入")
            else:
                self.client_th = threading.Thread(target=self.tcp_client_concurrency)
                self.client_th.start()
                self.label_6.setPixmap(QtGui.QPixmap(":/pic/imag/icon_enon.ico"))
                self.msg = 'TCP客户端已连接IP:%s端口:%s\n' % self.address
                self.signal_write_msg.emit("写入")

    def tcp_client_concurrency(self):
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return:
        """
        while True:
            recv_msg = self.tcp_socket.recv(1024)
            if recv_msg:
                msg = recv_msg.decode('utf-8')
                self.DateProcess(list(msg))
                self.msg = '来自IP:{}端口:{}:\n{}\n'.format(self.address[0], self.address[1], msg)
                self.signal_write_msg.emit(msg)
            else:
                self.tcp_socket.close()
                self.reset()
                self.msg = '从服务器断开连接\n'
                self.signal_write_msg.emit("写入")
                break

    def tcp_send(self):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            try:
                send_msg=self.bSerialTXBuff
                send_msg =''.join(send_msg)
                send_msg=(str(send_msg)).encode('utf-8')

                 # print(self.bSerialTXBuff)
                self.tcp_socket.send(send_msg)
                self.msg = 'TCP客户端已发送\n'
                self.signal_write_msg.emit(self.msg)

            except Exception as ret:
                self.msg = '发送失败\n'
                self.signal_write_msg.emit("写入")

    def stap_read(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.DataProduce(5,12,5)
            self.tcp_send()
            time.sleep(0.5)
            self.m_wFlutterFrequency = self.wDataRam[12]
            self.m_wFlutterAmplitude = self.wDataRam[13]
            self.m_wSignalThreshold = self.wDataRam[14]
            self.m_wStepSignalA = self.wDataRam[15]
            self.m_wStepSignalB = self.wDataRam[16]
            self.lineEdit_stapA.setText(str(self.m_wStepSignalA))
            self.lineEdit_stapB.setText(str(self.m_wStepSignalB))
            self.lineEdit_Frequency.setText(str(self.m_wFlutterFrequency))
            self.lineEdit_Amplitude.setText(str(self.m_wFlutterAmplitude))
            self.lineEdit_threshold.setText(str(self.m_wSignalThreshold))



    def stap_set(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.m_wStepSignalA=str(self.lineEdit_stapA.text())
            self.m_wStepSignalB=str(self.lineEdit_stapB.text())
            self.m_wFlutterFrequency = str(self.lineEdit_Frequency.text())
            self.m_wFlutterAmplitude = str(self.lineEdit_Amplitude.text())
            self.m_wSignalThreshold  =  str(self.lineEdit_threshold.text())
            self.wDataRam[12] = int(self.m_wFlutterFrequency)
            self.wDataRam[13] = int(self.m_wFlutterAmplitude)
            self.wDataRam[14] = int(self.m_wSignalThreshold)
            self.wDataRam[15] = int(self.m_wStepSignalA)
            self.wDataRam[16] = int(self.m_wStepSignalB)
            self.DataProduce(6,12,5)
            self.tcp_send()

    def input_parameter_read(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.DataProduce(5, 0, 6)
            self.tcp_send()
            time.sleep(0.5)
            self.m_wReferenceValue1 = self.wDataRam[0]
            self.m_wReferenceValue2 = self.wDataRam[1]
            self.m_wReferenceValue3 = self.wDataRam[2]
            self.m_wReferenceValue4 = self.wDataRam[3]
            self.m_wReferenceValuePositive = self.wDataRam[4]  # 0代表是负数，1代表是正数
            self.wCurrentSignalChannal = self.wDataRam[5]
            if self.m_wReferenceValuePositive==0:
                self.lineEdit_input_set.setText('-'+str(self.m_wReferenceValue1))
            else:
                self.lineEdit_input_set.setText(str(self.m_wReferenceValue1))




    def input_parameter_set(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            if self.radioButton_digital.isChecked()==True:
                self.wCurrentSignalChannal = 8
                self.m_wReferenceValue1 = int(self.lineEdit_input_set.text())
                if int(self.m_wReferenceValue1)< 0:
                    self.wTempReferenceValue1 = (-1) * self.m_wReferenceValue1
                    self.m_wReferenceValuePositive = 0
                else:
                    self.wTempReferenceValue1 = self.m_wReferenceValue1
                    self.m_wReferenceValuePositive = 1
                self.wDataRam[0] = int(self.wTempReferenceValue1)
                self.wDataRam[1] = int(self.wTempReferenceValue2)
                self.wDataRam[2] = int(self.wTempReferenceValue3)
                self.wDataRam[3] = int(self.wTempReferenceValue4)
                self.wDataRam[4] = int(self.m_wReferenceValuePositive)
                self.wDataRam[5] = int(self.wCurrentSignalChannal)
                self.DataProduce(6, 0, 6)
                self.tcp_send()
            else:
                self.msg = '请选择输入类型\n'
                self.signal_write_msg.emit("写入")


    def spool_current_read(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.DataProduce(5, 38, 2)
            self.tcp_send()
            time.sleep(0.5)
            self.m_wCurrentKP = self.wDataRam[38]
            self.m_wCurrentKI = self.wDataRam[39]
            self.lineEdit_spool_current_p.setText(str(self.m_wCurrentKP))
            self.lineEdit_spool_current_i.setText(str(self.m_wCurrentKI))

    def spool_current_set(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")

        else:
            self.m_wCurrentKP = str(self.lineEdit_spool_current_p.text())
            self.m_wCurrentKI = str(self.lineEdit_spool_current_i.text())
            self.wDataRam[38] = int(self.m_wCurrentKP)
            self.wDataRam[39] = int(self.m_wCurrentKI)
            self.DataProduce(6,38,2)
            self.tcp_send()

    def spool_displacement_read(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.DataProduce(5, 40,3)
            self.tcp_send()
            time.sleep(0.5)
            self.m_wDisplacementKP = self.wDataRam[40]
            self.m_wDisplacementKI = self.wDataRam[41]
            self.m_wDisplacementKD = self.wDataRam[42]
            self.lineEdit_spool_displacement_p.setText(str(self.m_wDisplacementKP))
            self.lineEdit_spool_displacement_i.setText(str(self.m_wDisplacementKI))
            self.lineEdit_spool_displacement_d.setText(str(self.m_wDisplacementKD))
    def spool_displacement_set(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.m_wDisplacementKP = str(self.lineEdit_spool_displacement_p.text())
            self.m_wDisplacementKI = str(self.lineEdit_spool_displacement_i.text())
            self.m_wDisplacementKD = str(self.lineEdit_spool_displacement_d.text())
            self.wDataRam[40] = int(self.m_wDisplacementKP)
            self.wDataRam[41] = int(self.m_wDisplacementKI)
            self.wDataRam[42] = int(self.m_wDisplacementKD)
            self.DataProduce(6, 40,3)
            self.tcp_send()

    def piston_displacement_read(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.DataProduce(5, 43, 3)
            self.tcp_send()
            time.sleep(0.5)
            self.m_wPistonDisplacementKP = self.wDataRam[43]
            self.m_wPistonDisplacementKI = self.wDataRam[44]
            self.m_wPistonDisplacementKD = self.wDataRam[45]
            self.lineEdit_piston_displacement_p.setText(str(self.m_wPistonDisplacementKP))
            self.lineEdit_piston_displacement_i.setText(str(self.m_wPistonDisplacementKI))
            self.lineEdit_piston_displacement_d.setText(str(self.m_wPistonDisplacementKD))

    def piston_displacement_set(self):
        self.click_clear()
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.m_wPistonDisplacementKP = str(self.lineEdit_piston_displacement_p.text())
            self.m_wPistonDisplacementKI = str(self.lineEdit_piston_displacement_i.text())
            self.m_wPistonDisplacementKD = str(self.lineEdit_piston_displacement_d.text())
            self.wDataRam[43] = int(self.m_wPistonDisplacementKP)
            self.wDataRam[44] = int(self.m_wPistonDisplacementKI)
            self.wDataRam[45] = int(self.m_wPistonDisplacementKD)
            self.DataProduce(6, 43, 3)
            self.tcp_send()

    # bSerialRXBuff[RX_BUFSIZE]=[0]
    # 将用ASCII表示的十六进制数，转换为真实的数据
    def ASCIIToHex(self,RXBuff, wStartAddr, bCount):
        wHex = 0
        for i in range(bCount):
            bTemp = ord(RXBuff[wStartAddr + i])
            if bTemp < 58:
                wHex = wHex * 16 + bTemp - 48
            else:
                wHex = wHex * 16 + bTemp - 55
        return wHex


    def ByteToASCII(self,bByte):
        self.ASCIITemp = int(bByte / 16)
        if self.ASCIITemp > 9:
            self.bASCIITemp[0] = self.ASCIITemp + 55
        else:
            self.bASCIITemp[0] = self.ASCIITemp + 48
        self.ASCIITemp = bByte % 16
        if self.ASCIITemp > 9:
            self.bASCIITemp[1] = self.ASCIITemp + 55
        else:
            self.bASCIITemp[1] = self.ASCIITemp + 48


    def DateProcess(self,sever_recbuf):
        self.bCommFCS = 0
        index = 0
        self.wDataLen = 0
        for index in range(len(sever_recbuf)):
            if '*' == sever_recbuf[index]:
                break
        self.wDataLen = index
        case = sever_recbuf[3]
        if case =='1':
            self.bNetworkPortType = 1
            self.wCommReadDataStartAddr = self.ASCIIToHex(sever_recbuf, 10, 2)
            self.wDataRam[self.wCommReadDataStartAddr]=self.ASCIIToHex(sever_recbuf, 12, 4)
        elif case == '2':
            self.bNetworkPortType = 2
            self.wCommReadDataStartAddr = self.ASCIIToHex(sever_recbuf, 10, 2)
            self.wDataRam[self.wCommReadDataStartAddr] = self.ASCIIToHex(sever_recbuf, 12, 4)
        elif case == '3':
            self.bNetworkPortType = 3
            self.wRunState1 = self.ASCIIToHex(sever_recbuf, 10, 4)
            self.wRunState2 = self.ASCIIToHex(sever_recbuf, 14, 4)
            self.wFaultState = self.ASCIIToHex(sever_recbuf, 18, 4)
        elif case == '4':
            self.bNetworkPortType = 4
            self.wRunState1 = self.ASCIIToHex(sever_recbuf, 10, 4)
            self.wRunState2 = self.ASCIIToHex(sever_recbuf, 14, 4)
            self.wFaultState = self.ASCIIToHex(sever_recbuf, 18, 4)
        elif case == '5':
            self.bNetworkPortType = 5
            self.wCommReadDataStartAddr = self.ASCIIToHex(sever_recbuf, 10, 2)
            # print(self.wCommReadDataStartAddr)
            self.wCommReadDataCount = int((self.wDataLen-14) /4)#前面12个，末尾校验位2位
            # print(self.wCommReadDataCount)
            for i in range(self.wCommReadDataCount):
                self.wDataRam[self.wCommReadDataStartAddr + i] = self.ASCIIToHex(sever_recbuf, i * 4+ 12, 4)
        elif case == '6':
            self.bNetworkPortType = 6
            self.wCommReadDataStartAddr = self.ASCIIToHex(sever_recbuf, 10, 2)
            self.wDataRam[self.wCommReadDataStartAddr] = self.ASCIIToHex(sever_recbuf, 12, 2)
        elif case == '7':
            self.bNetworkPortType = 9
        elif case == '8':
            self.bNetworkPortType = 8


    def DataProduce(self,bCommType, wCommReadDataStartAddr, wCommChangeDateStartCount):
        bCommmFCS = 0
        # del self.bSerialTXBuff[:]
        self.bSerialTXBuff[0] = '@'
        self.bSerialTXBuff[1] = '0'
        self.bSerialTXBuff[2] = '0'
        if 1 == bCommType:
            self.bSerialTXBuff[3] = '1'
        elif 2 == bCommType:
            self.bSerialTXBuff[3] = '2'
        elif 2 == bCommType:
            self.bSerialTXBuff[3] = '2'
        elif 3 == bCommType:
            self.bSerialTXBuff[3] = '3'
        elif 4 == bCommType:
            self.bSerialTXBuff[3] = '4'
        elif 5 == bCommType:
            self.bSerialTXBuff[3] = '5'
        elif 6 == bCommType:
            self.bSerialTXBuff[3] = '6'
        elif 8 == bCommType:
            self.bSerialTXBuff[3] = '8'

        if 1 == bCommType:
            self.ByteToASCII(wCommReadDataStartAddr)
            for i in range(2):
                self.bSerialTXBuff[4 + i] = self.bASCIITemp[i]
            self.wCommTXDataAddr = 6

        elif 2 == bCommType:
            self.ByteToASCII(wCommReadDataStartAddr)
            for i in range(2):
                self.bSerialTXBuff[4 + i] = self.bASCIITemp[i]
            self.ByteToASCII(self.wDataRam[wCommReadDataStartAddr] // 256)
            for i in range(2):
                self.bSerialTXBuff[6 + i] = self.bASCIITemp[i]
            self.ByteToASCII(self.wDataRam[wCommReadDataStartAddr] % 256)
            for i in range(2):
                self.bSerialTXBuff[8 + i] = self.bASCIITemp[i]
            self.wCommTXDataAddr = 10

        elif 4 == bCommType:
            self.wCommTXDataAddr = 4

        elif 5 == bCommType:
            self.ByteToASCII(wCommReadDataStartAddr)
            for i in range(2):
                self.bSerialTXBuff[4 + i] = chr(self.bASCIITemp[i])
            self.wCommTXDataAddr = 6
            self.ByteToASCII(wCommChangeDateStartCount)
            for i in range(2):
                self.bSerialTXBuff[6 + i] = chr(self.bASCIITemp[i])
            self.wCommTXDataAddr = 8

        elif 6 == bCommType:
            self.ByteToASCII(wCommReadDataStartAddr)
            for i in range(2):
                self.bSerialTXBuff[4 + i] = chr(self.bASCIITemp[i])
            self.wCommTXDataAddr = 6
            for i in range(wCommChangeDateStartCount):
                self.ByteToASCII(self.wDataRam[wCommReadDataStartAddr + i] // 256)
                for j in range(2):
                    self.bSerialTXBuff[self.wCommTXDataAddr + j] = chr(self.bASCIITemp[j])

                self.wCommTXDataAddr = self.wCommTXDataAddr + 2
                self.ByteToASCII(self.wDataRam[wCommReadDataStartAddr + i] % 256)
                for z in range(2):
                    self.bSerialTXBuff[self.wCommTXDataAddr + z] = chr(self.bASCIITemp[z])
                self.wCommTXDataAddr = self.wCommTXDataAddr + 2

        elif 8 == bCommType:
            if wCommReadDataStartAddr == 1:
                self.bSerialTXBuff[4] = 'Y'
            elif wCommReadDataStartAddr == 0:
                self.bSerialTXBuff[4] = 'N'
            self.wCommTXDataAddr = 5

        for i in range(self.wCommTXDataAddr):
            bCommmFCS = bCommmFCS^ ord(self.bSerialTXBuff[i])

        self.ByteToASCII(bCommmFCS)
        for i in range(2):
            self.bSerialTXBuff[self.wCommTXDataAddr + i] = chr(self.bASCIITemp[i])
        self.wCommTXDataAddr = self.wCommTXDataAddr + 2
        self.bSerialTXBuff[self.wCommTXDataAddr] = '*'
        self.wCommTXDataLength = self.wCommTXDataAddr




if __name__ == "__main__":

    app = QApplication(sys.argv)
    st=StopThreading()
    myWin = MyMainWindow(st)
    myWin.show()
    sys.exit(app.exec_())

# self.lineEdit_ip.setInputMask("000.000.000.000;_")
# self.lineEdit_ip.setInputMask("00.00.000.000;_")
# self.lineEdit_ip.setPlaceholderText("10.13.106.216")
# self.lineEdit_ip.setText("10.13.106.216")
# self.lineEdit_port.setText("8080")
# self.lineEdit_port.setPlaceholderText("8080")
# self.lineEdit_input_set.setText('0')
# self.lineEdit_threshold.setText('0')
# self.lineEdit_stapA.setText('0')
# self.lineEdit_stapB.setText('0')
# self.lineEdit_Frequency.setText('0')
# self.lineEdit_Amplitude.setText('0')
# self.lineEdit_spool_current_p.setText('0')
# self.lineEdit_spool_current_i.setText('0')
# self.lineEdit_spool_displacement_p.setText('0')
# self.lineEdit_spool_displacement_i.setText('0')
# self.lineEdit_spool_displacement_d.setText('0')
# self.lineEdit_piston_displacement_p.setText('0')
# self.lineEdit_piston_displacement_i.setText('0')
# self.lineEdit_piston_displacement_d.setText('0')
# MainWindow.setFixedSize(1120, 850)

