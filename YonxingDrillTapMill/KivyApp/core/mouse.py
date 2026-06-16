class Mouse(object):
    def __init__(self):
        self.down_time_sec = 0
        self.drag = False
        self.drag_begin = [0, 0]
        self.drag_offset = [0, 0]
        self.selected_object = None
        self.selected_object_pos = [0, 0]