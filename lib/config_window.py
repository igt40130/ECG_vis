# -*- coding:utf-8 -*-
import numpy as np
from PyQt5 import QtCore, QtGui
import pyqtgraph as pg
from .parameters import *
from .data_aquisition import rContinuous
from .virtual_data_aquisition import vContinuous
from .plot_window import PlotWindow


SETTING = 'Settings (should be configured in Central\'s Hardware Configuration):\n' \
          + '0. ch1 : LNC ref\n' \
          + '1. ch3 : ECG0 signal, LNC adopted\n' \
          + '2. ch4 : ECG1 signal, LNC adopted\n' \
          + '3. ch5 : ECG0 ref, LNC adopted\n' \
          + '4. ch6 : ECG1 ref, LNC adopted\n' \
          + '5. ch27: ECG2 signal, LNC adopted\n' \
          + '6. ch28: ECG3 signal, LNC adopted\n' \
          + '7. ch29: ECG2 ref, LNC adopted\n' \
          + '8. ch30: ECG3 ref, LNC adopted\n'


class CongfigWindow(QtGui.QWidget):
    def __init__(self, v_continuous=False):
        super(CongfigWindow, self).__init__()
        self.is_v_continuous = v_continuous
        self.initUI()
        self.init_plot_windows()

    def cb_callback(self, state):
        source = self.sender()
        if source is self.ecg0_subref_cb:
            self.continuous.ecg0_subref_setting(subref=(state==QtCore.Qt.Checked))
        elif source is self.ecg0_invert_cb:
            self.continuous.ecg0_invert_setting(invert=(state==QtCore.Qt.Checked))
        elif source is self.ecg1_subref_cb:
            self.continuous.ecg1_subref_setting(subref=(state==QtCore.Qt.Checked))
        elif source is self.ecg1_invert_cb:
            self.continuous.ecg1_invert_setting(invert=(state==QtCore.Qt.Checked))
        elif source is self.ecg2_subref_cb:
            self.continuous.ecg2_subref_setting(subref=(state==QtCore.Qt.Checked))
        elif source is self.ecg2_invert_cb:
            self.continuous.ecg2_invert_setting(invert=(state==QtCore.Qt.Checked))
        elif source is self.ecg3_subref_cb:
            self.continuous.ecg3_subref_setting(subref=(state==QtCore.Qt.Checked))
        elif source is self.ecg3_invert_cb:
            self.continuous.ecg3_invert_setting(invert=(state==QtCore.Qt.Checked))
        elif source is self.ecg0_notch_cb:
            self.ecg0_win.notch_setting(enable=(state==QtCore.Qt.Checked))
        elif source is self.ecg1_notch_cb:
            self.ecg1_win.notch_setting(enable=(state==QtCore.Qt.Checked))
        elif source is self.ecg2_notch_cb:
            self.ecg2_win.notch_setting(enable=(state==QtCore.Qt.Checked))
        elif source is self.ecg3_notch_cb:
            self.ecg3_win.notch_setting(enable=(state==QtCore.Qt.Checked))

    @QtCore.pyqtSlot()
    def le_callback(self):
        source = self.sender()
        if source is self.ecg0_gname_le:
            source.setText(self.ecg0_gname)
            # TODO: enable to rename
        elif source is self.ecg0_thresh_le:
            try:
                val = float(self.ecg0_thresh_le.text())
            except ValueError:
                pass
            if val < 99.9 and val > 0.1:
                self.ecg0_thresh = val
                self.ecg0_win.set_thresh_percentile(self.ecg0_thresh)
            self.ecg0_thresh_le.setText(str(self.ecg0_thresh))
        elif source is self.ecg1_gname_le:
            source.setText(self.ecg1_gname)
        elif source is self.ecg1_thresh_le:
            try:
                val = float(self.ecg1_thresh_le.text())
            except ValueError:
                pass
            if val < 99.9 and val > 0.1:
                self.ecg1_thresh = val
                self.ecg1_win.set_thresh_percentile(self.ecg1_thresh)
            self.ecg1_thresh_le.setText(str(self.ecg1_thresh))
        elif source is self.ecg2_gname_le:
            source.setText(self.ecg2_gname)
        elif source is self.ecg2_thresh_le:
            try:
                val = float(self.ecg2_thresh_le.text())
            except ValueError:
                pass
            if val < 99.9 and val > 0.1:
                self.ecg2_thresh = val
                self.ecg2_win.set_thresh_percentile(self.ecg2_thresh)
            self.ecg2_thresh_le.setText(str(self.ecg2_thresh))
        elif source is self.ecg3_gname_le:
            source.setText(self.ecg3_gname)
        elif source is self.ecg3_thresh_le:
            try:
                val = float(self.ecg3_thresh_le.text())
            except ValueError:
                pass
            if val < 99.9 and val > 0.1:
                self.ecg3_thresh = val
                self.ecg3_win.set_thresh_percentile(self.ecg3_thresh)
            self.ecg3_thresh_le.setText(str(self.ecg3_thresh))

    def init_plot_windows(self):
        if self.is_v_continuous:
            self.continuous = vContinuous()
        else:
            self.continuous = rContinuous(timer_interval=CBPY_TIMER_INTERVAL)
        self.ecg0_win = PlotWindow(self.ecg0_gname, fetch_func=self.continuous.ecg0_get_func, color='#00ffff')
        self.ecg1_win = PlotWindow(self.ecg1_gname, fetch_func=self.continuous.ecg1_get_func, color='#ff00ff')
        self.ecg2_win = PlotWindow(self.ecg2_gname, fetch_func=self.continuous.ecg2_get_func, color='#88ff88')
        self.ecg3_win = PlotWindow(self.ecg3_gname, fetch_func=self.continuous.ecg3_get_func, color='#ffff00')

    def start_plot(self):
        self.continuous.start(QtCore.QThread.HighestPriority)
        self.ecg0_win.start_calculate()
        self.ecg0_win.show()
        self.ecg1_win.show()
        self.ecg1_win.start_calculate()
        self.ecg2_win.show()
        self.ecg2_win.start_calculate()
        self.ecg3_win.show()
        self.ecg3_win.start_calculate()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', \
                                           "Are you sure to close all windows ?", \
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            del self.ecg0_win
            del self.ecg1_win
            del self.ecg2_win
            del self.ecg3_win
            pg.exit()
            event.accept()
        else:
            event.ignore()

    def initUI(self):
        self.setWindowTitle('Configuration')
        self.start_button = QtGui.QPushButton('Start', self)
        self.start_button.clicked[bool].connect(self.start_plot)

        global SETTING
        self.setting_label = QtGui.QLabel(SETTING, self)
        self.setting_label.setGeometry(20, 20, 500, 200)

        self.ecg0_gname = 'Group1'
        self.ecg0_thresh = THRESH_PERCENTILE
        self.ecg0_gname_le = QtGui.QLineEdit(self)
        self.ecg0_gname_le.setText(self.ecg0_gname)
        self.ecg0_gname_le.returnPressed.connect(self.le_callback)
        self.ecg0_thresh_le = QtGui.QLineEdit(self)
        self.ecg0_thresh_le.setText(str(self.ecg0_thresh))
        self.ecg0_thresh_le.returnPressed.connect(self.le_callback)
        self.ecg0_flo = QtGui.QFormLayout()
        self.ecg0_flo.addRow('ECG0:', self.ecg0_gname_le)
        self.ecg0_flo.addRow('Thresh(0.1-99.9):', self.ecg0_thresh_le)
        self.ecg0_subref_cb = QtGui.QCheckBox('ref', self)
        self.ecg0_invert_cb = QtGui.QCheckBox('invert', self)
        self.ecg0_subref_cb.stateChanged.connect(self.cb_callback)
        self.ecg0_invert_cb.stateChanged.connect(self.cb_callback)
        self.ecg0_flo.addRow(self.ecg0_subref_cb, self.ecg0_invert_cb)
        self.ecg0_notch_cb = QtGui.QCheckBox('notch', self)
        self.ecg0_notch_cb.stateChanged.connect(self.cb_callback)
        self.ecg0_flo.addRow('', self.ecg0_notch_cb)

        self.ecg1_gname = 'Group2'
        self.ecg1_thresh = THRESH_PERCENTILE
        self.ecg1_gname_le = QtGui.QLineEdit(self)
        self.ecg1_gname_le.setText(self.ecg1_gname)
        self.ecg1_gname_le.returnPressed.connect(self.le_callback)
        self.ecg1_thresh_le = QtGui.QLineEdit(self)
        self.ecg1_thresh_le.setText(str(self.ecg1_thresh))
        self.ecg1_thresh_le.returnPressed.connect(self.le_callback)
        self.ecg1_flo = QtGui.QFormLayout()
        self.ecg1_flo.addRow('ECG1:', self.ecg1_gname_le)
        self.ecg1_flo.addRow('Thresh(0.1-99.9):', self.ecg1_thresh_le)
        self.ecg1_subref_cb = QtGui.QCheckBox('ref', self)
        self.ecg1_invert_cb = QtGui.QCheckBox('invert', self)
        self.ecg1_subref_cb.stateChanged.connect(self.cb_callback)
        self.ecg1_invert_cb.stateChanged.connect(self.cb_callback)
        self.ecg1_flo.addRow(self.ecg1_subref_cb, self.ecg1_invert_cb)
        self.ecg1_notch_cb = QtGui.QCheckBox('notch', self)
        self.ecg1_notch_cb.stateChanged.connect(self.cb_callback)
        self.ecg1_flo.addRow('', self.ecg1_notch_cb)

        self.ecg2_gname = 'Group3'
        self.ecg2_thresh = THRESH_PERCENTILE
        self.ecg2_gname_le = QtGui.QLineEdit(self)
        self.ecg2_gname_le.setText(self.ecg2_gname)
        self.ecg2_gname_le.returnPressed.connect(self.le_callback)
        self.ecg2_thresh_le = QtGui.QLineEdit(self)
        self.ecg2_thresh_le.setText(str(self.ecg2_thresh))
        self.ecg2_thresh_le.returnPressed.connect(self.le_callback)
        self.ecg2_flo = QtGui.QFormLayout()
        self.ecg2_flo.addRow('ECG2:', self.ecg2_gname_le)
        self.ecg2_flo.addRow('Thresh(0.1-99.9):', self.ecg2_thresh_le)
        self.ecg2_subref_cb = QtGui.QCheckBox('ref', self)
        self.ecg2_invert_cb = QtGui.QCheckBox('invert', self)
        self.ecg2_subref_cb.stateChanged.connect(self.cb_callback)
        self.ecg2_invert_cb.stateChanged.connect(self.cb_callback)
        self.ecg2_flo.addRow(self.ecg2_subref_cb, self.ecg2_invert_cb)
        self.ecg2_notch_cb = QtGui.QCheckBox('notch', self)
        self.ecg2_notch_cb.stateChanged.connect(self.cb_callback)
        self.ecg2_flo.addRow('', self.ecg2_notch_cb)

        self.ecg3_gname = 'Group4'
        self.ecg3_thresh = THRESH_PERCENTILE
        self.ecg3_gname_le = QtGui.QLineEdit(self)
        self.ecg3_gname_le.setText(self.ecg3_gname)
        self.ecg3_gname_le.returnPressed.connect(self.le_callback)
        self.ecg3_thresh_le = QtGui.QLineEdit(self)
        self.ecg3_thresh_le.setText(str(self.ecg3_thresh))
        self.ecg3_thresh_le.returnPressed.connect(self.le_callback)
        self.ecg3_flo = QtGui.QFormLayout()
        self.ecg3_flo.addRow('ECG3:', self.ecg3_gname_le)
        self.ecg3_flo.addRow('Thresh(0.1-99.9):', self.ecg3_thresh_le)
        self.ecg3_subref_cb = QtGui.QCheckBox('ref', self)
        self.ecg3_invert_cb = QtGui.QCheckBox('invert', self)
        self.ecg3_subref_cb.stateChanged.connect(self.cb_callback)
        self.ecg3_invert_cb.stateChanged.connect(self.cb_callback)
        self.ecg3_flo.addRow(self.ecg3_subref_cb, self.ecg3_invert_cb)
        self.ecg3_notch_cb = QtGui.QCheckBox('notch', self)
        self.ecg3_notch_cb.stateChanged.connect(self.cb_callback)
        self.ecg3_flo.addRow('', self.ecg3_notch_cb)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.ecg0_flo)
        vbox.addStretch()
        vbox.addLayout(self.ecg1_flo)
        vbox.addStretch()
        vbox.addLayout(self.ecg2_flo)
        vbox.addStretch()
        vbox.addLayout(self.ecg3_flo)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.setting_label)
        vbox2.addWidget(self.start_button)
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(vbox2)
        hbox.addStretch()
        hbox.addLayout(vbox)
        self.setLayout(hbox)
