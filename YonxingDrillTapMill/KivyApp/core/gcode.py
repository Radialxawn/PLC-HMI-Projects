import re
from pathlib import Path
from kivy.core.image import Image as CoreImage

class GCode(object):
    pattern = re.compile(r'(?<=[^\s])(?=[A-Z])', re.IGNORECASE)

    def __init__(self):
        self._path = None
        self.lines = []
        self.combine = ''

    @staticmethod
    def _clean(line: str) -> str:
        line = re.sub(r'\(.*?\)', '', line)
        line = line.split(';')[0]
        return re.sub(r'\s+', '', line)

    def read(self, _path_):
        self._path = _path_
        with _path_.open(mode='r') as file:
            for line in file:
                l = re.sub(GCode.pattern, ' ', GCode._clean(line))
                if len(l) > 0:
                    self.lines.append(l)
        imax = len(self.lines) - 1
        for i, line in enumerate(self.lines):
            self.combine += f'N%d %s%s' % (i, line, '\r\n' if i < imax else '')
        return self

    def chunks(self, _chunk_size_):
        chunks = []
        for i in range(0, len(self.combine), _chunk_size_):
            chunk = self.combine[i : i + _chunk_size_]
            chunks.append(chunk)
        return chunks

    def image_remove(self):
        path = self._path.with_suffix('.png')
        path.unlink(missing_ok=True)

    def image_generate(self):
        print('generate image', self._path)

    @staticmethod
    def image_get(_path_: Path):
        path = _path_.with_suffix('.png')
        if not path.exists():
            return None
        return CoreImage(path)