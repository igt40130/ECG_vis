# -*- coding:utf-8 -*-
import numpy as np
from .parameters import *
from PyQt5 import QtCore, QtGui
import pyqtgraph as pg
import time
from .logger import ECGLogger
from .heartrate_calcuration import OnlineHeartrateCalculator


class PlotWindow(QtGui.QWidget):
    plot_window_signal = QtCore.pyqtSignal(str)
    def __init__(self, title='Group N', fetch_func=None, color='#00ffff'):
        super(PlotWindow, self).__init__()
        # params
        self.phase = 0    # 薬物投与のタイミングの記録用
        self.phase_timestamp = '00:00:00'

        # buffer
        self.oscillo_buf_len = OSCILLO_BUF_LEN
        self.raw_buf = np.zeros(self.oscillo_buf_len)
        self.peak_buf = np.zeros(self.oscillo_buf_len)
        self.buf_pos = 0

        # recording
        self.is_recording = False
        self.recording_start_time = None
        self.logger = ECGLogger(title.replace(' ', '-'))
        self.plot_window_signal.connect(self.logger.signal_manager)

        #アップデート時間設定
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.oscillo_timer_interval = OSCILLO_TIMER_INTERVAL
        self.timer.start(self.oscillo_timer_interval)

        # UI
        self.initUI(title, color)

        # online heartrate calculation
        self.ohc_buf_len = BUF_LEN
        self.online_heartrate_calculator = OnlineHeartrateCalculator(
            buf_len=self.ohc_buf_len,
            timer_interval=FETCH_TIMER_INTERVAL,
            fetch_func=fetch_func,
            thresh_percentile=THRESH_PERCENTILE)

    def start_calculate(self):
        self.online_heartrate_calculator.start(QtCore.QThread.NormalPriority)

    def initUI(self, title, color):
        self.title = title
        self.color = color
        self.setWindowTitle(self.title)
        # # プロット初期設定
        self.plt_wid = pg.PlotWidget()
        self.plt_wid.setYRange(-500,1500)
        self.plt_wid.setXRange(0,2000)
        self.raw_curve = self.plt_wid.plot(pen=self.color)
        self.peak_dot = pg.ScatterPlotItem(size=5, pen=pg.mkPen(None), brush=pg.mkBrush(255, 100, 50), symbol='o')
        self.plt_wid.addItem(self.peak_dot)
        ax = self.plt_wid.getAxis('bottom')
        ttick = [(t, t//2) for t in range(0, 2001, 200)]
        ax.setTicks([ttick])
        # text
        self.heart_rate_format = '<p><font size="7" color="#ffffff">Heart rate: {heart_rate} bpm<br>RR interval: {RR_interval} ms</font></p>'
        self.heart_rate_text = pg.TextItem(html=self.heart_rate_format.format(heart_rate='000', RR_interval='00.0'))
        self.heart_rate_text.setPos(0, 1400)
        self.plt_wid.addItem(self.heart_rate_text)
        self.group_name_format = '<p><font size="8" color="{color}">{group_name}&nbsp;</font><font size="8" color="#aaaa50"> Phase: {phase}</font></font><font size="8" color="#ffffff"> &nbsp; {phase_time}</font></p>'
        self.group_name_text = pg.TextItem(html=self.group_name_format.format(color=self.color, group_name=self.title, phase=0, phase_time=self.phase_timestamp))
        self.group_name_text.setPos(0, 1550)
        self.plt_wid.addItem(self.group_name_text)
        self.recording_message_format = '<p><font size="7" color="#ff0000">{text}</font></p>'
        self.recording_message_text = pg.TextItem(html=self.recording_message_format.format(text=''))
        self.recording_message_text.setPos(1600, 1550)
        self.plt_wid.addItem(self.recording_message_text)
        self.recording_timer_format = '<p><font size="8" color="#ffffff">{text}</font></p>'
        self.recording_timer_text = pg.TextItem(html=self.recording_timer_format.format(text='00:00:00'))
        self.recording_timer_text.setPos(1600, 1400)
        self.plt_wid.addItem(self.recording_timer_text)

        # # ボタン
        record_button = QtGui.QPushButton('Record', self)
        record_button.setStyleSheet('background-color: red; color: white')
        record_button.setCheckable(True)
        record_button.clicked[bool].connect(self.button_callback)
        check_button = QtGui.QPushButton('Phase', self)
        check_button.setStyleSheet('background-color: yellow; color: black')
        check_button.clicked[bool].connect(self.button_callback)

        # # layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(record_button)
        vbox.addStretch(2)
        vbox.addWidget(check_button)
        vbox.addStretch(1)
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.plt_wid)
        self.setLayout(hbox)


    @QtCore.pyqtSlot(bool)
    def button_callback(self, pressed):
        source = self.sender()
        if source.text() == 'Record':
            # print('Record')
            self.is_recording = False if self.is_recording else True
            if self.is_recording:
                self.recording_message_text.setHtml(self.recording_message_format.format(text='Recording...'))
                self.recording_start_time = time.perf_counter()
                self.phase_timestamp = '00:00:00'
                self.plot_window_signal.emit('start recording')
            else:
                self.recording_message_text.setHtml(self.recording_message_format.format(text=''))
                self.plot_window_signal.emit('stop recording')
        elif source.text() == 'Phase':
            self.phase += 1
            elapsed_time = time.perf_counter() - self.recording_start_time if self.recording_start_time is not None else 0
            s = int(elapsed_time%60); m = int((elapsed_time/60)%60); h = int((elapsed_time/60)/60)
            self.phase_timestamp = str(h).zfill(2) + ':' + str(m).zfill(2) + ':' + str(s).zfill(2)
            self.group_name_text.setHtml(self.group_name_format.format(color=self.color, group_name=self.title, phase=self.phase, phase_time=self.phase_timestamp))

    def set_thresh_percentile(self, thresh_percentile):
        self.online_heartrate_calculator.set_thresh_percentile(thresh_percentile)

    def set_group_name(self, group_name):
        self.title = group_name
        self.group_name_text.setHtml(self.group_name_format.format(color=self.color, group_name=self.title, phase=self.phase, phase_time=self.phase_timestamp))

    def notch_setting(self, enable=False):
        self.online_heartrate_calculator.notch_setting(enable)

    def update(self):
        # start_time = time.time()
        new_data_len, raw, peak_pos, heart_rate, RR_interval = self.online_heartrate_calculator.flush_data_for_plot()
        # print('Heart rate(bpm) / interval(ms):', round(heart_rate, 1), round(RR_interval,1))
        self.logger.set_data(new_data_len, peak_pos, self.phase)
        if new_data_len > 0:
            if new_data_len > self.ohc_buf_len: new_data_len = self.ohc_buf_len
            if (self.buf_pos + new_data_len) < self.oscillo_buf_len:
                self.raw_buf[self.buf_pos:(self.buf_pos+new_data_len)] = raw[:]
                self.peak_buf[self.buf_pos:(self.buf_pos+new_data_len)] = peak_pos[:]
            else:
                self.raw_buf[self.buf_pos:] = raw[:(self.oscillo_buf_len-self.buf_pos)]
                self.peak_buf[self.buf_pos:] = peak_pos[:(self.oscillo_buf_len-self.buf_pos)]

            self.buf_pos += new_data_len
            if self.buf_pos >= self.oscillo_buf_len: self.buf_pos = 0

            # plot
            self.raw_curve.setData(self.raw_buf)
            t, = np.where((self.peak_buf>0)); y = np.ones(t.shape)*1000
            self.peak_dot.setData(t, y)
            self.heart_rate_text.setHtml(self.heart_rate_format.format(heart_rate=str(round(heart_rate,1)), RR_interval=str(round(RR_interval,1))))

        # recording timer
        if self.is_recording:
            elapsed_time = time.perf_counter() - self.recording_start_time
            s = int(elapsed_time%60); m = int((elapsed_time/60)%60); h = int((elapsed_time/60)/60)
            time_str = str(h).zfill(2) + ':' + str(m).zfill(2) + ':' + str(s).zfill(2)
            self.recording_timer_text.setHtml(self.recording_timer_format.format(text=time_str))

        # elapsed_time = time.time() - start_time
        # print('elapsed time (ms):', round(elapsed_time*1000, 3))
        return 0

    def closeEvent(self, event):
        #メッセージ画面の設定いろいろ
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            print('#Quit', self.title)
            self.timer.stop()
            self.online_heartrate_calculator.quit()
            event.accept()
        else:
            event.ignore()
