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
from _uaclient import UaClient
from _data import Data
from _download import Download
################
################
################
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy_garden.graph import Graph, LinePlot

class Main(GridLayout):
    def __init__(self, **kvargs):
        super(Main, self).__init__(**kvargs)
        self.uac = UaClient()
        self.data = Data(self.uac)
        self.download = Download(self.uac, self.data)
        for k in logging.root.manager.loggerDict:
            if 'asyncua' in k:
                logger = logging.getLogger(k)
                logger.setLevel(level=logging.CRITICAL)
        Window.bind(on_request_close=self._close)
        Window.size = (1280, 720)
        self.cols = 2
        #
        self.ui_connect = Button(text='Connect', font_size=32)
        self.ui_connect.bind(on_press=self.connect)
        self.add_widget(self.ui_connect)
        #
        self.ui_disconnect = Button(text='Disconnect', font_size=32)
        self.ui_disconnect.bind(on_press=self.disconnect)
        self.add_widget(self.ui_disconnect)
        #
        self.add_widget(Label(text='Data'))
        self.ui_data = Label()
        self.add_widget(self.ui_data)
        #
        self.ui_button_machine_run = Button(text='Run', font_size=32)
        self.ui_button_machine_run.bind(on_press=functools.partial(self.button_machine_run, True))
        self.ui_button_machine_run.bind(on_release=functools.partial(self.button_machine_run, False))
        self.add_widget(self.ui_button_machine_run)
        #
        self.ui_button_machine_stop = Button(text='Stop', font_size=32)
        self.ui_button_machine_stop.bind(on_press=functools.partial(self.button_machine_stop, True))
        self.ui_button_machine_stop.bind(on_release=functools.partial(self.button_machine_stop, False))
        self.add_widget(self.ui_button_machine_stop)
        #
        self.ui_graph_sample = 100
        self.ui_graph = Graph(y_ticks_major=1.0,
                           x_ticks_major=0,
                           border_color=[0, 1, 1, 1],
                           tick_color=[0, 1, 1, 0.7],
                           x_grid=True, y_grid=True,
                           xmin=0, xmax=self.ui_graph_sample,
                           ymin=-1.0, ymax=1.0,
                           draw_border=False,
                           x_grid_label=False, y_grid_label=True)
        self.add_widget(self.ui_graph)
        self.ui_graph_line = LinePlot(color=[1, 1, 0, 1], line_width=1.0)
        self.ui_graph_line.points = [(x, 0) for x in range(self.ui_graph_sample)]
        self.ui_graph_line_pindex = 0
        self.ui_graph.add_plot(self.ui_graph_line)
        #
        self.ui_button_file_download = Button(text='File download', font_size=32)
        self.ui_button_file_download.bind(on_press=self.button_file_download)
        self.add_widget(self.ui_button_file_download)
        #
        names = [
            'M.hmi.run',
            'M.hmi.stop',
            'F.fst.index',
            'F.fst.ready',
            'F.fst.begin',
            'F.fst.end',
            'F.fst.line',
            'F.fst.line_done',
            ]
        for i in range(13):
            names.append('M.hmi.view_axis_mNm[%d]' % (i))
            names.append('M.hmi.view_axis_micro[%d]' % (i))
        self.data.set('ns=4;s=|var|LS.Application.', names)
    
    def _close(self, *kvargs):
        self.disconnect('close')
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
        s = ''
        for nm in self.data.nms:
            if nm not in self.data.nm__id:
                break
            no = self.data.node(nm)
            vl = self.data.value(nm)
            if no in self.data.no__change:
                s += '%s : %s -> %s\n' % (nm, vl, self.data.change(nm))
        self.ui_data.text = s
        #
        self.ui_graph_line_pindex = (self.ui_graph_line_pindex + 1) % self.ui_graph_sample
        value = self.data.value('M.hmi.view_axis_mNm[0]')
        self.ui_graph_line.points[self.ui_graph_line_pindex] = (self.ui_graph_line_pindex, value * 0.001)
    
    def connect(self, _instance_):
        self._connect(self.data.address)
        self.data.start(0.010)
        data_show = Clock.schedule_interval(self._data_show, 0.050)
        self._connect_clock = [data_show]
    
    def disconnect(self, _instance_):
        if hasattr(self, '_connect_clock'):
            for clock in self._connect_clock:
                Clock.unschedule(clock)
        self.data.stop()
        self.download.stop()
        self._disconnect()
    
    #####
    def button_machine_run(self, _value_, _instance_):
        if self.uac.is_connected():
            self.data.node('M.hmi.run').write_value(_value_)
    
    def button_machine_stop(self, _value_, _instance_):
        if self.uac.is_connected():
            self.data.node('M.hmi.stop').write_value(_value_)

    def button_file_download(self, _instance_):
        if self.uac.is_connected():
            self.download.start(0)

class MainWindow(App):
    def on_stop(self):
        return
    def build(self):
        return Main()

if __name__ == '__main__':
    MainWindow().run()