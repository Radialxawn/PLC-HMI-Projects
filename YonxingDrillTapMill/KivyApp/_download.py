from asyncua import ua
from pathlib import Path
from kivy.clock import Clock

class Download(object):
    def __init__(self, _uac_, _data_):
        self.uac = _uac_
        self.data = _data_

    def start(self, _index_):
        if hasattr(self, '_download_index_clock') or hasattr(self, '_download_line_clock'):
            print('File downloading')
            return
        self.file_index = _index_
        file_path = Path(Path.cwd(), 'cnc', 'custom_%d.cnc' % (self.file_index))
        if not file_path.is_file():
            print('File does not exist: %s' % (file_path))
            return
        self.file = []
        with file_path.open(mode='r') as file:
            for line in file:
                self.file.append(line.strip())
        if self.data.value('F.fst.ready') == True:
            self.file_li = 0
            self.data.node('F.fst.index').set_value(ua.Variant(self.file_index, ua.VariantType.Int16))
            self._download_index_clock = Clock.schedule_interval(self._download_index, 0.010)
    
    def _download_index(self, _dt_):
        if self.data.value('F.fst.index') == self.file_index:
            Clock.unschedule(self._download_index_clock)
            delattr(self, '_download_index_clock')
            d_id = self._d_name__id['F.fst.begin']
            self.uac.set_node_data(d_id, True)
            self._download_line_clock = Clock.schedule_interval(self._download_line, 0.010)
    
    def _download_line(self, _dt_):
        d_id = self._d_name__id['F.fst.line_done']
        d_node = self._d_id__node[d_id]
        d_value = self._d_node__value[d_node]
        if d_value:
            if self.file_li >= len(self.file):
                d_id = self._d_name__id['F.fst.end']
                self.uac.set_node_data(d_id, True)
                Clock.unschedule(self._download_line_clock)
                delattr(self, '_download_line_clock')
            else:
                d_id = self._d_name__id['F.fst.line_done']
                self.uac.set_node_data(d_id, False)
                d_id = self._d_name__id['F.fst.line']
                d_node = self._d_id__node[d_id]
                d_node.set_value(ua.Variant(self.file[self.file_li], ua.VariantType.String))
                self.file_li += 1
    
    def stop(self):
        if hasattr(self, '_download_index_clock'):
            Clock.unschedule(self._download_index_clock)
            delattr(self, '_download_index_clock')
        if hasattr(self, '_download_line_clock'):
            Clock.unschedule(self._download_line_clock)
            delattr(self, '_download_line_clock')