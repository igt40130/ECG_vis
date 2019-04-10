#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import argparse
import sys
from PyQt5 import QtCore, QtGui
from lib.config_window import CongfigWindow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', default=False, action='store_true')
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    config_win = CongfigWindow(v_continuous=args.v)
    config_win.show()
    sys.exit(app.exec_())




if __name__ == '__main__':
    main()
