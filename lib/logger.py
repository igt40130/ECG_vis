# -*- coding:utf-8 -*-
import numpy as np
import os
import datetime
import time
import sys
from PyQt5 import QtCore
from .parameters import *


class ECGLogger(QtCore.QObject):
    chdata_signal = QtCore.pyqtSignal(str)
    def __init__(self, group_name='GroupN', sampling_rate=2000.0):
        super(ECGLogger, self).__init__()
        self.log_format = '{time_stamp}, {phase}\r\n'
        self.group_name = group_name
        self.last_peak = 0
        self.cumulative_time = 0
        global LOG_SAVE_PATH
        self.save_path = LOG_SAVE_PATH.rstrip('/')
        self.exe_time = self.group_name + '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        self.save_filename = None
        self.is_recording = False
        self.fp = None
        self.ms_correction_div = sampling_rate/1000.0
        self.thresh_for_false_positive_inverval = 10 # ms

    @QtCore.pyqtSlot(str)
    def signal_manager(self, signal):
        if signal == 'start recording':
            print('start recording')
            self.start_recording()
        elif signal == 'stop recording':
            print('stop recording')
            self.stop_recording()

    def start_recording(self):
        if not self.is_recording:
            if sys.platform == 'win32':
                os.system('mkdir ' + '\\'.join([self.save_path, self.exe_time]))
            else:
                os.system('mkdir -p ' + '/'.join([self.save_path, self.exe_time]))
            now_datetime =  datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
            self.last_peak = 0
            self.cumulative_time = 0
            self.save_filename = '/'.join([self.save_path, self.exe_time, now_datetime + '.csv'])
            self.is_recording = True
            self.fp = open(self.save_filename, 'w')
            self.fp.write('#time_stamp, phase\r\n')

    def stop_recording(self):
        self.is_recording = False
        self.fp.close()

    def set_data(self, new_data_len, peak_pos_buf, phase):
        if self.is_recording:
            # print('Set Data')
            if new_data_len == 0: return 1
            elapsed_time = new_data_len/self.ms_correction_div
            peak_pos, = np.where(peak_pos_buf>0);
            peak_pos = peak_pos / self.ms_correction_div
            time_offset = peak_pos[0] if self.cumulative_time == 0 and len(peak_pos) > 0 else 0
            peak_pos = peak_pos + self.cumulative_time - time_offset
            self.cumulative_time += elapsed_time - time_offset
            if len(peak_pos) > 0:
                valid_peak = None
                for _peak in peak_pos:
                    # バッファの継ぎ目の誤検出を取り除く
                    if (_peak - self.last_peak) < self.thresh_for_false_positive_inverval:
                        pass
                    else:
                        valid_peak = _peak
                        self.fp.write(self.log_format.format(time_stamp=valid_peak, phase=phase))
                self.last_peak = valid_peak if valid_peak != None else \
                                           self.last_peak + elapsed_time - time_offset
            else:
                self.last_peak += elapsed_time - time_offset
