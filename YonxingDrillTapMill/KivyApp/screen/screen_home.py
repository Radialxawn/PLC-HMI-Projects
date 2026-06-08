import sys
import time
import asyncio
import logging
import functools
import numpy as np
from asyncua import ua
from pathlib import Path
from datetime import datetime
from asyncua.sync import SyncNode
from _ui import UI
from _data import Data
from _uaclient import UaClient
from _download import Download
################
################
################
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
import kivy.utils

class ScreenHome(Screen):
    def __init__(self, **kvargs):
        super(ScreenHome, self).__init__(**kvargs)
        self._log_mode()
        Window.bind(on_request_close=self._close)
        #
        self.ui = UI(self)
        self.uac = UaClient()
        self.data = Data(self.uac, 'opc.tcp://192.168.2.3:4840')
        self.download = Download(self.uac, self.data)
        #
        self.data.create(r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml', 'ns=4;s=|var|LS')
        self.ui.create()
    
    def _log_mode(self):
        for k in logging.root.manager.loggerDict:
            if 'asyncua' in k:
                logger = logging.getLogger(k)
                logger.setLevel(level=logging.CRITICAL)
    
    def _close(self, *kvargs):
        self.button_disconnect('close')
        App.get_running_app().stop()
        Window.close()
    
    def _connect(self, _uri_):
        uri = _uri_.strip()
        try:
            self.uac.connect(uri)
        except Exception as ex:
            print(ex)
            raise
    
    def _disconnect(self):
        try:
            self.uac.disconnect()
        except Exception as ex:
            print(ex)
            raise
    
    def _data_show(self, _dt_):
        for name in self.ui.name__button:
            if name in self.data.name__block:
                block = self.data.name__block[name]
                btn = self.ui.name__button[name]
                btn.color = kivy.utils.get_color_from_hex("#b9f542") if block.value == True else ("#414946")
        for i in range(6):
            block = self.data.name__block['hmi.face_index']
            btn = self.ui.button_face_indexs[i]
            btn.color = kivy.utils.get_color_from_hex("#b9f542") if block.value == i else ("#414946")
        text = ''
        for i in range(13):
            block = self.data.name__block[f'hmi.cf.gear_num[{i}]']
            text += f'{block.value}, '
        text = text[:-2] + '\n'
        for i in range(13):
            block = self.data.name__block[f'hmi.cf.gear_dir[{i}]']
            text += f'{block.value}, '
        text = text[:-2] + '\n'
        self.ui.data.text = text
    
    def button_connect(self, _instance_):
        self._connect(self.data.address)
        self.data.start(0.010, 32)
        data_show = Clock.schedule_interval(self._data_show, 0.050)
        self._connect_clock = [data_show]
    
    def button_disconnect(self, _instance_):
        if hasattr(self, '_connect_clock'):
            for clock in self._connect_clock:
                Clock.unschedule(clock)
        self.data.stop()
        self.download.stop()
        self._disconnect()
    
    def button_machine_run(self, _value_, _instance_):
        if self.uac.is_connected():
            self.data.set('hmi.run', _value_)
    
    def button_machine_stop(self, _value_, _instance_):
        if self.uac.is_connected():
            self.data.set('hmi.stop', _value_)
    
    def button_machine_home(self, _value_, _instance_):
        if self.uac.is_connected():
            self.data.set('hmi.home', _value_)
    
    def button_machine_face(self, _value_, _instance_):
        if self.uac.is_connected():
            self.data.set('hmi.face_index', _value_)

    def button_download(self, _instance_):
        if self.uac.is_connected():
            self.download.start(0)