# -*- coding:utf-8 -*-
import numpy as np
from scipy import signal
from .parameters import *
from PyQt5 import QtCore


class OnlineHeartrateCalculator(QtCore.QThread):
    def __init__(self, buf_len=BUF_LEN, timer_interval=10, fetch_func=None, thresh_percentile=THRESH_PERCENTILE):
        super(OnlineHeartrateCalculator, self).__init__()
        # fetch data function
        self.fetch_func = self._fetch_func if fetch_func is None else fetch_func
        self.new_data = None
        self.cumulative_new_data_len = 0 # for plot
        # buffer
        self.buf_len = buf_len
        self.raw_buf = np.zeros(buf_len)
        self.filtered_buf = np.zeros(buf_len)
        # filter
        order = 3; focus_range = FOCUS_RANGE; nyquist_freq = 1000.0
        self.butter_a, self.butter_b = None, None
        self.apply_filter = None
        self.set_filter(order, focus_range, nyquist_freq)
        # notch filter
        notch_b, notch_a = signal.butter(3, [49.0/nyquist_freq, 51.0/nyquist_freq], btype='bandstop')
        self.apply_notch = lambda x: signal.lfilter(notch_b, notch_a, x)
        self.notch_enable = False
        # heart rate calculation
        self.thresh_percentile = thresh_percentile
        self.thresh_idx = int(self.buf_len * self.thresh_percentile / 100.0)
        self.over_thresh_buf = np.zeros(self.buf_len)
        self.peak_pos = np.asarray([])
        self.peak_pos_buf = np.zeros(self.buf_len)
        self.heart_rate = 0
        self.RR_interval = 0
        self.thresh_coef = OUTLIER_THRESH_COEF
        # timer:
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.setInterval(timer_interval)
        self.timer.timeout.connect(self.fetch_data)
        self.count = 0

    def run(self):
        self.timer.start()
        self.exec_()

    def flush_data_for_plot(self):
        _new_data_len = self.cumulative_new_data_len
        self.cumulative_new_data_len = 0
        return _new_data_len, self.filtered_buf[-_new_data_len:], \
            self.peak_pos_buf[-_new_data_len:], self.heart_rate, self.RR_interval

    def fetch_data(self):
        #start_time = time.perf_counter()
        self.new_data = self.fetch_func()
        self.count += 1
        if self.new_data is None:
            print('#Get no data!!', self.count)
            return 0;
        self.new_data = self.new_data/4 # scaling
        self.set_new_data(self.new_data)
        self.calc_heartrate()
        #elapsed_time = time.perf_counter() - start_time
        # print('elapsed time (ms):', round(elapsed_time*1000, 3))

    def calc_heartrate(self):
        sorted_buf = np.sort(self.filtered_buf)[::-1]
        self.thresh_val = sorted_buf[self.thresh_idx]
        self.over_thresh_buf = np.copy(self.filtered_buf)
        self.over_thresh_buf -= self.thresh_val
        self.over_thresh_buf[self.over_thresh_buf<0] = 0
        relmax_idx, = signal.argrelmax(self.over_thresh_buf, mode='wrap')
        self.peak_pos_buf[:] = 0
        if len(relmax_idx) == 0:
            self.peak_pos = np.asarray([])
            self.heart_rate = 0
            self.RR_interval = 0
        else:
            relmax_idx = self.remove_outlier(relmax_idx)
            interval = (relmax_idx[1:] - relmax_idx[:-1]) / 2.0  # 2kHz sampling
            self.heart_rate = (self.buf_len/2.0)/np.mean(interval) * 60  # 2kHz sampling
            self.RR_interval = np.mean(interval)
            self.peak_pos = np.copy(relmax_idx)
            self.peak_pos_buf[self.peak_pos] = 1
        # print('Heart rate(bpm) / interval(ms):', round(self.heart_rate, 1), round(self.RR_interval,1))

    def remove_outlier(self, relmax_idx):
        interval = (relmax_idx[1:] - relmax_idx[:-1]) / 2.0 # 2kHz sampling
        mean_val, std_val = np.mean(interval), np.std(interval)
        l_thresh, u_thresh = mean_val/self.thresh_coef, mean_val*self.thresh_coef
        # outlier_idx_array, = np.where(((interval<l_thresh)|(interval>u_thresh)))
        outlier_idx_array, = np.where(((interval<l_thresh))) # false positive のみを対象
        if len(outlier_idx_array) > 0:
            print('#Remove Outlier!')
            # print(interval, interval[outlier_idx_array])
            # # 外れ値のintervalを形成する前方のpeakを削除
            # # 心電図の波形的にR後に誤検出されるというheuristicsを入れている
            outlier_idx_list = list(outlier_idx_array + 1) # 前方の場合は+0
            outlier_idx = outlier_idx_list.pop(0)
            res = []
            for i, _relmax_id  in enumerate(relmax_idx):
                if i == outlier_idx:
                    outlier_idx = outlier_idx_list.pop(0) if len(outlier_idx_list)>0 else None
                else:
                    res.append(_relmax_id)
            res = np.asarray(res)
        else:
            res = relmax_idx
        return res

    def _fetch_func(self):
        print('Dummy fetch func was called!')
        return np.zeros(STEP)

    def set_new_data(self, new_data):
        new_data_len = self.buf_len if len(new_data) > self.buf_len else len(new_data)
        self.cumulative_new_data_len += new_data_len
        self.raw_buf = np.hstack((self.raw_buf, new_data))
        self.raw_buf = self.raw_buf[-self.buf_len:]
        self.filtered_buf = self.apply_filter(self.raw_buf)
        if self.notch_enable: self.filtered_buf = self.apply_notch(self.filtered_buf)

    def set_filter(self, order=3, focus_range=[150, 250], nyquist_freq=1000.0):
        self.butter_b, self.butter_a = signal.butter(order, [focus_range[0]/nyquist_freq, focus_range[1]/nyquist_freq], btype='band')
        self.apply_filter = lambda x: signal.lfilter(self.butter_b, self.butter_a, x)

    def set_thresh_percentile(self, thresh_percentile):
        self.thresh_percentile = thresh_percentile
        self.thresh_idx = int(self.buf_len * self.thresh_percentile / 100.0)

    def notch_setting(self, enable=False):
        self.notch_enable = enable
