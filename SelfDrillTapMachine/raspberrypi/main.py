import sys
import time
import asyncio
import logging
import functools
import numpy as np
from asyncua import ua
from pathlib import Path
from datetime import datetime
from _uaclient import UaClient
from asyncua.sync import SyncNode
################
################
################
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.camera import Camera
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
        for k in logging.root.manager.loggerDict:
            if 'asyncua' in k:
                logger = logging.getLogger(k)
                logger.setLevel(level=logging.CRITICAL)
        Window.bind(on_request_close=self._close)
        Window.size = (320*2, 160*4)
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
        #self.camera = Camera(resolution=(640, 480))
        #self.camera.play = True
        #self.add_widget(self.camera)
        #
        self.ui_button_file_download = Button(text='File download', font_size=32)
        self.ui_button_file_download.bind(on_press=self.button_file_download)
        self.add_widget(self.ui_button_file_download)
        #
        self._address = 'opc.tcp://192.168.2.3:4840'
        d_names = [
            'M.hmi.plc_ready',
            'M.hmi.hmi_ready',
            'M.hmi.run',
            'M.hmi.stop',
            'M.hmi.view_axis_mNm[0]',
            'M.hmi.view_axis_micro[0]',
            'F.fdb.name',
            'F.fdb.ready',
            'F.fdb.begin',
            'F.fdb.end',
            'F.fdb.line',
            'F.fdb.line_done',
            'C.file_name',
            ]
        self._d_ids = [('ns=4;s=|var|LS.Application.' + n) for n in d_names]
        self._d_name__id = dict(zip(d_names, self._d_ids))
    
    def _close(self, *kvargs):
        self.disconnect('close')
        if hasattr(self, 'camera'):
            self.camera.play = False
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
    
    def _d_get(self, _dt_):
        if not self._d_get_done:
            return
        self._d_get_done = False
        id__node = self.uac.get_id__node(self._d_ids)
        node__value = self.uac.get_node__value(id__node.values())
        for k, v in node__value.items():
            self._d_check(k, v)
        self._d_id__node = id__node
        self._d_node__value = node__value
        self._d_get_done = True
    
    def _d_check(self, _node_, _value_):
        if _node_ in self._d_node__value:
            value_last = self._d_node__value[_node_]
            if _value_ != value_last:
                if _node_ not in self._d_node__change:
                    self._d_node__change[_node_] = 1
                else:
                    self._d_node__change[_node_] += 1
    
    def _d_show(self, _dt_):
        s = ''
        for d_name, d_id in self._d_name__id.items():
            if d_id not in self._d_id__node:
                break
            d_node = self._d_id__node[d_id]
            d_value = self._d_node__value[d_node]
            if d_node in self._d_node__change:
                s += '%s : %s -> %s\n' % (d_name, d_value, self._d_node__change[d_node])
        self.ui_data.text = s
        #
        self.ui_graph_line_pindex = (self.ui_graph_line_pindex + 1) % self.ui_graph_sample
        d_id = self._d_name__id['M.hmi.view_axis_mNm[0]']
        d_node = self._d_id__node[d_id]
        d_value = self._d_node__value[d_node]
        self.ui_graph_line.points[self.ui_graph_line_pindex] = (self.ui_graph_line_pindex, d_value * 0.001)
    
    def connect(self, _instance_):
        self._d_id__node = set(self._d_ids)
        self._d_node__value = {}
        self._d_node__change = {}
        self._d_get_done = True
        self._connect(self._address)
        _d_get = Clock.schedule_interval(self._d_get, 0.010)
        _d_show = Clock.schedule_interval(self._d_show, 0.050)
        self._clock_connect = [_d_get, _d_show]
    
    def disconnect(self, _instance_):
        for clock in self._clock_connect:
            Clock.unschedule(clock)
        if hasattr(self, '_clock_file_download'):
            Clock.unschedule(self._clock_file_download)
            delattr(self, '_clock_file_download')
        self._disconnect()
    
    #####
    def button_machine_run(self, _value_, _instance_):
        if not self.uac.connected():
            return
        d_id = self._d_name__id['M.hmi.run']
        self.uac.set_node_data(d_id, _value_)
    
    def button_machine_stop(self, _value_, _instance_):
        if not self.uac.connected():
            return
        d_id = self._d_name__id['M.hmi.stop']
        self.uac.set_node_data(d_id, _value_)

    def button_file_download(self, _instance_):
        if not self.uac.connected():
            return
        if hasattr(self, '_clock_file_download_name') or hasattr(self, '_clock_file_download'):
            print('File downloading')
            return
        self.file_name = 'profile_a'
        file_path = Path(Path.cwd(), 'cnc', '%s.cnc' % (self.file_name))
        if not file_path.is_file():
            print('File does not exist: %s' % (file_path))
            return
        self.file = []
        with file_path.open(mode='r') as file:
            for line in file:
                self.file.append(line.strip())
        d_id = self._d_name__id['F.fdb.ready']
        d_node = self._d_id__node[d_id]
        d_value = self._d_node__value[d_node]
        if d_value:
            self.file_li = 0
            d_id = self._d_name__id['F.fdb.name']
            d_node = self._d_id__node[d_id]
            d_node.set_value(ua.Variant(self.file_name, ua.VariantType.String))
            self._clock_file_download_name = Clock.schedule_interval(self._file_download_name, 0.010)
    
    def _file_download_name(self, _dt_):
        d_id = self._d_name__id['F.fdb.name']
        d_node = self._d_id__node[d_id]
        d_value = self._d_node__value[d_node]
        if d_value == self.file_name:
            Clock.unschedule(self._clock_file_download_name)
            delattr(self, '_clock_file_download_name')
            d_id = self._d_name__id['F.fdb.begin']
            self.uac.set_node_data(d_id, True)
            self._clock_file_download = Clock.schedule_interval(self._file_download, 0.010)
    
    def _file_download(self, _dt_):
        d_id = self._d_name__id['F.fdb.line_done']
        d_node = self._d_id__node[d_id]
        d_value = self._d_node__value[d_node]
        if d_value:
            if self.file_li >= len(self.file):
                d_id = self._d_name__id['F.fdb.end']
                self.uac.set_node_data(d_id, True)
                Clock.unschedule(self._clock_file_download)
                delattr(self, '_clock_file_download')
            else:
                d_id = self._d_name__id['F.fdb.line_done']
                self.uac.set_node_data(d_id, False)
                d_id = self._d_name__id['F.fdb.line']
                d_node = self._d_id__node[d_id]
                d_node.set_value(ua.Variant(self.file[self.file_li], ua.VariantType.String))
                self.file_li += 1

class MainWindow(App):
    def on_stop(self):
        return
    def build(self):
        return Main()

if __name__ == '__main__':
    MainWindow().run()