# -*- coding:utf-8 -*-
import numpy as np
from PyQt5 import QtCore
from cerebus import cbpy


class rContinuous(QtCore.QThread):
    def __init__(self, timer_interval=50):
        super(rContinuous, self).__init__()
        self.is_connected = False
        self.init_cbpy()
        self.init_params()
        self.trial = None
        # timer:
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.setInterval(timer_interval)
        if self.is_connected:
            self.timer.timeout.connect(self._fetch_continuous)

    def init_cbpy(self):
        res, connection = cbpy.open(instance=0, connection='default')
        print('#connection', connection)
        if res != 0:
            self.is_connected = False
            print('ERROR: cbSdkOpen')
            return 1
        self.is_connected = True
        global CBPY_BUF_LEN
        res, reset = cbpy.trial_config(instance=0,
                                       reset=True,
                                       buffer_parameter={'continuous_length':CBPY_BUF_LEN},
                                       range_parameter={},
                                       noevent=True,
                                       nocontinuous=False,
                                       nocomment=True)
        if res != 0:
            print('ERROR: cbSdkSetTrialConfig')
            return 1
        return 0

    def _fetch_continuous(self):
        res, self.trial = cbpy.trial_continuous(instance=0, reset=True)
        if len(self.trial) > 0:
            self._set_buf()

    def _set_buf(self):
        self.ecg0_signal_buf = np.hstack((self.ecg0_signal_buf, self.trial[1][1]))
        self.ecg0_ref_buf = np.hstack((self.ecg0_ref_buf, self.trial[3][1]))
        self.ecg1_signal_buf = np.hstack((self.ecg1_signal_buf, self.trial[2][1]))
        self.ecg1_ref_buf = np.hstack((self.ecg1_ref_buf, self.trial[4][1]))
        self.ecg2_signal_buf = np.hstack((self.ecg2_signal_buf, self.trial[5][1]))
        self.ecg2_ref_buf = np.hstack((self.ecg2_ref_buf, self.trial[7][1]))
        self.ecg3_signal_buf = np.hstack((self.ecg3_signal_buf, self.trial[6][1]))
        self.ecg3_ref_buf = np.hstack((self.ecg3_ref_buf, self.trial[8][1]))

    def ecg0_get_func(self):
        if self.ecg0_subref: self.ecg0_signal_buf -= self.ecg0_ref_buf
        if self.ecg0_invert: self.ecg0_signal_buf *= -1
        res = np.copy(self.ecg0_signal_buf) if len(self.ecg0_signal_buf) > 0 else None
        self.ecg0_signal_buf = np.array([], dtype=np.int16)
        self.ecg0_ref_buf = np.array([], dtype=np.int16)
        return res

    def ecg1_get_func(self):
        if self.ecg1_subref: self.ecg1_signal_buf -= self.ecg1_ref_buf
        if self.ecg1_invert: self.ecg1_signal_buf *= -1
        res = np.copy(self.ecg1_signal_buf) if len(self.ecg1_signal_buf) > 0 else None
        self.ecg1_signal_buf = np.array([], dtype=np.int16)
        self.ecg1_ref_buf = np.array([], dtype=np.int16)
        return res

    def ecg2_get_func(self):
        if self.ecg2_subref: self.ecg2_signal_buf -= self.ecg2_ref_buf
        if self.ecg2_invert: self.ecg2_signal_buf *= -1
        res = np.copy(self.ecg2_signal_buf) if len(self.ecg2_signal_buf) > 0 else None
        self.ecg2_signal_buf = np.array([], dtype=np.int16)
        self.ecg2_ref_buf = np.array([], dtype=np.int16)
        return res

    def ecg3_get_func(self):
        if self.ecg3_subref: self.ecg3_signal_buf -= self.ecg3_ref_buf
        if self.ecg3_invert: self.ecg3_signal_buf *= -1
        res = np.copy(self.ecg3_signal_buf) if len(self.ecg3_signal_buf) > 0 else None
        self.ecg3_signal_buf = np.array([], dtype=np.int16)
        self.ecg3_ref_buf = np.array([], dtype=np.int16)
        return res

    def ecg0_subref_setting(self, subref=False):
        self.ecg0_subref = subref

    def ecg0_invert_setting(self, invert=False):
        self.ecg0_invert = invert

    def ecg1_subref_setting(self, subref=False):
        self.ecg1_subref = subref

    def ecg1_invert_setting(self, invert=False):
        self.ecg1_invert = invert

    def ecg2_subref_setting(self, subref=False):
        self.ecg2_subref = subref

    def ecg2_invert_setting(self, invert=False):
        self.ecg2_invert = invert

    def ecg3_subref_setting(self, subref=False):
        self.ecg3_subref = subref

    def ecg3_invert_setting(self, invert=False):
        self.ecg3_invert = invert

    def init_params(self):
        # ECG0: ch3, 5
        self.ecg0_signal_buf = np.array([], dtype=np.int16)
        self.ecg0_ref_buf = np.array([], dtype=np.int16)
        self.ecg0_invert = False
        self.ecg0_subref = False
        # ECG1: ch4, 6
        self.ecg1_signal_buf = np.array([], dtype=np.int16)
        self.ecg1_ref_buf = np.array([], dtype=np.int16)
        self.ecg1_invert = False
        self.ecg1_subref = False
        # ECG2: ch27, 29
        self.ecg2_signal_buf = np.array([], dtype=np.int16)
        self.ecg2_ref_buf = np.array([], dtype=np.int16)
        self.ecg2_invert = False
        self.ecg2_subref = False
        # ECG3: ch28, 30
        self.ecg3_signal_buf = np.array([], dtype=np.int16)
        self.ecg3_ref_buf = np.array([], dtype=np.int16)
        self.ecg3_invert = False
        self.ecg3_subref = False

    def run(self):
        self.timer.start()
        self.exec_()

    def __del__(self):
        cbpy.close()


