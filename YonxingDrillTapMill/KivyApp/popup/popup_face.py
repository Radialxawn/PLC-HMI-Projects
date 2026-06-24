from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from popup.popup_shape import PopupShape
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from core.mouse import Mouse
from core.draw import Draw
from data.face import Face
from core.ui import UITextInputInteger
from kivy.utils import get_color_from_hex as clhex

class PopupFace(Popup):
    def set_data(self, _face_, _rule_, _apply_, _delete_):
        _face_.limit()
        self._face_ = _face_
        self._face_edit = _face_.clone()
        self._rule_ = _rule_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(1e-3, [0.5e-3, 10e-3])
        self._mouse = Mouse()
        self._property__input, self._name__input_view, self._name__value = self._generate()
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)
        return self

    def _generate(self):
        property__input, name__input_view, name__value = {}, {}, {}
        self.ids.face_property.add_widget(Widget())
        self.ids.face_property.width = 380
        for property in Face.property__data:
            data = Face.property__data[property]
            box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=35,
            )
            label = Label(
                text=data['label'],
                size_hint_x=None,
                halign='left',
                valign='center',
                width=180
            )
            label.bind(size=label.setter('text_size'))
            box.add_widget(label)
            input = UITextInputInteger(
                halign='center',
                multiline=False
            ).data_set(
                _key_=property,
                _factor_=data['factor'],
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            input.v_value_set(self._face_edit[property])
            input.disabled = property in self._rule_['property_exclude']
            property__input[property] = input
            box.add_widget(input)
            if 'name_view' in data and not input.disabled:
                input_view = UITextInputInteger(
                    halign='center',
                    multiline=False
                ).data_set(
                    _key_=data['name_view'].format(self._face_edit.index_get()),
                    _factor_=data['factor'],
                    _validate_=None,
                    _focus_=None
                )
                input_view.disabled = True
                box.add_widget(input_view)
                name__input_view[input_view.v_key] = input_view
                name__value[input_view.v_key] = None
                input.v_name_view = input_view.v_key
            self.ids.face_property.add_widget(box)
        self.ids.face_property.add_widget(Widget())
        for i in range(len(self._face_edit.z)):
            box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                spacing=5,
                height=35,
            )
            zlabel = Label(
                text=f'Z{i+1}',
                size_hint_x=None,
                width=30
            )
            zslabel = Label(
                text=f'BƯỚC',
                size_hint_x=None,
                width=60
            )
            zinput = UITextInputInteger(
                halign='center',
                multiline=False
            ).data_set(
                _key_=f'z[{i}]',
                _factor_=1e-3,
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            zinput.v_value_set(self._face_edit.z[i])
            zsinput = UITextInputInteger(
                halign='center',
                multiline=False
            ).data_set(
                _key_=f'zs[{i}]',
                _factor_=1e-3,
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            zsinput.v_value_set(self._face_edit.zs[i])
            box.add_widget(zlabel)
            box.add_widget(zinput)
            box.add_widget(zslabel)
            box.add_widget(zsinput)
            self.ids.face_property.add_widget(box)
        self.ids.face_property.add_widget(Widget())
        return property__input, name__input_view, name__value

    def on_open(self, *args):
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.1)

    def on_dismiss(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _face_to_org(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.face_to_org', _value_)
    
    def _face_run(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.face_run', _value_)
    
    def _face_org_set(self):
        app = App.get_running_app()
        for property in ['ox', 'oy', 'oz', 'tool_offset']:
            input = self._property__input[property]
            if hasattr(input, 'v_name_view') and not input.disabled:
                input_view = self._name__input_view[input.v_name_view]
                value = app.data.get(input_view.v_key)
                if value != None:
                    input.v_value_set(value)
                    self._on_text_input_validate(input, input.v_value_get())

    def _value_update(self, _dt_):
        app = App.get_running_app()
        for name in self._name__input_view:
            input_view = self._name__input_view[name]
            block = app.data.block(name)
            value = self._name__value[name]
            if value == block.value:
                continue
            self._name__value[name] = block.value
            input_view.v_value_set(block.value)
        view_can_run = app.data.get('hmi.view_can_run')
        self.ids.face_run.disabled = not view_can_run
        self.ids.face_to_org.disabled = not view_can_run

    def _on_text_input_validate(self, _instance_, _value_):
        changed = False
        array = _instance_.v_key.split('[')
        if len(array) > 1:
            self._face_edit[array[0]][int(array[1][:-1])] = _value_
            changed = True
        elif _value_ != self._face_edit[_instance_.v_key]:
            self._face_edit[_instance_.v_key] = _value_
            changed = True
        if changed:
            self._update_canvas()    

    def _update_canvas(self, *args):
        self._face_draw()

    def _apply(self):
        self._face_edit.limit()
        self._face_.copy(self._face_edit)
        self._apply_()
        self.dismiss()
    
    def _delete(self):
        self._delete_()
        self.dismiss()

    def _cancel(self):
        self.dismiss()
    
    ##############
    # SHAPE EDIT #
    ##############

    def on_touch_down(self, touch):
        self._mouse.drag = False
        self._mouse.selected_object = None
        self._mouse.down_time_sec = Clock.get_time()
        dxp, dyp, inside = self._draw.touch_pos_to_center_of_widget(self.ids.area, touch.pos)
        if inside:
            changed = False
            match touch.button:
                case 'scrollup':
                    self._draw.pixel_per_micro *= 0.9
                    changed = True
                case 'scrolldown':
                    self._draw.pixel_per_micro *= 1.1
                    changed = True
                case 'left':
                    dx, dy = self._draw.pixel_to_micro(dxp, dyp)
                    shape = self._shape_select(dx, dy)
                    if shape != None:
                        self._mouse.selected_object = shape
                        self._mouse.selected_object_pos = [dx, dy]
                        self._mouse.drag = True
                        self._mouse.drag_begin[0] = touch.pos[0]
                        self._mouse.drag_begin[1] = touch.pos[1]
                        self._mouse.drag_offset = [shape.x, shape.y]
                case 'right':
                    self._mouse.drag = True
                    self._mouse.drag_begin[0] = touch.pos[0]
                    self._mouse.drag_begin[1] = touch.pos[1]
                    self._mouse.drag_offset = self._draw.offset_pixel
            if changed:
                self._face_draw()
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self._mouse.drag == True:
            match touch.button:
                case 'left':
                    shape = self._mouse.selected_object
                    if shape != None and shape.id > 0:
                        dxp = touch.pos[0] - self._mouse.drag_begin[0]
                        dyp = touch.pos[1] - self._mouse.drag_begin[1]
                        dx, dy = self._draw.pixel_to_micro(dxp, dyp)
                        offset = self._mouse.drag_offset
                        shape.x = offset[0] + dx
                        shape.y = offset[1] + dy
                        self._face_draw()
                case 'right':
                    dxp = touch.pos[0] - self._mouse.drag_begin[0] + self._mouse.drag_offset[0]
                    dyp = touch.pos[1] - self._mouse.drag_begin[1] + self._mouse.drag_offset[1]
                    self._draw.offset_pixel = [dxp, dyp]
                    self._face_draw()
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        match touch.button:
            case 'left':
                shape = self._mouse.selected_object
                if Clock.get_time() - self._mouse.down_time_sec < 0.2:
                    if shape != None:
                        if shape.id == 0:
                            pos = self._mouse.selected_object_pos
                            shape.x = pos[0]
                            shape.y = pos[1]
                        self._shape_open(shape)
                return True
        return super().on_touch_up(touch)
    
    def _face_draw(self):
        area = self.ids.area
        area.canvas.clear()
        with area.canvas:
            self._draw.axis(area, [area.center_x, area.center_y], None, 2)
            cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
            self._draw.face(_face_=self._face_edit, _position_=[cx, cy], _color_=clhex("#be3e3eff"))

    def _shape_apply(self):
        self._face_edit.shape.sort(key=lambda s: (s.id == 0, s.x)) # sort using x value and push id = 0 object to the back
        self._face_draw()

    def _shape_delete(self, _shape_):
        _shape_.id = 0
        self._shape_apply()
        self._face_draw()

    def _shape_select(self, _dx_, _dy_):
        shape_index = -1
        shape_index_free = -1
        for i, shape in enumerate(self._face_edit.shape):
            if shape.id > 0:
                if shape.contain(_dx_, _dy_, 10):
                    shape_index = i
                    break
            else:
                if shape_index_free == -1:
                    shape_index_free = i
        if shape_index == -1 and shape_index_free != -1:
            shape_index = shape_index_free
        if shape_index != -1:
            return self._face_edit.shape[shape_index]
        return None
    
    def _shape_open(self, _shape_):
        popup = PopupShape().set_data(
            _shape_=_shape_,
            _rule_=self._rule_,
            _apply_=self._shape_apply,
            _delete_=self._shape_delete
        )
        popup.open()