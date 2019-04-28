# -*- coding: utf-8 -*-

import sys
from PyQt5.QtGui import *
from Amplifer import *
from Dialog import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import*
from PyQt5.QtCore import *
import socket
import threading
import ctypes
import inspect
import webbrowser
import time
# class MyQwidget(QDialog,Ui_Dialog):
#     # signal_write_msg = QtCore.pyqtSignal(str)
#     def __init__(self, parent=None):
#         super(MyQwidget,self).__init__(parent)
#         self.setupUi(self)



class MyMainWindow(QMainWindow, Ui_MainWindow):
    signal_write_msg = QtCore.pyqtSignal(str)

    def __init__(self, st,parent=None):
        super(MyMainWindow, self).__init__(parent)
#        设置界面图标----------------2019.4.2
        self.setWindowIcon(QIcon('./imag/12.png'))
        
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
        #数据解析
        self.TX_BUFSIZE = 150
        self.RX_BUFSIZE = 5000

        self.bSerialTXBuff =['0']*50
        self.bASCIITemp = [0, 0]
        self.bNetworkPortType = 0
        self.wCommReadDataStartAddr = 0
        self.wCommReadDataCount = 0
        self.wDataRam=[0]*100
        self.wRunState1 = 0
        self.wRunState2 = 0
        self.wFaultState = 0
        self.wCommTXDataAddr = 0

        self.m_wStepSignalA = 0
        self.m_wStepSignalB = 0
        # 创建TCP/UDP套接字，AF_INET表示使用IPv4地址，SOCK_STREAM表示socket类型为流格式套接字
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect(self):
        """
        控件信号-槽的设置
        :param : QDialog类创建的对象
        :return: None
        """
        self.signal_write_msg.connect(self.write_msg)
        self.pushButton_ip_connect.clicked.connect(self.click_ip_link)
        self.pushButton_ip_disconnect.clicked.connect(self.click_ip_unlink)
        self.pushButton_clear.clicked.connect(self.click_clear)
        self.pushButton_send.clicked.connect(self.tcp_send)
        # self.pushButton_stap_read.clicked.connect(self.stap_read)
        # self.pushButton_stap_set.clicked.connect(self.stap_set)
        self.pushButton_update_program.clicked.connect(self.click_update_program)

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
        # self.link = False
        # self.pushButton_ip_disconnect.setEnabled(False)
        # self.pushButton_ip_connect.setEnabled(True)

    def click_update_program(self):
        # self.browser=QWebEngineView()
        # self.browser.openUrl(QUrl('http://www.baidu.com'))
        # # self.setCentralWidget(self.browser)


        # dig=MyQwidget()
        # dig.show()
        # dig.exec_()
        reply = QMessageBox.information(self, "更新程序", "确定更新程序", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        print(int(reply))
        if reply==16384:
            webbrowser.open('http://www.baidu.com')




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
                # print(recv_msg)
                msg = recv_msg.decode('utf-8')
                # print(msg)
                # print(list(msg))
                self.DateProcess(list(msg))
                print(self.wDataRam)
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
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            try:

                # send_msg = (str(self.textEdit_send.toPlainText())).encode('utf-8')
                # self.wDataRam[5]=send_msg
                # self.DataProduce(5,8,2)
                send_msg=self.bSerialTXBuff
                send_msg =''.join(send_msg)
                send_msg=(str(send_msg)).encode('utf-8')

                print(self.bSerialTXBuff)
                print(send_msg)
                self.tcp_socket.send(send_msg)
                self.msg = 'TCP客户端已发送\n'
                self.signal_write_msg.emit(self.msg)

            except Exception as ret:
                self.msg = '发送失败\n'
                self.signal_write_msg.emit("写入")

    def stap_read(self):

        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.DataProduce(5,12,5)
            #print(self.bSerialTXBuff)
            self.tcp_send()
            self.m_wStepSignalA = self.wDataRam[15]
            self.m_wStepSignalB = self.wDataRam[16]
            print(self.m_wStepSignalA,self.m_wStepSignalB)
            self.lineEdit_stapA.setText(str(self.m_wStepSignalA))
            self.lineEdit_stapB.setText(str(self.m_wStepSignalB))

    def stap_set(self):
        if self.link is False:
            self.msg = '请选择服务，并点击连接网络\n'
            self.signal_write_msg.emit("写入")
        else:
            self.m_wStepSignalA=str(self.lineEdit_stapA.text())
            self.m_wStepSignalB=str(self.lineEdit_stapB.text())
            self.wDataRam[15]=int(self.m_wStepSignalA)
            self.wDataRam[16]=int(self.m_wStepSignalB)
            print(self.wDataRam)
            self.DataProduce(6,12,5)
            print(self.bSerialTXBuff)
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
        print(self.wDataRam)
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

class StopThreading:
    """强制关闭线程的方法"""

    @staticmethod
    def _async_raise(tid, exc_type):
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exc_type):
            exc_type = type(exc_type)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)


#class Icon(QWidget):  
#    def __init__(self,  parent = None):  
#        super(Icon,self).__init__(parent)    
#        self.initUI()
#     
#    #2   
#    def initUI(self):
##        self.setGeometry(300,  300,  250,  150)  
##        self.setWindowTitle('演示程序图标例子')  
#        self.setWindowIcon(QIcon('./images/1223475.png'))  
#              
#






if __name__ == "__main__":

    app = QApplication(sys.argv)

    st=StopThreading()
    myWin = MyMainWindow(st)
    # myWin.wDataRam[15]=8000
    # myWin.wDataRam[16]=9000
    # myWin.DataProduce(6,12,5)
    # myWin.DataProduce(5, 12, 5)
    print(myWin.bSerialTXBuff)
    # myWin.DateProcess(myWin.bSerialTXBuff)
    # print(myWin.wDataRam)
    myWin.show()
    sys.exit(app.exec_())

# self.lineEdit_ip.setInputMask("000.000.000.000;_")
# self.lineEdit_ip.setInputMask("00.00.000.000;_")
# self.lineEdit_ip.setPlaceholderText("10.13.106.216")
# self.lineEdit_ip.setText("10.13.106.216")
# self.lineEdit_port.setText("8080")
# self.lineEdit_port.setPlaceholderText("8080")
