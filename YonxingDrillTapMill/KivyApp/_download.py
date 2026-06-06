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
        self.file_content = []
        with file_path.open(mode='r') as file:
            for line in file:
                self.file_content.append(line.strip())
        if self.data.get('fst.ready') == True:
            self.file_line_index = 0
            self.data.set('fst.index', self.file_index)
            self._download_index_clock = Clock.schedule_interval(self._download_index, 0.010)
    
    def _download_index(self, _dt_):
        if self.data.get('fst.index') == self.file_index:
            Clock.unschedule(self._download_index_clock)
            delattr(self, '_download_index_clock')
            self.data.set('fst.begin', True)
            self._download_line_clock = Clock.schedule_interval(self._download_line, 0.010)
    
    def _download_line(self, _dt_):
        if self.data.get('fst.line_done') == True:
            if self.file_line_index >= len(self.file_content):
                self.data.set('fst.end', True)
                Clock.unschedule(self._download_line_clock)
                delattr(self, '_download_line_clock')
            else:
                self.data.set('fst.line_done', False)
                self.data.set('fst.line', self.file_content[self.file_line_index])
                self.file_line_index += 1
    
    def stop(self):
        if hasattr(self, '_download_index_clock'):
            Clock.unschedule(self._download_index_clock)
            delattr(self, '_download_index_clock')
        if hasattr(self, '_download_line_clock'):
            Clock.unschedule(self._download_line_clock)
            delattr(self, '_download_line_clock')