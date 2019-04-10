# -*- coding:utf-8 -*-
import numpy as np
from scipy import io
from PyQt5 import QtCore
from .parameters import CBPY_TIMER_INTERVAL
from .data_aquisition import rContinuous

# # for simulator
FILENAME = 'data/ECG_sample.mat'
DATA_KEY = 'ECG'
STEP = CBPY_TIMER_INTERVAL*2    # 2kHz sampling


class vContinuous(rContinuous):
    def __init__(self, timer_interval=CBPY_TIMER_INTERVAL, filename=FILENAME, data_key=DATA_KEY, step=STEP):
        super(rContinuous, self).__init__()
        self.filename = filename
        self.init_params()
        _data = io.loadmat(filename)
        self.signal = _data[data_key][0]
        self.ref = _data[data_key][1]
        self.step = step
        self.data_len = len(self.signal)
        self.data_pos = 0
        self.trial = [[-1, np.array([])] for i in range(9)]
        # # for debug
        # t = np.arange(0, self.data_len)/2000.0
        # self.signal = np.sin(2*np.pi*t*50)*1000.0
        # self.ref = np.sin(2*np.pi*t*50)*1000.0
        # # timer:
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.setInterval(timer_interval)
        self.timer.timeout.connect(self._fetch_continuous)

    def _fetch_continuous(self):
        _sig = self.signal[self.data_pos:self.data_pos+self.step]
        _ref = self.ref[self.data_pos:self.data_pos+self.step]
        self.data_pos += self.step
        self.trial[0][1] = _sig
        self.trial[1][1] = _sig
        self.trial[2][1] = _sig
        self.trial[5][1] = _sig
        self.trial[6][1] = _sig
        self.trial[3][1] = _ref
        self.trial[4][1] = _ref
        self.trial[7][1] = _ref
        self.trial[8][1] = _ref
        self._set_buf()

    def __del__(self):
        pass


