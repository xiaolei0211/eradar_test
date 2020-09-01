# #检查文件的格式
# 1.文件名后缀是 *S19
# 2.文件有S0
# 3.文件S0内容正确；解析文件S0的内容并显示
# 4.文件有S7结束帧
import binascii

from PyQt5.QtCore import QObject, pyqtSignal


class Chery_file_format(QObject):
    signal_send_str_to_ui = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def check_cali_file_check(self, path):
        with open(path, 'r', encoding='utf-8') as check_file_app:
            app_file = check_file_app.readlines()
            app_file_header = app_file[0]
            app_file_ending = app_file[-1]
            app_file_first_line = app_file[1]
            app_file_start_address = app_file_first_line[4:12]
            app_file_end_address = app_file_ending[4:12]
            app_file_header = app_file_header.strip()
            if app_file_header[:2] == 'S0' and len(app_file_header) == 54 and app_file_header[50:52] == '02':
                app_file_header_id = app_file_header[9:12]
                app_file_header_supplier = app_file_header[12:18]
                app_file_header_supplier = app_file_header_supplier.strip()
                app_file_header_supplier = str(binascii.a2b_hex(app_file_header_supplier), encoding="utf-8")
                app_file_header_part_number = app_file_header[18:50]
                app_file_header_part_number = app_file_header_part_number.strip()
                app_file_header_part_number = str(binascii.a2b_hex(app_file_header_part_number), encoding="utf-8")
                app_file_header_module_id = app_file_header[50:52]

                self.signal_send_str_to_ui.emit('读取诊断ID：' + app_file_header_id)
                self.signal_send_str_to_ui.emit('读取供应商代码：' + app_file_header_supplier)
                self.signal_send_str_to_ui.emit('读取零件号：' + app_file_header_part_number)
                self.signal_send_str_to_ui.emit('读取文件类型：' + app_file_header_module_id + '(参数文件)')

                if app_file_ending[:2] == 'S7' and len(app_file_ending) == 14 and (
                        app_file_start_address == app_file_end_address):
                    self.signal_send_str_to_ui.emit('格式正确')
                else:
                    self.signal_send_str_to_ui.emit('格式不正确')
            else:
                self.signal_send_str_to_ui.emit('格式不正确')

    def check_app_file_check(self, path):
        with open(path, 'r', encoding='utf-8') as check_file_app:
            app_file = check_file_app.readlines()
            app_file_header = app_file[0]
            app_file_ending = app_file[-1]
            app_file_first_line = app_file[3]
            app_file_start_address = app_file_first_line[4:12]
            app_file_end_address = app_file_ending[4:12]
            app_file_header = app_file_header.strip()
            if app_file_header[:2] == 'S0' and len(app_file_header) == 70 and app_file_header[50:52] == '01':
                app_file_header_id = app_file_header[9:12]
                app_file_header_supplier = app_file_header[12:18]
                app_file_header_supplier = app_file_header_supplier.strip()
                app_file_header_supplier = str(binascii.a2b_hex(app_file_header_supplier), encoding="utf-8")
                app_file_header_part_number = app_file_header[18:50]
                app_file_header_part_number = app_file_header_part_number.strip()
                app_file_header_part_number = str(binascii.a2b_hex(app_file_header_part_number), encoding="utf-8")
                app_file_header_module_id = app_file_header[50:52]
                app_file_header_sw = app_file_header[52:68]
                app_file_header_sw = app_file_header_sw.strip()
                app_file_header_sw = str(binascii.a2b_hex(app_file_header_sw), encoding="utf-8")

                self.signal_send_str_to_ui.emit('读取诊断ID：' + app_file_header_id)
                self.signal_send_str_to_ui.emit('读取供应商代码：' + app_file_header_supplier)
                self.signal_send_str_to_ui.emit('读取零件号：' + app_file_header_part_number)
                self.signal_send_str_to_ui.emit('读取文件类型：' + app_file_header_module_id + '(应用文件)')
                self.signal_send_str_to_ui.emit('读取软件版本：' + app_file_header_sw)

                if app_file_ending[:2] == 'S7' and len(app_file_ending) == 14 and (
                        app_file_start_address == app_file_end_address):
                    self.signal_send_str_to_ui.emit('格式正确')
                else:
                    self.signal_send_str_to_ui.emit('格式不正确')
            else:
                self.signal_send_str_to_ui.emit('格式不正确')

    def check_flash_driver_file_check(self, path):
        with open(path, 'r', encoding='utf-8') as check_file_flash:
            flash_file = check_file_flash.readlines()
            flash_file_header = flash_file[0]
            flash_file_ending = flash_file[-1]
            flash_file_first_line = flash_file[1]
            flash_file_start_address = flash_file_first_line[4:12]
            flash_file_end_address = flash_file_ending[4:12]
            flash_file_header = flash_file_header.strip()
            if flash_file_header[:2] == 'S0' and len(flash_file_header) == 54 and flash_file_header[50:52] == '00':
                flash_file_header_id = flash_file_header[9:12]
                flash_file_header_supplier = flash_file_header[12:18]
                flash_file_header_supplier = flash_file_header_supplier.strip()
                flash_file_header_supplier = str(binascii.a2b_hex(flash_file_header_supplier), encoding="utf-8")
                flash_file_header_part_number = flash_file_header[18:50]
                flash_file_header_part_number = flash_file_header_part_number.strip()
                flash_file_header_part_number = str(binascii.a2b_hex(flash_file_header_part_number), encoding="utf-8")
                flash_file_header_module_id = flash_file_header[50:52]
                self.signal_send_str_to_ui.emit('读取诊断ID：' + flash_file_header_id)
                self.signal_send_str_to_ui.emit('读取供应商代码：' + flash_file_header_supplier)
                self.signal_send_str_to_ui.emit('读取零件号：' + flash_file_header_part_number)
                self.signal_send_str_to_ui.emit('读取文件类型：' + flash_file_header_module_id + '(驱动文件)')
                if flash_file_ending[:2] == 'S7' and len(flash_file_ending) == 14 and (
                        flash_file_start_address == flash_file_end_address):
                    self.signal_send_str_to_ui.emit('格式正确')
                else:
                    self.signal_send_str_to_ui.emit('格式不正确')
            else:
                self.signal_send_str_to_ui.emit('格式不正确')
