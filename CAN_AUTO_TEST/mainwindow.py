import binascii
import os
import time
from can import bus
from mailcap import show

import self as self
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog

from chery_file_format_check import Chery_file_format
from diag_read_interpreter import diag_read_interpreter_sf_len, diag_read_interpreter_sf_data, \
    diag_read_interpreter_sf_data_interpreter, diag_read_interpreter_ff_len, diag_read_interpreter_ff_data, \
    diag_read_interpreter_cf_data, diag_read_interpreter_cf_data_interpreter
from ui_mainwindow import Ui_MainWindow
import can
import logging
import types
import threading
from xml.dom.minidom import parse
import xml.dom.minidom
################
from diag_error_judgment_processing import error_judgment_processing
from evaluation_system import evaluation_system_result
from track_on_can import track_on

################

logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s - %(message)s')
# 文件保存到TXT中
# logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG,
#                    format=' %(asctime)s - %(levelname)s - %(message)s')

logging.debug('Start of program')


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.thread_can_frame = Thread_can_frame()  # 创建接收CANFRAME线程
        self.thread_send_kvaser_file = Thread_send_kvaser_file()  # 创建接收CANFRAME线程
        self.thread_device_online = Thread_device_online()  # 创建设备在线线程
        self.setupUi(self)
        self.pushButton_bus_on.clicked.connect(self.on_pushButton_bus_on)
        self.pushButton_bus_off.clicked.connect(self.on_pushButton_bus_off)
        self.pushButton_bus_off.setEnabled(False)
        self.pushButton_diva.clicked.connect(self.on_pushButton_diva)
        self.pushButton_diva_test.clicked.connect(self.on_pushButton_diva_test)
        self.radioButton_device_online.setChecked(False)
        self.radioButton_device_online.clicked.connect(self.on_radioButton_device_online)
        self.thread_can_frame.signal_send_str_to_ui.connect(self.set_text_to_diag_ui)
        self.thread_can_frame.signal_send_str_to_lcd_total.connect(self.set_lcd_total_display)
        self.thread_can_frame.signal_send_str_to_lcd_pass.connect(self.set_lcd_pass_display)
        self.thread_can_frame.signal_send_str_to_lcd_error.connect(self.set_lcd_error_display)
        self.pushButton_diva_select.clicked.connect(self.on_pushButton_diva_select)
        self.pushButton_car_scene.clicked.connect(self.on_pushButton_car_scene)
        self.pushButton_read_file.clicked.connect(self.on_pushButton_read_file)
        self.pushButton_load_kvaser_file.clicked.connect(self.on_pushButton_load_kvaser_file)
        self.lineEdit_filter_app_node.setInputMask("000")
        self.lineEdit_filter_nm_node.setInputMask("000")
        self.lineEdit_filter_nm_node.setText('630')
        self.lineEdit_filter_app_node.setText('449')
        self.thread_send_kvaser_file.signal_send_kvaser_file_ui.connect(self.set_text_to_kvaser_file_ui)
        self.label_show_car.setPixmap(QPixmap("car.jpg"))
        self.label_show_car.setScaledContents(True)
        self.pushButton_car_action.clicked.connect(self.on_pushButton_car_action)
        self.radioButton_left_led_off.setChecked(1)
        self.radioButton_left_dow_off.setChecked(1)
        self.radioButton_right_led_off.setChecked(1)
        self.radioButton_right_dow_off.setChecked(1)
        self.radioButton_chery_t1d.setChecked(1)
        self.radioButton_left_led_off.toggled.connect(self.left_led_state)
        self.radioButton_left_dow_off.toggled.connect(self.left_dow_state)
        self.radioButton_right_led_off.toggled.connect(self.right_led_state)
        self.radioButton_right_dow_off.toggled.connect(self.right_dow_state)
        self.textEdit_car_led_state.setText('请检查车身灯状态')
        self.pushButton_self_test.clicked.connect(self.on_pushButton_self_test)
        self.pushButton_send_ihu_sw.clicked.connect(self.set_ihu_sw)
        self.pushButton_send_ctcs_ihu_sw.clicked.connect(self.set_ctcs_ihu_sw)
        self.radioButton_bsd_on.setChecked(1)
        self.radioButton_rcw_on.setChecked(1)
        self.radioButton_dow_on.setChecked(1)
        self.radioButton_ctcs_bsd_on.setChecked(1)
        self.radioButton_ctcs_dow_on.setChecked(1)
        self.radioButton_ctcs_cvw_on.setChecked(1)
        self.radioButton_ctcs_rcw_on.setChecked(1)
        self.pushButton_select_version_file.clicked.connect(self.on_show_version_file_path)
        self.pushButton_read_write_version.clicked.connect(self.send_read_write_version)
        self.thread_general_send_frame = Thread_general_send_frame()  # 创建接收CANFRAME线程
        self.pushButton_read_version.clicked.connect(self.on_pushButton_read_version)
        self.thread_general_send_frame.signal_send_str_to_ui.connect(self.set_text_to_diag_ui)
        self.radioButton_chery_t1d_2.setChecked(1)
        self.radioButton_chery_t1d_2.clicked.connect(self.set_enable_diff_sw)
        self.radioButton_chery_ctcs_2.clicked.connect(self.set_enable_diff_sw)
        self.groupBox_ctcs_sw.setEnabled(False)
        self.pushButton_signal.clicked.connect(self.on_pushButton_signal)
        self.radioButton_chery_t1d.clicked.connect(self.set_enable_led_dow_sw)
        self.radioButton_chery_ctcs.clicked.connect(self.set_enable_led_dow_sw)
        self.radioButton_high_match.setChecked(1)
        self.radioButton_high_match.clicked.connect(self.set_enable_led_dow_sw)
        self.radioButton_low_match.clicked.connect(self.set_enable_led_dow_sw)
        self.pushButton_diag_configer_file.clicked.connect(self.select_diag_configer_file)
        self.pushButton_release_file_format_check.clicked.connect(self.on_pushButton_release_file_format_check)
        self.pushButton_flash_driver_select.clicked.connect(self.on_pushButton_flash_driver_select)
        self.pushButton_cali_select.clicked.connect(self.on_pushButton_cali_select)
        self.pushButton_app_select.clicked.connect(self.on_pushButton_app_select)
        self.chery_file_format = Chery_file_format()
        self.chery_file_format.signal_send_str_to_ui.connect(self.on_textEdit_file_format_show)
        self.pushButton_diagnosis.clicked.connect(self.on_pushButton_diagnosis)
        self.pushButton_car_dtc.clicked.connect(self.on_pushButton_car_dtc)
        self.pushButton_dtc_info.clicked.connect(self.on_pushButton_dtc_info)
        self.radioButton_dtc_chery.setChecked(1)
        self.thread_dtc_info = Thread_dtc_info()
        self.thread_dtc_info.signal_send_str_to_ui.connect(self.set_text_to_diag_ui)

    def on_pushButton_dtc_info(self):
        if self.radioButton_dtc_chery.isChecked():
            self.textBrowser_dtc_info.setText('乘用车系列诊断故障信息：')
            self.thread_dtc_info.start()
        else:
            self.textBrowser_dtc_info.setText('CTCS诊断故障信息：')
            self.thread_dtc_info.start()

    def on_pushButton_car_dtc(self):
        self.stackedWidget.setCurrentIndex(7)

    def on_pushButton_diagnosis(self):
        self.stackedWidget.setCurrentIndex(2)

    def on_textEdit_file_format_show(self, str):
        self.textEdit_file_format_show.append(str)
        self.textEdit_file_format_show.moveCursor(QtGui.QTextCursor.End)

    def on_pushButton_flash_driver_select(self):
        flash_driver_file_path, _ = QFileDialog.getOpenFileName(self,
                                                                "选取文件",
                                                                "E:",
                                                                "Files (*s19)")  # 设置文件扩展名过滤,注意用双分号
        self.textEdit_file_format_show.clear()
        if len(flash_driver_file_path) == 0:
            self.lineEdit_flash_driver_address.setText('flash driver file 未选取')
        else:
            self.lineEdit_flash_driver_address.setText(flash_driver_file_path)
            self.chery_file_format.check_flash_driver_file_check(flash_driver_file_path)

    def on_pushButton_cali_select(self):
        cali_file_path, _ = QFileDialog.getOpenFileName(self,
                                                        "选取文件",
                                                        "E:",
                                                        "Files (*s19)")  # 设置文件扩展名过滤,注意用双分号
        self.textEdit_file_format_show.clear()
        if len(cali_file_path) == 0:
            self.lineEdit_cali_address.setText('cali file 未选取')
        else:
            self.lineEdit_cali_address.setText(cali_file_path)
            self.chery_file_format.check_cali_file_check(cali_file_path)

    def on_pushButton_app_select(self):
        app_file_path, _ = QFileDialog.getOpenFileName(self,
                                                       "选取文件",
                                                       "E:",
                                                       "Files (*s19)")  # 设置文件扩展名过滤,注意用双分号
        self.textEdit_file_format_show.clear()
        if len(app_file_path) == 0:
            self.lineEdit_app_address.setText('app file 未选取')
        else:
            self.lineEdit_app_address.setText(app_file_path)
            self.chery_file_format.check_app_file_check(app_file_path)

    def on_pushButton_release_file_format_check(self):
        self.stackedWidget.setCurrentIndex(8)

    def select_diag_configer_file(self):
        diag_configer_file_path, _ = QFileDialog.getOpenFileName(self,
                                                                 "选取文件",
                                                                 "E:\\python_tool\\CAN_AUTO_TEST\\TEST_FILE\\诊断配置",
                                                                 "Files (*xml)")  # 设置文件扩展名过滤,注意用双分号
        self.label_diag_title.setText(diag_configer_file_path)

    def set_enable_led_dow_sw(self):
        if self.radioButton_chery_t1d.isChecked() is True and self.radioButton_high_match.isChecked() is True:
            self.groupBox_left_led_sw.setEnabled(True)
            self.groupBox_left_dow_sw.setEnabled(True)
            self.groupBox_right_led_sw.setEnabled(True)
            self.groupBox_right_dow_sw.setEnabled(True)
        else:
            self.groupBox_left_led_sw.setEnabled(True)
            self.groupBox_left_dow_sw.setEnabled(False)
            self.groupBox_right_led_sw.setEnabled(True)
            self.groupBox_right_dow_sw.setEnabled(False)

    def on_pushButton_signal(self):
        self.stackedWidget.setCurrentIndex(4)

    def set_enable_diff_sw(self):
        if self.radioButton_chery_t1d_2.isChecked() is True:
            self.groupBox_ctcs_sw.setEnabled(False)
            self.groupBox_chery_sw.setEnabled(True)
        else:
            self.groupBox_chery_sw.setEnabled(False)
            self.groupBox_ctcs_sw.setEnabled(True)

    def on_pushButton_read_version(self):
        self.stackedWidget.setCurrentIndex(6)

    def send_read_write_version(self):
        self.textEdit_show_result.clear()
        self.textEdit_show_result.setPlainText('读取写软件版本信息')
        self.thread_general_send_frame.start()  # 开始线程

    def on_show_version_file_path(self):
        global version_file_path
        version_file_path, _ = QFileDialog.getOpenFileName(self,
                                                           "选取文件",
                                                           "E:\\python_tool\\CAN_AUTO_TEST\\TEST_FILE",
                                                           "Files (*xml)")  # 设置文件扩展名过滤,注意用双分号
        self.lineEdit_show_version_file.setText(version_file_path)

    def set_ihu_sw(self):
        self.textBrowser_ihu_sw_message.setText('奇瑞乘用车系列大屏设置BSD系统开关项为：(需知道车型的功能配置)')
        if self.radioButton_bsd_on.isChecked() is True:
            bsd_sw = 1
            self.textBrowser_ihu_sw_message.append('BSD_SW : ON')
        else:
            bsd_sw = 2
            self.textBrowser_ihu_sw_message.append('BSD_SW : OFF')
        if self.radioButton_rcw_on.isChecked() is True:
            rcw_sw = 1
            self.textBrowser_ihu_sw_message.append('RCW_SW : ON')
        else:
            rcw_sw = 2
            self.textBrowser_ihu_sw_message.append('RCW_SW : OFF')
        if self.radioButton_dow_on.isChecked() is True:
            dow_sw = 1
            self.textBrowser_ihu_sw_message.append('DOW_SW : ON')
        else:
            dow_sw = 2
            self.textBrowser_ihu_sw_message.append('DOW_SW : OFF')

        ihu_sw = (dow_sw << 6) + (rcw_sw << 4) + (bsd_sw << 2)
        for i in range(3):
            msg = can.Message(arbitration_id=0x4FC,
                              data=[0x00, ihu_sw, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.1)

    def set_ctcs_ihu_sw(self):
        self.textBrowser_ihu_sw_message.setText('CTCS-大屏设置BSD系统开关项为：(需知道车型的功能配置)')
        if self.radioButton_ctcs_bsd_on.isChecked() is True:
            bsd_sw = 1
            self.textBrowser_ihu_sw_message.append('BSD_SW : ON')
        else:
            bsd_sw = 0
            self.textBrowser_ihu_sw_message.append('BSD_SW : OFF')
        if self.radioButton_ctcs_cvw_on.isChecked() is True:
            cvw_sw = 1
            self.textBrowser_ihu_sw_message.append('CVW_SW : ON')
        else:
            cvw_sw = 0
            self.textBrowser_ihu_sw_message.append('CVW_SW : OFF')
        if self.radioButton_ctcs_dow_on.isChecked() is True:
            dow_sw = 1
            self.textBrowser_ihu_sw_message.append('DOW_SW : ON')
        else:
            dow_sw = 0
            self.textBrowser_ihu_sw_message.append('DOW_SW : OFF')
        if self.radioButton_ctcs_rcw_on.isChecked() is True:
            rcw_sw = 1
            self.textBrowser_ihu_sw_message.append('RCW_SW : ON')
        else:
            rcw_sw = 0
            self.textBrowser_ihu_sw_message.append('RCW_SW : OFF')

        ihu_sw_1 = (bsd_sw << 4) + (cvw_sw << 6)
        ihu_sw_2 = dow_sw + (rcw_sw << 2)
        for i in range(3):
            msg = can.Message(arbitration_id=0x308,
                              data=[0x00, 0x00, 0x00, ihu_sw_1, ihu_sw_2, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.1)

    def on_pushButton_self_test(self):
        if self.radioButton_chery_t1d.isChecked() is True:
            self.textEdit_car_led_state.setText('依次发送M1DFL2-key-sts-状态信号')
            self.textEdit_car_led_state.append('发送M1DFL2-key-sts-OFF')
            msg = can.Message(arbitration_id=0x391,
                              data=[0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('发送M1DFL2-key-sts-ACC')
            msg = can.Message(arbitration_id=0x391,
                              data=[0xA0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('发送M1DFL2-key-sts-ON')
            msg = can.Message(arbitration_id=0x391,
                              data=[0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('发送M1DFL2-key-sts-START')
            msg = can.Message(arbitration_id=0x391,
                              data=[0xE0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('自检完成')

        else:
            self.textEdit_car_led_state.setText('依次发送M32TFL-key-sts-状态信号')
            self.textEdit_car_led_state.append('发送M32TFL-key-sts-OFF')
            msg = can.Message(arbitration_id=0x155,
                              data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('发送M32TFL-key-sts-ACC')
            msg = can.Message(arbitration_id=0x155,
                              data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('发送M32TFL-key-sts-ON')
            msg = can.Message(arbitration_id=0x155,
                              data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('发送M32TFL-key-sts-START')
            msg = can.Message(arbitration_id=0x155,
                              data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            time.sleep(0.5)
            self.textEdit_car_led_state.append('自检完成')

    def left_led_state(self):
        if self.radioButton_left_led_off.isChecked() is False and self.radioButton_left_led_on.isChecked() is True:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查左LED灯是否点亮')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x42, 0x03, 0x04, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)

            else:
                self.textEdit_car_led_state.setText('请检查左LED灯是否点亮')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0xFD, 0x02, 0x03, 0x01, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
        else:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查左LED灯是否熄灭')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x42, 0x03, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
            else:
                self.textEdit_car_led_state.setText('请检查左LED灯是否熄灭')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0xFD, 0x02, 0x03, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)

    def left_dow_state(self):
        if self.radioButton_left_dow_off.isChecked() is False and self.radioButton_left_dow_on.isChecked() is True:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查左DOW灯是否点亮')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x53, 0x03, 0x01, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
            else:
                self.textEdit_car_led_state.setText('CTCS暂不支持DOW灯自驱动')
                # self.textEdit_car_led_state.setText('请检查左DOW灯是否点亮')

        else:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查左DOW灯是否熄灭')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x53, 0x03, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
            else:
                self.textEdit_car_led_state.setText('CTCS暂不支持DOW灯自驱动')
                # self.textEdit_car_led_state.setText('请检查左DOW灯是否熄灭')

    def right_led_state(self):
        if self.radioButton_right_led_off.isChecked() is False and self.radioButton_right_led_on.isChecked() is True:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查右LED灯是否点亮')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x42, 0x03, 0x02, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
            else:
                self.textEdit_car_led_state.setText('请检查右LED灯是否点亮')
                msg = can.Message(arbitration_id=0x66F,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x66F,
                                  data=[0x05, 0x2F, 0xFD, 0x02, 0x03, 0x01, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)

        else:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查右LED灯是否熄灭')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x42, 0x03, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)

            else:
                self.textEdit_car_led_state.setText('请检查右LED灯是否熄灭')
                msg = can.Message(arbitration_id=0x66F,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x66F,
                                  data=[0x05, 0x2F, 0xFD, 0x02, 0x03, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)

    def right_dow_state(self):
        if self.radioButton_right_dow_off.isChecked() is False and self.radioButton_right_dow_on.isChecked() is True:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查右DOW灯是否点亮')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x52, 0x03, 0x01, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
            else:
                # self.textEdit_car_led_state.setText('请检查右DOW灯是否点亮')
                self.textEdit_car_led_state.setText('CTCS暂不支持DOW灯自驱动')

        else:
            if self.radioButton_chery_t1d.isChecked() is True:
                self.textEdit_car_led_state.setText('请检查右DOW灯是否熄灭')
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
                msg = can.Message(arbitration_id=0x767,
                                  data=[0x05, 0x2F, 0x76, 0x52, 0x03, 0x00, 0x00, 0x00],
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(0.2)
            else:
                # self.textEdit_car_led_state.setText('请检查右DOW灯是否熄灭')
                self.textEdit_car_led_state.setText('CTCS暂不支持DOW灯自驱动')

    def on_pushButton_car_action(self):
        self.stackedWidget.setCurrentIndex(5)

    def set_text_to_kvaser_file_ui(self, str):
        self.textEdit_car_scene.setText(str)

    def on_pushButton_load_kvaser_file(self):
        self.textEdit_car_scene.setText('加载文件')
        global kvaser_file
        kvaser_file, _ = QFileDialog.getOpenFileName(self,
                                                     "选取文件",
                                                     os.getcwd(),
                                                     "Files (*txt)")  # 设置文件扩展名过滤,注意用双分号
        self.lineEdit_load_kvaser_file.setText(kvaser_file)

    def on_pushButton_read_file(self):
        global app_node
        global nm_node
        app_node = self.lineEdit_filter_app_node.text()
        nm_node = self.lineEdit_filter_nm_node.text()
        app_node = int(app_node, 16)
        nm_node = int(nm_node, 16)
        self.thread_send_kvaser_file.start()

    def on_pushButton_car_scene(self):
        self.stackedWidget.setCurrentIndex(1)

    def on_pushButton_diva_select(self):
        global diva_test_case_file
        diva_test_case_file, _ = QFileDialog.getOpenFileName(self,
                                                             "选取文件",
                                                             os.getcwd(),
                                                             "Files (*xml)")  # 设置文件扩展名过滤,注意用双分号

        self.lineEdit_show_diva_test_file.setText(diva_test_case_file)

    def on_radioButton_device_online(self):
        if self.radioButton_device_online.isChecked():
            msg = can.Message(arbitration_id=0x7CF,
                              data=[0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00],
                              is_extended_id=False)
            bus.send(msg)
            print('start')
            # self.thread_device_online.start()
        else:
            print('pause')
            # self.thread_device_online.pause()

    def set_text_to_diag_ui(self, str):
        self.textEdit_show_result.append(str)
        self.textEdit_show_result.moveCursor(QtGui.QTextCursor.End)

    def set_lcd_total_display(self, str):
        self.lcdNumber_total.display(str)

    def set_lcd_pass_display(self, str):
        self.lcdNumber_pass.display(str)

    def set_lcd_error_display(self, str):
        self.lcdNumber_error.display(str)

    def on_pushButton_bus_on(self):
        # 1.bus 作为全局使用
        global bus
        bus = can.interface.Bus(bustype='kvaser', channel=0, bitrate=500000)
        """
        设置接收过滤
        """
        # 2.设置接收过滤
        # can_filters = [{"can_id": 0x677, "can_mask": 0x677, "extended": False}]
        # bus.set_filters(can_filters)
        try:
            self.textEdit_show_result.setPlainText('TEST START UP')
            self.pushButton_bus_off.setEnabled(True)
            self.pushButton_bus_on.setEnabled(False)
            self.textBrowser_bus_status.setText('**********BUS ON**********')
            self.textBrowser_bus_status.append('Channel:' + '   ' + bus.channel_info)
            self.textBrowser_bus_status.append('Settings:  500000bit/s')
            self.textBrowser_bus_status.append('***************************')
            message = can.Message(arbitration_id=0x7DF, is_extended_id=True,
                                  data=[0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00])

            bus.send(message, timeout=0.2)

        except can.CanError:
            print("Message NOT sent")

    def on_pushButton_bus_off(self):
        self.textEdit_show_result.setPlainText('TEST OFF')
        self.textBrowser_bus_status.setText('**********BUS OFF**********')
        self.pushButton_bus_off.setEnabled(False)
        self.pushButton_bus_on.setEnabled(True)
        bus.shutdown()

    # todo:增加其他功能对应的页面
    def on_pushButton_diva(self):
        self.stackedWidget.setCurrentIndex(0)

    def on_pushButton_diva_test(self):
        self.textEdit_show_result.clear()
        self.textEdit_show_result.setPlainText('TEST START UP')
        self.thread_can_frame.start()  # 开始线程


class Thread_device_online(QThread):

    def __init__(self):
        super().__init__()
        self.iterations = 0
        self.daemon = True  # Allow main to exit even if still running.
        self.paused = True  # Start out paused.
        self.state = threading.Condition()

    def run(self):
        while True:
            with self.state:  # 在该条件下操作
                while self._pause:
                    t = threading.Timer(3, self.online)
                    t.start()
                if self.paused:
                    self.state.wait()  # Block execution until notified.

    def resume(self):  # 用来恢复/启动run
        with self.state:  # 在该条件下操作
            self.paused = False
            self.state.notify()  # Unblock self if waiting.

    def pause(self):  # 用来暂停run
        with self.state:  # 在该条件下操作
            self.paused = True  # Block self

    def online(self):
        msg = can.Message(arbitration_id=0x7CF,
                          data=[0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00],
                          is_extended_id=False)
        bus.send(msg)
        t = threading.Timer(3, self.online)
        t.start()
        print(msg)


class Thread_send_kvaser_file(QThread):
    signal_send_kvaser_file_ui = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        self.signal_send_kvaser_file_ui.emit('正在发送，请等待.......')
        track_on(kvaser_file, app_node, nm_node)
        self.signal_send_kvaser_file_ui.emit('关闭文件')


# CAN FRAME 接收线程
class Thread_can_frame(QThread):
    # 创建一个信号从信号发送到UI主线程
    signal_send_str_to_ui = pyqtSignal(str)
    signal_send_str_to_lcd_total = pyqtSignal(str)
    signal_send_str_to_lcd_pass = pyqtSignal(str)
    signal_send_str_to_lcd_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def show(self, str):
        self.signal_send_str_to_ui.emit(str)

    def run_security_access_locked(self):
        self.signal_send_str_to_ui.emit('Title: security_access_locked')

    def run_security_access_unlocked_L1(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_security_access_unlocked_L1 = xml.dom.minidom.parse("common_service_security_access_unlocked_L1.xml")
        test_security_access_unlocked_L1 = DOMTree_security_access_unlocked_L1.documentElement
        if test_security_access_unlocked_L1.hasAttribute("shelf"):
            print("Root element : %s" % test_security_access_unlocked_L1.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_security_access_unlocked_L1 = test_security_access_unlocked_L1.getElementsByTagName("case")

        for case_security_access_unlocked_L1 in case_list_security_access_unlocked_L1:
            print("*****case-list*****")
            if case_security_access_unlocked_L1.hasAttribute("title"):
                print("Title: %s" % case_security_access_unlocked_L1.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_security_access_unlocked_L1.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_security_access_unlocked_L1.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_security_access_unlocked_L1.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_security_access_unlocked_L1.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_security_access_unlocked_L1.getElementsByTagName('delay_time'):
                delay_time = case_security_access_unlocked_L1.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_security_access_unlocked_L1.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_security_access_unlocked_L1.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_security_access_unlocked_L2(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_security_access_unlocked_L2 = xml.dom.minidom.parse("common_service_security_access_unlocked_L2.xml")
        test_security_access_unlocked_L2 = DOMTree_security_access_unlocked_L2.documentElement
        if test_security_access_unlocked_L2.hasAttribute("shelf"):
            print("Root element : %s" % test_security_access_unlocked_L2.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_security_access_unlocked_L2 = test_security_access_unlocked_L2.getElementsByTagName("case")

        for case_security_access_unlocked_L2 in case_list_security_access_unlocked_L2:
            print("*****case-list*****")
            if case_security_access_unlocked_L2.hasAttribute("title"):
                print("Title: %s" % case_security_access_unlocked_L2.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_security_access_unlocked_L2.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_security_access_unlocked_L2.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_security_access_unlocked_L2.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_security_access_unlocked_L2.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_security_access_unlocked_L2.getElementsByTagName('delay_time'):
                delay_time = case_security_access_unlocked_L2.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_security_access_unlocked_L2.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_security_access_unlocked_L2.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_security_access_unlocked_L3(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_security_access_unlocked_L3 = xml.dom.minidom.parse("common_service_security_access_unlocked_L3.xml")
        test_security_access_unlocked_L3 = DOMTree_security_access_unlocked_L3.documentElement
        if test_security_access_unlocked_L3.hasAttribute("shelf"):
            print("Root element : %s" % test_security_access_unlocked_L3.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_security_access_unlocked_L3 = test_security_access_unlocked_L3.getElementsByTagName("case")

        for case_security_access_unlocked_L3 in case_list_security_access_unlocked_L3:
            print("*****case-list*****")
            if case_security_access_unlocked_L3.hasAttribute("title"):
                print("Title: %s" % case_security_access_unlocked_L3.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_security_access_unlocked_L3.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_security_access_unlocked_L3.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_security_access_unlocked_L3.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_security_access_unlocked_L3.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_security_access_unlocked_L3.getElementsByTagName('delay_time'):
                delay_time = case_security_access_unlocked_L3.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_security_access_unlocked_L3.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_security_access_unlocked_L3.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_security_access_unlocked_L4(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_security_access_unlocked_L4 = xml.dom.minidom.parse("common_service_security_access_unlocked_L4.xml")
        test_security_access_unlocked_L4 = DOMTree_security_access_unlocked_L4.documentElement
        if test_security_access_unlocked_L4.hasAttribute("shelf"):
            print("Root element : %s" % test_security_access_unlocked_L4.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_security_access_unlocked_L4 = test_security_access_unlocked_L4.getElementsByTagName("case")

        for case_security_access_unlocked_L4 in case_list_security_access_unlocked_L4:
            print("*****case-list*****")
            if case_security_access_unlocked_L4.hasAttribute("title"):
                print("Title: %s" % case_security_access_unlocked_L4.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_security_access_unlocked_L4.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_security_access_unlocked_L4.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_security_access_unlocked_L4.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_security_access_unlocked_L4.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_security_access_unlocked_L4.getElementsByTagName('delay_time'):
                delay_time = case_security_access_unlocked_L4.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_security_access_unlocked_L4.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_security_access_unlocked_L4.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_ECUReset(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_ECUReset = xml.dom.minidom.parse("common_service_ecu_reset.xml")
        test_ECUReset = DOMTree_ECUReset.documentElement
        if test_ECUReset.hasAttribute("shelf"):
            print("Root element : %s" % test_ECUReset.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_ECUReset = test_ECUReset.getElementsByTagName("case")

        for case_ECUReset in case_list_ECUReset:
            print("*****case-list*****")
            if case_ECUReset.hasAttribute("title"):
                print("Title: %s" % case_ECUReset.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_ECUReset.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_ECUReset.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_ECUReset.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_ECUReset.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_ECUReset.getElementsByTagName('delay_time'):
                delay_time = case_ECUReset.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_ECUReset.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_ECUReset.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_default_session(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_default_session = xml.dom.minidom.parse("common_service_default_session.xml")
        test_default_session = DOMTree_default_session.documentElement
        if test_default_session.hasAttribute("shelf"):
            print("Root element : %s" % test_default_session.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_default_session = test_default_session.getElementsByTagName("case")

        for case_default_session in case_list_default_session:
            print("*****case-list*****")
            if case_default_session.hasAttribute("title"):
                print("Title: %s" % case_default_session.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_default_session.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_default_session.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_default_session.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_default_session.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_default_session.getElementsByTagName('delay_time'):
                delay_time = case_default_session.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_default_session.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_default_session.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_programming_session(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_programming_session = xml.dom.minidom.parse("common_service_programming_session.xml")
        test_programming_session = DOMTree_programming_session.documentElement
        if test_programming_session.hasAttribute("shelf"):
            print("Root element : %s" % test_programming_session.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_programming_session = test_programming_session.getElementsByTagName("case")

        for case_programming_session in case_list_programming_session:
            print("*****case-list*****")
            if case_programming_session.hasAttribute("title"):
                print("Title: %s" % case_programming_session.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_programming_session.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_programming_session.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_programming_session.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_programming_session.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_programming_session.getElementsByTagName('delay_time'):
                delay_time = case_programming_session.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_programming_session.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_programming_session.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_extended_session(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_extended_session = xml.dom.minidom.parse("common_service_extended_session.xml")
        test_extended_session = DOMTree_extended_session.documentElement
        if test_extended_session.hasAttribute("shelf"):
            print("Root element : %s" % test_extended_session.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_extended_session = test_extended_session.getElementsByTagName("case")

        for case_extended_session in case_list_extended_session:
            print("*****case-list*****")
            if case_extended_session.hasAttribute("title"):
                print("Title: %s" % case_extended_session.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_extended_session.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_extended_session.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_extended_session.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_extended_session.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_extended_session.getElementsByTagName('delay_time'):
                delay_time = case_extended_session.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_extended_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_extended_session.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_extended_session.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run_codings_session(self):
        # 使用minidom解析器打开 XML 文档
        DOMTree_codings_session = xml.dom.minidom.parse("common_service_codings_session.xml")
        test_codings_session = DOMTree_codings_session.documentElement
        if test_codings_session.hasAttribute("shelf"):
            print("Root element : %s" % test_codings_session.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_codings_session = test_codings_session.getElementsByTagName("case")

        for case_codings_session in case_list_codings_session:
            print("*****case-list*****")
            if case_codings_session.hasAttribute("title"):
                print("Title: %s" % case_codings_session.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_codings_session.getAttribute("title"))
            # 从xml 获取要发送的数据
            tx_id = case_codings_session.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case_codings_session.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case_codings_session.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case_codings_session.getElementsByTagName('delay_time'):
                delay_time = case_codings_session.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                msg = can.Message(arbitration_id=0x767,
                                  data=tx_frame_data,
                                  is_extended_id=False)
                # 调用驱动
                bus.send(msg)
                # 界面显示 CAN tx frame
                tx_frame_id = str(hex(msg.arbitration_id))
                tx_frame_len = str(msg.dlc)
                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                tx_frame_time = str(round(time.perf_counter(), 3))
                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                print(tx_frame)
                # 发送信号到界面
                self.signal_send_str_to_ui.emit(tx_frame)
                # 获取 time out
                wait_time = wait_time.childNodes[0].data
                wait_time = int(wait_time) / 1000
                print(wait_time)
                # 设置等待回复的时间
                time_left = wait_time + time.time() + delay_time
                time_start = 0
                try:
                    # 在time out 下一直接收数据
                    while (time_left - time_start) > 0:
                        time_start = time.time()
                        msg = bus.recv(0)
                        if msg is not None and msg.arbitration_id != 0:
                            # 收到特定ID的数据
                            rx_frame_id = str(hex(msg.arbitration_id))
                            rx_frame_len = str(msg.dlc)
                            rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                            rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                rx_frame_data[14:16])
                            rx_frame_time = str(round(time.perf_counter(), 3))
                            rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                            print(rx_frame)
                            self.signal_send_str_to_ui.emit(rx_frame)

                            # 接收错误判断处理
                            if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                error_handler = error_judgment_processing(rx_frame_data[9:11])
                                self.signal_send_str_to_ui.emit(error_handler)
                            if rx_frame_data[0:2] == '10':
                                msg = can.Message(arbitration_id=0x767,
                                                  data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                  is_codings_id=False)
                                # CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                    tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                    tx_frame_data[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                bus.send(msg)
                                print(tx_frame)
                                self.signal_send_str_to_ui.emit(tx_frame)

                            # 与文件接收标准数据对比
                            print(rx_frame_data)
                            rx_id = case_codings_session.getElementsByTagName('rx_id')[0]
                            print("rx_id: %s" % rx_id.childNodes[0].data)
                            rx_data = case_codings_session.getElementsByTagName('rx_data')[0]
                            print("rx: %s" % rx_data.childNodes[0].data)
                            rx_data = rx_data.childNodes[0].data
                            print(rx_data)
                            if evaluation_system_result(rx_data, rx_frame_data):
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :pass'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)
                            else:
                                expect_the_result = 'expected :' + rx_data
                                actual_the_result = 'actual   :' + rx_frame_data
                                dividing_line = '***************************************************'
                                result = 'result   :error'
                                # todo 显示到ui
                                self.signal_send_str_to_ui.emit(dividing_line)
                                self.signal_send_str_to_ui.emit(expect_the_result)
                                self.signal_send_str_to_ui.emit(actual_the_result)
                                self.signal_send_str_to_ui.emit(result)
                                self.signal_send_str_to_ui.emit(dividing_line)

                except KeyboardInterrupt:
                    pass
            except can.CanError:
                print("Message NOT sent")

    def run(self):
        # 使用minidom解析器打开 XML 文档
        # DOMTree = xml.dom.minidom.parse(diva_test_case_file)
        DOMTree = xml.dom.minidom.parse('case1-5.xml')
        test = DOMTree.documentElement
        if test.hasAttribute("shelf"):
            print("Root element : %s" % test.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list = test.getElementsByTagName("case")
        total_count = 0
        pass_count = 0
        error_count = 0
        for case in case_list:
            print("*****case-list*****")
            if case.hasAttribute("title"):
                print("Title: %s" % case.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case.getAttribute("title"))
                # todo 显示到LCD
                total_count = total_count + 1
                self.signal_send_str_to_lcd_total.emit(str(total_count))
            ##########################################################################################################
            # 1.先从xml 得到需要复位 & 当前会话状态 & 安全等级
            # 1.1 需要复位
            if case.getElementsByTagName('automatic_ecu_reset'):
                automatic_ecu_reset = case.getElementsByTagName('automatic_ecu_reset')[0]
                print("automatic_State_Change: %s" % automatic_ecu_reset.childNodes[0].data)
                # 获取  automatic_ecu_reset
                automatic_ecu_reset = automatic_ecu_reset.childNodes[0].data
                # 2.1 从xml 得到当前会话状态；判断
                if str(automatic_ecu_reset) == 'ECUReset':
                    self.run_ECUReset()
            # 1.2 会话状态
            if case.getElementsByTagName('automatic_State_Change'):
                automatic_State_Change = case.getElementsByTagName('automatic_State_Change')[0]
                print("automatic_State_Change: %s" % automatic_State_Change.childNodes[0].data)
                # 获取  automatic_State
                automatic_State_Change = automatic_State_Change.childNodes[0].data
                # 2.1 从xml 得到当前会话状态；判断
                if str(automatic_State_Change) != 'FALSE':
                    if str(automatic_State_Change) == 'DefaultSession':
                        print('DefaultSession')
                        self.run_default_session()
                    elif str(automatic_State_Change) == 'ProgrammingSession':
                        self.run_programming_session()
                        print('ProgrammingSession')
                    elif str(automatic_State_Change) == 'ExtendedDiagnosticSession':
                        self.run_extended_session()
                        print('ExtendedDiagnosticSession')
                    elif str(automatic_State_Change) == 'CodingDiagnosticSession':
                        self.run_codings_session()
                        print('CodingDiagnosticSession')
                else:
                    print('FALSE')
            # 1.3 安全等级
            if case.getElementsByTagName('automatic_SecurityAccess_Change'):
                automatic_SecurityAccess_Change = case.getElementsByTagName('automatic_SecurityAccess_Change')[0]
                print("automatic_SecurityAccess_Change: %s" % automatic_SecurityAccess_Change.childNodes[0].data)
                # 获取  automatic_State
                automatic_SecurityAccess_Change = automatic_SecurityAccess_Change.childNodes[0].data
                if str(automatic_SecurityAccess_Change) != 'Locked':
                    if str(automatic_SecurityAccess_Change) == 'SecurityAccess_unlocked_L1':
                        self.run_security_access_unlocked_L1()
                    elif str(automatic_SecurityAccess_Change) == 'SecurityAccess_unlocked_L2':
                        self.run_security_access_unlocked_L2()
                    elif str(automatic_SecurityAccess_Change) == 'SecurityAccess_unlocked_L3':
                        self.run_security_access_unlocked_L3()
                    elif str(automatic_SecurityAccess_Change) == 'SecurityAccess_unlocked_L4':
                        self.run_security_access_unlocked_L4()
            ###########################################################################################################
            # 从xml 获取要发送的数据
            tx_id = case.getElementsByTagName('tx_id')[0]
            print("tx_id: %s" % tx_id.childNodes[0].data)
            tx_data = case.getElementsByTagName('tx_data')[0]
            print("tx_data: %s" % tx_data.childNodes[0].data)
            wait_time = case.getElementsByTagName('wait_time')[0]
            print("wait_time: %s" % wait_time.childNodes[0].data)

            # todo delay time
            if case.getElementsByTagName('delay_time'):
                delay_time = case.getElementsByTagName('delay_time')[0]
                print("delay_time: %s" % delay_time.childNodes[0].data)
                # 获取 delay time
                delay_time = delay_time.childNodes[0].data
                delay_time = int(delay_time) / 1000
            else:
                delay_time = 0
            ###########################################################################################################
            # 单帧多帧区分
            try:
                # 解析成list 格式 ；形式为tx_frame_data
                tx_frame_data = tx_data.childNodes[0].data
                tx_frame_data = bytearray.fromhex(tx_frame_data)
                tx_frame_data = list(map(int, tx_frame_data))
                # 此处开始处理多帧fsm
                # 此为sf
                if len(tx_frame_data) <= 7:
                    tx_frame_data_sf_dl = int(len(tx_frame_data))
                    tx_frame_data.insert(0, tx_frame_data_sf_dl)
                    tx_frame_data_sf_padding = []
                    tx_frame_data_sf_dl = 7 - tx_frame_data_sf_dl
                    for i in range(tx_frame_data_sf_dl):
                        tx_frame_data_sf_padding.append(0)
                    tx_frame_data_sf = tx_frame_data + tx_frame_data_sf_padding
                    tx_frame_data = tx_frame_data_sf
                    msg = can.Message(arbitration_id=0x767,
                                      data=tx_frame_data_sf,
                                      is_extended_id=False)
                    # 调用驱动
                    bus.send(msg)
                    # 界面显示 CAN tx frame
                    tx_frame_id = str(hex(msg.arbitration_id))
                    tx_frame_len = str(msg.dlc)
                    tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                    tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                        tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                        tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                    tx_frame_time = str(round(time.perf_counter(), 3))
                    tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                    print(tx_frame)
                    # 发送信号到界面
                    self.signal_send_str_to_ui.emit(tx_frame)
                    # 获取 time out
                    wait_time = wait_time.childNodes[0].data
                    wait_time = int(wait_time) / 1000
                    print(wait_time)
                    # 设置等待回复的时间
                    time_left = wait_time + time.time() + delay_time
                    time_start = 0
                    recv_data_flag = 0
                    try:
                        # 在time out 下一直接收数据
                        while (time_left - time_start) > 0:
                            time_start = time.time()
                            msg = bus.recv(0)
                            if msg is not None and msg.arbitration_id != 0:
                                recv_data_flag = 1
                                # 收到特定ID的数据
                                rx_frame_id = str(hex(msg.arbitration_id))
                                rx_frame_len = str(msg.dlc)
                                rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                                rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                    rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                    rx_frame_data[14:16])
                                rx_frame_time = str(round(time.perf_counter(), 3))
                                rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                                print(rx_frame)
                                self.signal_send_str_to_ui.emit(rx_frame)

                                # 接收错误判断处理
                                if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                    error_handler = error_judgment_processing(rx_frame_data[9:11])
                                    self.signal_send_str_to_ui.emit(error_handler)
                                if rx_frame_data[0:2] == '10':
                                    msg = can.Message(arbitration_id=0x767,
                                                      data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                      is_extended_id=False)
                                    # CAN tx frame
                                    tx_frame_id = str(hex(msg.arbitration_id))
                                    tx_frame_len = str(msg.dlc)
                                    tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                    tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                        tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                                        tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                        tx_frame_data[14:16])
                                    tx_frame_time = str(round(time.perf_counter(), 3))
                                    tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                    bus.send(msg)
                                    print(tx_frame)
                                    self.signal_send_str_to_ui.emit(tx_frame)
                                    # 与文件接收标准数据对比
                                    print(rx_frame_data)
                                    rx_id = case.getElementsByTagName('rx_id')[0]
                                    print("rx_id: %s" % rx_id.childNodes[0].data)
                                    rx_data = case.getElementsByTagName('rx_data')[0]
                                    print("rx: %s" % rx_data.childNodes[0].data)
                                    rx_data = rx_data.childNodes[0].data
                                    print(rx_data)
                                    if evaluation_system_result(rx_data, rx_frame_data[0:11]):
                                        expect_the_result = 'expected :' + rx_data
                                        actual_the_result = 'actual   :' + rx_frame_data[0:11]
                                        dividing_line = '***************************************************'
                                        result = 'result   :pass'
                                        # todo 显示到ui
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        self.signal_send_str_to_ui.emit(expect_the_result)
                                        self.signal_send_str_to_ui.emit(actual_the_result)
                                        self.signal_send_str_to_ui.emit(result)
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        # todo 显示到LCD
                                        pass_count = pass_count + 1
                                        self.signal_send_str_to_lcd_pass.emit(str(pass_count))
                                    else:
                                        expect_the_result = 'expected :' + rx_data
                                        actual_the_result = 'actual   :' + rx_frame_data
                                        dividing_line = '***************************************************'
                                        result = 'result   :error'
                                        # todo 显示到ui
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        self.signal_send_str_to_ui.emit(expect_the_result)
                                        self.signal_send_str_to_ui.emit(actual_the_result)
                                        self.signal_send_str_to_ui.emit(result)
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        # todo 显示到LCD
                                        error_count = error_count + 1
                                        self.signal_send_str_to_lcd_error.emit(str(error_count))
                                else:
                                    # 与文件接收标准数据对比
                                    print(rx_frame_data)
                                    rx_frame_data_sf_len = int(rx_frame_data[0:2])
                                    rx_id = case.getElementsByTagName('rx_id')[0]
                                    print("rx_id: %s" % rx_id.childNodes[0].data)
                                    rx_data = case.getElementsByTagName('rx_data')[0]
                                    print("rx: %s" % rx_data.childNodes[0].data)
                                    rx_data = rx_data.childNodes[0].data
                                    print(rx_data)
                                    if evaluation_system_result(rx_data, rx_frame_data[3:4 + rx_frame_data_sf_len * 2]):
                                        expect_the_result = 'expected :' + rx_data
                                        actual_the_result = 'actual   :' + rx_frame_data[3:4 + rx_frame_data_sf_len * 2]
                                        dividing_line = '***************************************************'
                                        result = 'result   :pass'
                                        # todo 显示到ui
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        self.signal_send_str_to_ui.emit(expect_the_result)
                                        self.signal_send_str_to_ui.emit(actual_the_result)
                                        self.signal_send_str_to_ui.emit(result)
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        # todo 显示到LCD
                                        pass_count = pass_count + 1
                                        self.signal_send_str_to_lcd_pass.emit(str(pass_count))
                                    else:
                                        expect_the_result = 'expected :' + rx_data
                                        actual_the_result = 'actual   :' + rx_frame_data
                                        dividing_line = '***************************************************'
                                        result = 'result   :error'
                                        # todo 显示到ui
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        self.signal_send_str_to_ui.emit(expect_the_result)
                                        self.signal_send_str_to_ui.emit(actual_the_result)
                                        self.signal_send_str_to_ui.emit(result)
                                        self.signal_send_str_to_ui.emit(dividing_line)
                                        # todo 显示到LCD
                                        error_count = error_count + 1
                                        self.signal_send_str_to_lcd_error.emit(str(error_count))
                        else:
                            # 与文件接收标准数据对比
                            if recv_data_flag == 0:
                                rx_frame_data = 'NULL'
                                rx_data = case.getElementsByTagName('rx_data')[0]
                                print("rx: %s" % rx_data.childNodes[0].data)
                                rx_data = rx_data.childNodes[0].data
                                print(rx_data)
                                if evaluation_system_result(rx_data, rx_frame_data):
                                    expect_the_result = 'expected :' + rx_data
                                    actual_the_result = 'actual   :' + rx_frame_data
                                    dividing_line = '***************************************************'
                                    result = 'result   :pass'
                                    # todo 显示到ui
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    self.signal_send_str_to_ui.emit(expect_the_result)
                                    self.signal_send_str_to_ui.emit(actual_the_result)
                                    self.signal_send_str_to_ui.emit(result)
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    # todo 显示到LCD
                                    pass_count = pass_count + 1
                                    self.signal_send_str_to_lcd_pass.emit(str(pass_count))
                                else:
                                    expect_the_result = 'expected :' + rx_data
                                    actual_the_result = 'actual   :' + rx_frame_data
                                    dividing_line = '***************************************************'
                                    result = 'result   :error'
                                    # todo 显示到ui
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    self.signal_send_str_to_ui.emit(expect_the_result)
                                    self.signal_send_str_to_ui.emit(actual_the_result)
                                    self.signal_send_str_to_ui.emit(result)
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    # todo 显示到LCD
                                    error_count = error_count + 1
                                    self.signal_send_str_to_lcd_error.emit(str(error_count))
                    except KeyboardInterrupt:
                        pass
                else:
                    tx_frame_data_ff = tx_frame_data
                    tx_frame_data_ff_dl = int(len(tx_frame_data))
                    tx_frame_data_ff_type = 16
                    tx_frame_data_ff.insert(0, tx_frame_data_ff_type)
                    tx_frame_data_ff.insert(1, tx_frame_data_ff_dl)
                    # 此为ff
                    tx_frame_data_ff = tx_frame_data_ff[0:8]
                    msg = can.Message(arbitration_id=0x767,
                                      data=tx_frame_data_ff,
                                      is_extended_id=False)
                    # 调用驱动
                    bus.send(msg)
                    # 界面显示 CAN tx frame
                    tx_frame_id = str(hex(msg.arbitration_id))
                    tx_frame_len = str(msg.dlc)
                    tx_frame_data_ff = str(binascii.hexlify(msg.data).decode().upper())
                    tx_frame_data_ff = "%s %s %s %s %s %s %s %s" % (
                        tx_frame_data_ff[0:2], tx_frame_data_ff[2:4], tx_frame_data_ff[4:6], tx_frame_data_ff[6:8],
                        tx_frame_data_ff[8:10], tx_frame_data_ff[10:12], tx_frame_data_ff[12:14],
                        tx_frame_data_ff[14:16])
                    tx_frame_time = str(round(time.perf_counter(), 3))
                    tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_ff + '  ' + tx_frame_time
                    print(tx_frame)
                    # 发送信号到界面
                    self.signal_send_str_to_ui.emit(tx_frame)
                    # 设置等待回复的时间
                    time_left = 0.01 + time.time()
                    time_start = 0
                    try:
                        # 在time out 下一直接收数据
                        while (time_left - time_start) > 0:
                            time_start = time.time()
                            msg = bus.recv(0)
                            if msg is not None and msg.arbitration_id != 0:
                                # 收到特定ID的数据
                                rx_frame_id = str(hex(msg.arbitration_id))
                                rx_frame_len = str(msg.dlc)
                                rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                                rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                    rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                    rx_frame_data[14:16])
                                rx_frame_time = str(round(time.perf_counter(), 3))
                                rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                                print(rx_frame)
                                self.signal_send_str_to_ui.emit(rx_frame)
                                # 接收错误判断处理
                                if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                    error_handler = error_judgment_processing(rx_frame_data[9:11])
                                    self.signal_send_str_to_ui.emit(error_handler)
                    except KeyboardInterrupt:
                        pass
                    # cf
                    tx_frame_data_cf_dl = int(len(tx_frame_data)) - 8
                    if (tx_frame_data_cf_dl / 7) > (tx_frame_data_cf_dl // 7):
                        tx_frame_data_cf_sn = (tx_frame_data_cf_dl // 7) + 1
                    else:
                        tx_frame_data_cf_sn = tx_frame_data_cf_dl // 7
                    tx_frame_data_cf_type = 33
                    if tx_frame_data_cf_sn == 1:
                        tx_frame_data_cf_padding = []
                        tx_frame_data_cf = tx_frame_data[8:(8 + tx_frame_data_cf_dl)]
                        tx_frame_data_cf_dl = 7 - tx_frame_data_cf_dl
                        for i in range(tx_frame_data_cf_dl):
                            tx_frame_data_cf_padding.append(0)
                        tx_frame_data_cf.insert(0, tx_frame_data_cf_type)
                        tx_frame_data_cf = tx_frame_data_cf + tx_frame_data_cf_padding
                        msg = can.Message(arbitration_id=0x767,
                                          data=tx_frame_data_cf,
                                          is_extended_id=False)
                        # 调用驱动
                        bus.send(msg)
                        # 界面显示 CAN tx frame
                        tx_frame_id = str(hex(msg.arbitration_id))
                        tx_frame_len = str(msg.dlc)
                        tx_frame_data_cf = str(binascii.hexlify(msg.data).decode().upper())
                        tx_frame_data_cf = "%s %s %s %s %s %s %s %s" % (
                            tx_frame_data_cf[0:2], tx_frame_data_cf[2:4], tx_frame_data_cf[4:6], tx_frame_data_cf[6:8],
                            tx_frame_data_cf[8:10], tx_frame_data_cf[10:12], tx_frame_data_cf[12:14],
                            tx_frame_data_cf[14:16])
                        tx_frame_time = str(round(time.perf_counter(), 3))
                        tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_cf + '  ' + tx_frame_time
                        print(tx_frame)
                        # 发送信号到界面
                        self.signal_send_str_to_ui.emit(tx_frame)
                    else:
                        for i in range(tx_frame_data_cf_sn - 1):
                            tx_frame_data_cf = tx_frame_data[8 * (i + 1):8 * (i + 1) + 7]
                            tx_frame_data_cf.insert(0, (tx_frame_data_cf_type + i))
                            msg = can.Message(arbitration_id=0x767,
                                              data=tx_frame_data_cf,
                                              is_extended_id=False)
                            # 调用驱动
                            bus.send(msg)
                            # 界面显示 CAN tx frame
                            tx_frame_id = str(hex(msg.arbitration_id))
                            tx_frame_len = str(msg.dlc)
                            tx_frame_data_cf = str(binascii.hexlify(msg.data).decode().upper())
                            tx_frame_data_cf = "%s %s %s %s %s %s %s %s" % (
                                tx_frame_data_cf[0:2], tx_frame_data_cf[2:4], tx_frame_data_cf[4:6],
                                tx_frame_data_cf[6:8],
                                tx_frame_data_cf[8:10], tx_frame_data_cf[10:12], tx_frame_data_cf[12:14],
                                tx_frame_data_cf[14:16])
                            tx_frame_time = str(round(time.perf_counter(), 3))
                            tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_cf + '  ' + tx_frame_time
                            print(tx_frame)
                            # 发送信号到界面
                            self.signal_send_str_to_ui.emit(tx_frame)
                        # last cf
                        tx_frame_data_cf = tx_frame_data[8 * tx_frame_data_cf_sn:8 * tx_frame_data_cf_sn + 7]
                        tx_frame_data_cf.insert(0, (tx_frame_data_cf_type + tx_frame_data_cf_sn - 1))
                        tx_frame_data_cf_padding = []
                        tx_frame_data_cf_dl = 7 * tx_frame_data_cf_sn - tx_frame_data_cf_dl + 1
                        for i in range(tx_frame_data_cf_dl):
                            tx_frame_data_cf_padding.append(0)
                        tx_frame_data_cf = tx_frame_data_cf + tx_frame_data_cf_padding
                        msg = can.Message(arbitration_id=0x67F,
                                          data=tx_frame_data_cf,
                                          is_extended_id=False)
                        # 调用驱动
                        bus.send(msg)
                        # 界面显示 CAN tx frame
                        tx_frame_id = str(hex(msg.arbitration_id))
                        tx_frame_len = str(msg.dlc)
                        tx_frame_data_cf = str(binascii.hexlify(msg.data).decode().upper())
                        tx_frame_data_cf = "%s %s %s %s %s %s %s %s" % (
                            tx_frame_data_cf[0:2], tx_frame_data_cf[2:4], tx_frame_data_cf[4:6], tx_frame_data_cf[6:8],
                            tx_frame_data_cf[8:10], tx_frame_data_cf[10:12], tx_frame_data_cf[12:14],
                            tx_frame_data_cf[14:16])
                        tx_frame_time = str(round(time.perf_counter(), 3))
                        tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_cf + '  ' + tx_frame_time
                        print(tx_frame)
                        # 发送信号到界面
                        self.signal_send_str_to_ui.emit(tx_frame)
                    # 获取 time out
                    wait_time = wait_time.childNodes[0].data
                    wait_time = int(wait_time) / 1000
                    print(wait_time)
                    # 设置等待回复的时间
                    time_left = wait_time + time.time() + delay_time
                    time_start = 0
                    try:
                        # 在time out 下一直接收数据
                        while (time_left - time_start) > 0:
                            time_start = time.time()
                            msg = bus.recv(0)
                            if msg is not None and msg.arbitration_id != 0:
                                # 收到特定ID的数据
                                rx_frame_id = str(hex(msg.arbitration_id))
                                rx_frame_len = str(msg.dlc)
                                rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                                rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                    rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                    rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                    rx_frame_data[14:16])
                                rx_frame_time = str(round(time.perf_counter(), 3))
                                rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                                print(rx_frame)
                                self.signal_send_str_to_ui.emit(rx_frame)

                                # 接收错误判断处理
                                if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                    error_handler = error_judgment_processing(rx_frame_data[9:11])
                                    self.signal_send_str_to_ui.emit(error_handler)
                                # 与文件接收标准数据对比
                                print(rx_frame_data)
                                rx_id = case.getElementsByTagName('rx_id')[0]
                                print("rx_id: %s" % rx_id.childNodes[0].data)
                                rx_data = case.getElementsByTagName('rx_data')[0]
                                print("rx: %s" % rx_data.childNodes[0].data)
                                rx_data = rx_data.childNodes[0].data
                                print(rx_data)
                                if evaluation_system_result(rx_data, rx_frame_data[0:11]):
                                    expect_the_result = 'expected :' + rx_data
                                    actual_the_result = 'actual   :' + rx_frame_data[0:11]
                                    dividing_line = '***************************************************'
                                    result = 'result   :pass'
                                    # todo 显示到ui
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    self.signal_send_str_to_ui.emit(expect_the_result)
                                    self.signal_send_str_to_ui.emit(actual_the_result)
                                    self.signal_send_str_to_ui.emit(result)
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    # todo 显示到LCD
                                    pass_count = pass_count + 1
                                    self.signal_send_str_to_lcd_pass.emit(str(pass_count))
                                else:
                                    expect_the_result = 'expected :' + rx_data
                                    actual_the_result = 'actual   :' + rx_frame_data
                                    dividing_line = '***************************************************'
                                    result = 'result   :error'
                                    # todo 显示到ui
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    self.signal_send_str_to_ui.emit(expect_the_result)
                                    self.signal_send_str_to_ui.emit(actual_the_result)
                                    self.signal_send_str_to_ui.emit(result)
                                    self.signal_send_str_to_ui.emit(dividing_line)
                                    # todo 显示到LCD
                                    error_count = error_count + 1
                                    self.signal_send_str_to_lcd_error.emit(str(error_count))
                    except KeyboardInterrupt:
                        pass
            except can.CanError:
                print("Message NOT sent")


# CAN FRAME 接收线程
class Thread_dtc_info(QThread):
    signal_send_str_to_ui = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        msg = can.Message(arbitration_id=0x7DF,
                          data=[0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00],
                          is_extended_id=False)
        bus.send(msg)
        print(msg)
        time.sleep(0.5)
        msg = can.Message(arbitration_id=0x767,
                          data=[0x02, 0x10, 0x83, 0x00, 0x00, 0x00, 0x00, 0x00],
                          is_extended_id=False)
        bus.send(msg)
        print(msg)
        time.sleep(0.5)
        msg = can.Message(arbitration_id=0x767,
                          data=[0x03, 0x19, 0x02, 0x09, 0x00, 0x00, 0x00, 0x00],
                          is_extended_id=False)
        bus.send(msg)
        print(msg)
        while True:
            msg = bus.recv(1)
            if msg is not None and msg.arbitration_id == 0x777:
                rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                    rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                    rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                    rx_frame_data[14:16])
                if rx_frame_data[0:2] == '10':
                    msg = can.Message(arbitration_id=0x767,
                                      data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                      is_extended_id=False)
                    bus.send(msg)
                    print(msg)
                else:
                    print(msg)


class Thread_general_send_frame(QThread):
    # 创建一个信号从信号发送到UI主线程
    signal_send_str_to_ui = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):

        # 使用minidom解析器打开 XML 文档
        DOMTree_codings_session = xml.dom.minidom.parse(version_file_path)
        test_codings_session = DOMTree_codings_session.documentElement
        if test_codings_session.hasAttribute("shelf"):
            print("Root element : %s" % test_codings_session.getAttribute("shelf"))
        # 在集合中获取所有case list
        case_list_codings_session = test_codings_session.getElementsByTagName("case")

        for case_codings_session in case_list_codings_session:
            print("*****case-list*****")
            if case_codings_session.hasAttribute("title"):
                print("Title: %s" % case_codings_session.getAttribute("title"))
                # todo 显示到ui
                block_line = '                                  '
                self.signal_send_str_to_ui.emit(block_line)
                self.signal_send_str_to_ui.emit("Title: %s" % case_codings_session.getAttribute("title"))
                #######################################################################################################
                # 从xml 获取要发送的数据
                tx_id = case_codings_session.getElementsByTagName('tx_id')[0]
                print("tx_id: %s" % tx_id.childNodes[0].data)
                tx_id = tx_id.childNodes[0].data
                tx_id = int(tx_id, 16)
                tx_data = case_codings_session.getElementsByTagName('tx_data')[0]
                print("tx_data: %s" % tx_data.childNodes[0].data)
                wait_time = case_codings_session.getElementsByTagName('wait_time')[0]
                print("wait_time: %s" % wait_time.childNodes[0].data)

                # todo delay time
                if case_codings_session.getElementsByTagName('delay_time'):
                    delay_time = case_codings_session.getElementsByTagName('delay_time')[0]
                    print("delay_time: %s" % delay_time.childNodes[0].data)
                    # 获取 delay time
                    delay_time = delay_time.childNodes[0].data
                    delay_time = int(delay_time) / 1000
                else:
                    delay_time = 0
                ######################################################################################################
                # 单帧多帧区分
                try:
                    # 解析成list 格式 ；形式为tx_frame_data
                    tx_frame_data = tx_data.childNodes[0].data
                    tx_frame_data = bytearray.fromhex(tx_frame_data)
                    tx_frame_data = list(map(int, tx_frame_data))
                    # 此处开始处理多帧fsm
                    # 此为sf
                    if len(tx_frame_data) <= 7:
                        tx_frame_data_sf_dl = int(len(tx_frame_data))
                        tx_frame_data.insert(0, tx_frame_data_sf_dl)
                        tx_frame_data_sf_padding = []
                        tx_frame_data_sf_dl = 7 - tx_frame_data_sf_dl
                        for i in range(tx_frame_data_sf_dl):
                            tx_frame_data_sf_padding.append(0)
                        tx_frame_data_sf = tx_frame_data + tx_frame_data_sf_padding
                        tx_frame_data = tx_frame_data_sf
                        msg = can.Message(arbitration_id=tx_id,
                                          data=tx_frame_data_sf,
                                          is_extended_id=False)
                        # 调用驱动
                        bus.send(msg)
                        # 界面显示 CAN tx frame
                        tx_frame_id = str(hex(msg.arbitration_id))
                        tx_frame_len = str(msg.dlc)
                        tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                        tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                            tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6], tx_frame_data[6:8],
                            tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14], tx_frame_data[14:16])
                        tx_frame_time = str(round(time.perf_counter(), 3))
                        tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                        print(tx_frame)
                        # 发送信号到界面
                        self.signal_send_str_to_ui.emit(tx_frame)
                        # 获取 time out
                        wait_time = wait_time.childNodes[0].data
                        wait_time = int(wait_time) / 1000
                        print(wait_time)
                        # 设置等待回复的时间
                        time_left = wait_time + time.time() + delay_time
                        time_start = 0
                        try:
                            # 在time out 下一直接收数据
                            while (time_left - time_start) > 0:
                                time_start = time.time()
                                msg = bus.recv(0)
                                if msg is not None and msg.arbitration_id != 0:
                                    # 收到特定ID的数据
                                    rx_frame_id = str(hex(msg.arbitration_id))
                                    rx_frame_len = str(msg.dlc)
                                    rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                                    rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                        rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                        rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                        rx_frame_data[14:16])
                                    rx_frame_time = str(round(time.perf_counter(), 3))
                                    rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                                    print(rx_frame)
                                    self.signal_send_str_to_ui.emit(rx_frame)

                                    # 接收错误判断处理
                                    if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                        error_handler = error_judgment_processing(rx_frame_data[9:11])
                                        self.signal_send_str_to_ui.emit(error_handler)
                                    if rx_frame_data[0:2] == '10':
                                        msg = can.Message(arbitration_id=tx_id,
                                                          data=[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                                                          is_extended_id=False)
                                        # CAN tx frame
                                        tx_frame_id = str(hex(msg.arbitration_id))
                                        tx_frame_len = str(msg.dlc)
                                        tx_frame_data = str(binascii.hexlify(msg.data).decode().upper())
                                        tx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                            tx_frame_data[0:2], tx_frame_data[2:4], tx_frame_data[4:6],
                                            tx_frame_data[6:8],
                                            tx_frame_data[8:10], tx_frame_data[10:12], tx_frame_data[12:14],
                                            tx_frame_data[14:16])
                                        tx_frame_time = str(round(time.perf_counter(), 3))
                                        tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data + '  ' + tx_frame_time
                                        bus.send(msg)
                                        print(tx_frame)
                                        self.signal_send_str_to_ui.emit(tx_frame)
                                        # # 与文件接收标准数据对比
                                        if rx_frame_data[6:8] == '62':
                                            did_ff_len = diag_read_interpreter_ff_len(rx_frame_data)
                                            did_ff_data = diag_read_interpreter_ff_data(rx_frame_data)
                                            did_cf_len = int(did_ff_len) - 3
                                            did_m_data = ''
                                    elif rx_frame_data[0:1] == '2':
                                        if did_cf_len - 7 > 0:
                                            did_cf_len = did_cf_len - 7
                                            did_cf_data = diag_read_interpreter_cf_data(rx_frame_data, 7)
                                            did_m_data = did_m_data + did_cf_data
                                        else:
                                            did_cf_data = diag_read_interpreter_cf_data(rx_frame_data, did_cf_len)
                                            did_m_data = did_m_data + did_cf_data
                                            did_m_data = did_ff_data + did_m_data
                                            self.signal_send_str_to_ui.emit(
                                                'did_length:' + did_ff_len)
                                            self.signal_send_str_to_ui.emit(
                                                'did_data:' + did_m_data)
                                            self.signal_send_str_to_ui.emit(
                                                'did_interpreter:' + diag_read_interpreter_cf_data_interpreter(
                                                    did_m_data))
                                    else:
                                        # # 与文件接收标准数据对比
                                        if rx_frame_data[3:5] == '62':
                                            self.signal_send_str_to_ui.emit(
                                                ('did_length:' + diag_read_interpreter_sf_len(rx_frame_data)))
                                            self.signal_send_str_to_ui.emit(
                                                ('did_data:' + diag_read_interpreter_sf_data(rx_frame_data)))
                                            self.signal_send_str_to_ui.emit(
                                                ('did_interpreter:' + diag_read_interpreter_sf_data_interpreter(
                                                    rx_frame_data)))
                        except KeyboardInterrupt:
                            pass
                    else:

                        tx_frame_data_ff = tx_frame_data
                        tx_frame_data_ff_dl = int(len(tx_frame_data))
                        tx_frame_data_ff_type = 16
                        tx_frame_data_ff.insert(0, tx_frame_data_ff_type)
                        tx_frame_data_ff.insert(1, tx_frame_data_ff_dl)
                        # 此为ff
                        tx_frame_data_ff = tx_frame_data_ff[0:8]
                        msg = can.Message(arbitration_id=tx_id,
                                          data=tx_frame_data_ff,
                                          is_extended_id=False)
                        # 调用驱动
                        bus.send(msg)
                        # 界面显示 CAN tx frame
                        tx_frame_id = str(hex(msg.arbitration_id))
                        tx_frame_len = str(msg.dlc)
                        tx_frame_data_ff = str(binascii.hexlify(msg.data).decode().upper())
                        tx_frame_data_ff = "%s %s %s %s %s %s %s %s" % (
                            tx_frame_data_ff[0:2], tx_frame_data_ff[2:4], tx_frame_data_ff[4:6], tx_frame_data_ff[6:8],
                            tx_frame_data_ff[8:10], tx_frame_data_ff[10:12], tx_frame_data_ff[12:14],
                            tx_frame_data_ff[14:16])
                        tx_frame_time = str(round(time.perf_counter(), 3))
                        tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_ff + '  ' + tx_frame_time
                        print(tx_frame)
                        # 发送信号到界面
                        self.signal_send_str_to_ui.emit(tx_frame)
                        # 设置等待回复的时间
                        time_left = 0.01 + time.time()
                        time_start = 0
                        try:
                            # 在time out 下一直接收数据
                            while (time_left - time_start) > 0:
                                time_start = time.time()
                                msg = bus.recv(0)
                                if msg is not None and msg.arbitration_id != 0:
                                    # 收到特定ID的数据
                                    rx_frame_id = str(hex(msg.arbitration_id))
                                    rx_frame_len = str(msg.dlc)
                                    rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                                    rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                        rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                        rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                        rx_frame_data[14:16])
                                    rx_frame_time = str(round(time.perf_counter(), 3))
                                    rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                                    print(rx_frame)
                                    self.signal_send_str_to_ui.emit(rx_frame)
                                    # 接收错误判断处理
                                    if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                        error_handler = error_judgment_processing(rx_frame_data[9:11])
                                        self.signal_send_str_to_ui.emit(error_handler)
                        except KeyboardInterrupt:
                            pass
                        # cf
                        tx_frame_data_cf_dl = int(len(tx_frame_data)) - 8
                        if (tx_frame_data_cf_dl / 7) > (tx_frame_data_cf_dl // 7):
                            tx_frame_data_cf_sn = (tx_frame_data_cf_dl // 7) + 1
                        else:
                            tx_frame_data_cf_sn = tx_frame_data_cf_dl // 7
                        tx_frame_data_cf_type = 33
                        if tx_frame_data_cf_sn == 1:
                            tx_frame_data_cf_padding = []
                            tx_frame_data_cf = tx_frame_data[8:(8 + tx_frame_data_cf_dl)]
                            tx_frame_data_cf_dl = 7 - tx_frame_data_cf_dl
                            for i in range(tx_frame_data_cf_dl):
                                tx_frame_data_cf_padding.append(0)
                            tx_frame_data_cf.insert(0, tx_frame_data_cf_type)
                            tx_frame_data_cf = tx_frame_data_cf + tx_frame_data_cf_padding
                            msg = can.Message(arbitration_id=tx_id,
                                              data=tx_frame_data_cf,
                                              is_extended_id=False)
                            # 调用驱动
                            bus.send(msg)
                            # 界面显示 CAN tx frame
                            tx_frame_id = str(hex(msg.arbitration_id))
                            tx_frame_len = str(msg.dlc)
                            tx_frame_data_cf = str(binascii.hexlify(msg.data).decode().upper())
                            tx_frame_data_cf = "%s %s %s %s %s %s %s %s" % (
                                tx_frame_data_cf[0:2], tx_frame_data_cf[2:4], tx_frame_data_cf[4:6],
                                tx_frame_data_cf[6:8],
                                tx_frame_data_cf[8:10], tx_frame_data_cf[10:12], tx_frame_data_cf[12:14],
                                tx_frame_data_cf[14:16])
                            tx_frame_time = str(round(time.perf_counter(), 3))
                            tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_cf + '  ' + tx_frame_time
                            print(tx_frame)
                            # 发送信号到界面
                            self.signal_send_str_to_ui.emit(tx_frame)
                        else:
                            for i in range(tx_frame_data_cf_sn - 1):
                                tx_frame_data_cf = tx_frame_data[8 * (i + 1):8 * (i + 1) + 7]
                                tx_frame_data_cf.insert(0, (tx_frame_data_cf_type + i))
                                msg = can.Message(arbitration_id=tx_id,
                                                  data=tx_frame_data_cf,
                                                  is_extended_id=False)
                                # 调用驱动
                                bus.send(msg)
                                # 界面显示 CAN tx frame
                                tx_frame_id = str(hex(msg.arbitration_id))
                                tx_frame_len = str(msg.dlc)
                                tx_frame_data_cf = str(binascii.hexlify(msg.data).decode().upper())
                                tx_frame_data_cf = "%s %s %s %s %s %s %s %s" % (
                                    tx_frame_data_cf[0:2], tx_frame_data_cf[2:4], tx_frame_data_cf[4:6],
                                    tx_frame_data_cf[6:8],
                                    tx_frame_data_cf[8:10], tx_frame_data_cf[10:12], tx_frame_data_cf[12:14],
                                    tx_frame_data_cf[14:16])
                                tx_frame_time = str(round(time.perf_counter(), 3))
                                tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_cf + '  ' + tx_frame_time
                                print(tx_frame)
                                # 发送信号到界面
                                self.signal_send_str_to_ui.emit(tx_frame)
                            # last cf
                            tx_frame_data_cf = tx_frame_data[8 * tx_frame_data_cf_sn:8 * tx_frame_data_cf_sn + 7]
                            tx_frame_data_cf.insert(0, (tx_frame_data_cf_type + tx_frame_data_cf_sn - 1))
                            tx_frame_data_cf_padding = []
                            tx_frame_data_cf_dl = 7 * tx_frame_data_cf_sn - tx_frame_data_cf_dl + 1
                            for i in range(tx_frame_data_cf_dl):
                                tx_frame_data_cf_padding.append(0)
                            tx_frame_data_cf = tx_frame_data_cf + tx_frame_data_cf_padding
                            msg = can.Message(arbitration_id=tx_id,
                                              data=tx_frame_data_cf,
                                              is_extended_id=False)
                            # 调用驱动
                            bus.send(msg)
                            # 界面显示 CAN tx frame
                            tx_frame_id = str(hex(msg.arbitration_id))
                            tx_frame_len = str(msg.dlc)
                            tx_frame_data_cf = str(binascii.hexlify(msg.data).decode().upper())
                            tx_frame_data_cf = "%s %s %s %s %s %s %s %s" % (
                                tx_frame_data_cf[0:2], tx_frame_data_cf[2:4], tx_frame_data_cf[4:6],
                                tx_frame_data_cf[6:8],
                                tx_frame_data_cf[8:10], tx_frame_data_cf[10:12], tx_frame_data_cf[12:14],
                                tx_frame_data_cf[14:16])
                            tx_frame_time = str(round(time.perf_counter(), 3))
                            tx_frame = tx_frame_id + '  ' + tx_frame_len + '  ' + tx_frame_data_cf + '  ' + tx_frame_time
                            print(tx_frame)
                            # 发送信号到界面
                            self.signal_send_str_to_ui.emit(tx_frame)
                        # 获取 time out
                        wait_time = wait_time.childNodes[0].data
                        wait_time = int(wait_time) / 1000
                        print(wait_time)
                        # 设置等待回复的时间
                        time_left = wait_time + time.time() + delay_time
                        time_start = 0
                        try:
                            # 在time out 下一直接收数据
                            while (time_left - time_start) > 0:
                                time_start = time.time()
                                msg = bus.recv(0)
                                if msg is not None and msg.arbitration_id != 0:
                                    # 收到特定ID的数据
                                    rx_frame_id = str(hex(msg.arbitration_id))
                                    rx_frame_len = str(msg.dlc)
                                    rx_frame_data = binascii.hexlify(msg.data).decode().upper()
                                    rx_frame_data = "%s %s %s %s %s %s %s %s" % (
                                        rx_frame_data[0:2], rx_frame_data[2:4], rx_frame_data[4:6], rx_frame_data[6:8],
                                        rx_frame_data[8:10], rx_frame_data[10:12], rx_frame_data[12:14],
                                        rx_frame_data[14:16])
                                    rx_frame_time = str(round(time.perf_counter(), 3))
                                    rx_frame = rx_frame_id + '  ' + rx_frame_len + '  ' + rx_frame_data + '  ' + rx_frame_time
                                    print(rx_frame)
                                    self.signal_send_str_to_ui.emit(rx_frame)

                                    # 接收错误判断处理
                                    if rx_frame_data[3:5] == '7F' and rx_frame_data[9:11] != '78':
                                        error_handler = error_judgment_processing(rx_frame_data[9:11])
                                        self.signal_send_str_to_ui.emit(error_handler)
                        except KeyboardInterrupt:
                            pass
                except can.CanError:
                    print("Message NOT sent")
