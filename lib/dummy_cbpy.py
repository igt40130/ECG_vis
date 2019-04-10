# -*- coding:utf-8 -*-

class DummyCbpy(object):
    def __init__(self):
        pass

    def open(*args, **kwargs):
        return 1, '# Dummy connection'

    def trial_config(*args, **kwargs):
        return 1, 1

    def trial_continuous(*args, **kwargs):
        return 1, []

