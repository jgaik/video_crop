# pylint: disable=attribute-defined-outside-init, C0114, C0115, C0116, invalid-name, unused-argument
import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
import random
from os import path, linesep
import json
import cv2
from PIL import ImageTk, Image


class OptionList:
    CENTER = 'Center'# pylint: disable=attribute-defined-outside-init, C0114, C0115, C0116, invalid-name, unused-argument
import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
import random
from os import path, linesep
import json
import cv2
from PIL import ImageTk, Image


class OptionList:
    CENTER = 'Center'
    TOP = 'Top'
    BOTTOM = 'Bottom'
    LEFT = 'Left'
    RIGHT = 'Right'
    CUSTOM = 'Custom'

    @classmethod
    def get(cls):
        attr = cls.__dict__
        out = []
        for a in attr:
            if not callable(getattr(cls, a)):
                if not a.startswith("__"):
                    out.append(attr[a])
        return out


class Dimensions:

    class Size:

        def __init__(self, width=0, height=0):
            self.width = width
            self.height = height
            

        def __iter__(self):
            yield self.width
            yield self.height

        def __repr__(self):
            dic = self.__dict__
            keys = [k for k in dic.keys() if k[0] != "_"]
            return json.dumps({
                'class': self.__class__.__name__, 
                'fields': dict([(k, dic[k]) for k in keys])}, indent=4)


    class Position:

        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

        def __iter__(self):
            yield self.x
            yield self.y

        def __repr__(self):
            dic = self.__dict__
            keys = [k for k in dic.keys() if k[0] != "_"]
            return json.dumps({
                'class': self.__class__.__name__, 
                'fields': dict([(k, dic[k]) for k in keys])}, indent=4)

    def __init__(self, pos_x=0, pos_y=0, width=0, height=0):
        self.position = Dimensions.Position(pos_x, pos_y)
        self.size = Dimensions.Size(width, height)

    def set_size(self, width, height):
        self.set_dimension(width=width, height=height)

    def get_size(self):
        return self.size

    def set_position(self, x, y):
        self.set_dimension(x=x, y=y)

    def get_position(self):
        return self.position

    def get_bbox(self):
        return (int(self.position.x - self.size.width/2),
                int(self.position.y - self.size.height/2),
                int(self.position.x + self.size.width/2),
                int(self.position.y + self.size.height/2))

    def set_dimension(self, width=None, height=None, x=None, y=None):
        if not width is None:
            self.size.width = width
        if not height is None:
            self.size.height = height
        if not x is None:
            self.position.x = x
        if not y is None:
            self.position.y = y

    def __repr__(self):
        return json.dumps({
            'class': self.__class__.__name__, 
            'fields': {
                self.position.__class__.__name__: json.loads(str(self.position)), 
                self.size.__class__.__name__: json.loads(str(self.size))}}, indent=4)

class VideoData:

    class Mode:
        WIDE = 2
        TALL = 1
        FIT = 0

        def __init__(self):
            self._current = None

        def set(self, mode):
            self._current = mode
            self._set_options()

        def _set_options(self):
            self._options = [OptionList.CENTER, OptionList.CUSTOM]
            if self._current == self.WIDE:
                self._options[1: 1] = [
                    OptionList.LEFT, OptionList.RIGHT]
            if self._current == self.TALL:
                self._options[1: 1] = [
                    OptionList.TOP, OptionList.BOTTOM]

        def get_options(self):
            if self._current is None:
                return None
            return self._options

        def get(self):
            return self._current

        def check(self, option):
            return option in self._options

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename, self._fileext = path.splitext(filepath)
        self.filename = path.basename(self.filename)
        self._dim_crop = Dimensions()
        self._dim_tk = Dimensions()
        self._video = cv2.VideoCapture(filepath)
        self._mode = VideoData.Mode()
        self._option = None
        self._frames = None
        self._resize_factor = 1

    def is_ok(self):
        return self._video.isOpened()

    def extract_image(self, aspect, random_frame=True):
        self._aspect = aspect
        if not self._frames:
            self._frames = int(self._video.get(cv2.CAP_PROP_FRAME_COUNT))
            self._width = int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if random_frame:
            self._video.set(cv2.CAP_PROP_POS_FRAMES,
                            random.randrange(self._frames))
        status, frame = self._video.read()
        if status:
            self._image = Image.fromarray(frame)
            self._ratio = self._check_ratio(self._width, self._height)
            if not self._ratio:
                self._mode.set(VideoData.Mode.FIT)
            else:
                if self._ratio > 1:
                    self._mode.set(VideoData.Mode.WIDE)
                else:
                    self._mode.set(VideoData.Mode.TALL)

    def get_image(self, size=None, crop=False):
        if crop:
            if size:
                self._size_border = size
            image_cropped = self._image.crop(self._dim_crop.get_bbox())
            if ratio_cropped := self._check_ratio(*self._size_border):
                if ratio_cropped > self._aspect:
                    width_output = self._size_border.width
                    height_output = int(width_output/ratio_cropped)
                else:
                    height_output = self._size_border.height
                    width_output = int(height_output*ratio_cropped)
            else:
                width_output, height_output = tuple(self._size_border)
            self._image_tk_cropped =  ImageTk.PhotoImage(
                image_cropped.resize((width_output, height_output)))
            return self._image_tk_cropped
        else:
            if size:
                if self._mode.get() == VideoData.Mode.FIT:
                    self._dim_tk.set_size(size.width, size.height)
                    self._dim_tk.set_position(0, 0)
                if self._mode.get() == VideoData.Mode.WIDE:
                    self._dim_tk.set_size(
                        width=size.width,
                        height=int(size.width/self._ratio))
                    self._dim_tk.set_position(
                        x=0,
                        y=(size.height - self._dim_tk.size.height)/2)
                if self._mode.get() == VideoData.Mode.TALL:
                    self._dim_tk.set_size(
                        height=size.height,
                        width=int(size.height*self._ratio))
                    self._dim_tk.set_position(
                        x=(size.width - self._dim_tk.size.width)/2,
                        y=0)
                self._image_tk = ImageTk.PhotoImage(
                    self._image.resize(self._dim_tk.get_size()))
                self._size_border = size
                self._aspect = size.width/size.height
                self._resize_factor = self._dim_tk.size.width/self._width
            return self._image_tk

    def set_crop(self, option, crop_dim=None):
        if option == OptionList.CUSTOM:
            self._dim_crop = crop_dim
        else:
            if self._mode.check(option):
                dim = Dimensions()
                self._option = option
                if self._mode.get() == VideoData.Mode.FIT:
                    if option == OptionList.CENTER:
                        dim.set_dimension(
                            width=self._width,
                            height=self._height,
                            x=self._width/2,
                            y=self._height/2)
                if self._mode.get() == VideoData.Mode.WIDE:
                    if option == OptionList.CENTER:
                        dim.set_dimension(
                            height=self._height,
                            width=self._height*self._aspect,
                            x=self._width/2,
                            y=self._height/2)
                    if option == OptionList.LEFT:
                        dim.set_size(
                            height=self._height,
                            width=self._height*self._aspect)
                        dim.set_position(
                            x=dim.size.width/2,
                            y=self._height/2)
                    if option == OptionList.RIGHT:
                        dim.set_size(
                            height=self._height,
                            width=self._height*self._aspect)
                        dim.set_position(
                            x=self._width - dim.size.width/2,
                            y=self._height/2)
                if self._mode.get() == VideoData.Mode.TALL:
                    if option == OptionList.CENTER:
                        dim.set_dimension(
                            width=self._width,
                            height=self._width/self._aspect,
                            x=self._width/2,
                            y=self._height/2)
                    if option == OptionList.BOTTOM:
                        dim.set_size(
                            width=self._width,
                            height=self._width/self._aspect)
                        dim.set_position(
                            x=self._width/2,
                            y=self._height - dim.size.height/2)
                    if option == OptionList.TOP:
                        dim.set_size(
                            width=self._width,
                            height=self._width/self._aspect)
                        dim.set_position(
                            x=self._width/2,
                            y=dim.size.height/2)
                self._dim_crop = dim

    def get_crop(self):
        return self._dim_crop

    def get_position(self):
        return self._dim_tk.get_position()

    def get_size(self):
        return Dimensions.Size(self._width, self._height)

    def get_option(self):
        return self._option
    
    def get_resize_factor(self):
        return self._resize_factor

    def process(self):
        self._video.release()

    def _check_ratio(self, w, h):
        if w/h/self._aspect == 1:
            return False
        return w/h


class App:

    def __init__(self, master):
        self.master = master
        self.videos = []
        self.show_idx = 0

        self.filetypes = {
            'MP4': '.mp4',
            'WEBM': '.webm',
            'MPEG': '.mpeg .mpg',
            'AVI': '.avi',
            'Any': '.*'
        }

        self.aspects = {
            '16:9': 16/9,
            '16:10': 16/10,
            '4:3': 4/3
        }

        self.aspect = 1
        self.dim_canvas = Dimensions(width=320, height=0, pos_x=160, pos_y=0)
        self.image_canvas_after = None
        self.image_canvas_before = None

        self.frame_control = ttk.Frame(self.master)
        self.frame_custom = ttk.LabelFrame(self.master, text='Custom crop')
        self.frame_text = ttk.Frame(self.frame_control)

        self.var_video = tk.StringVar()
        self.option_video = ttk.OptionMenu(
            self.master, variable=self.var_video)
        self.frame_preview = ttk.LabelFrame(
            self.master, text='Preview', labelwidget=None)

        self.scroll_filepaths = ttk.Scrollbar(
            self.frame_text, orient=tk.HORIZONTAL)
        self.text_filepaths = tk.Text(
            self.frame_text, height=1, width=30,
            xscrollcommand=self.scroll_filepaths.set, wrap=tk.NONE)
        self.button_choose_video = ttk.Button(
            self.frame_control, text="Choose video..", command=self.event_add_videos)
        self.scroll_filepaths.config(command=self.text_filepaths.xview)

        self.canvas_video_before = tk.Canvas(
            self.frame_preview, bg='black',
            width=self.dim_canvas.size.width, height=self.dim_canvas.size.height,
            relief=tk.SUNKEN)
        label_video_before = ttk.Label(self.frame_preview, text='Before')
        self.canvas_video_after = tk.Canvas(
            self.frame_preview, bg='black',
            width=self.dim_canvas.size.width, height=self.dim_canvas.size.height,
            relief=tk.SUNKEN)
        label_video_after = ttk.Label(self.frame_preview, text='After')

        self.var_aspect = tk.StringVar()
        self.option_aspect = ttk.OptionMenu(
            self.frame_control, self.var_aspect)
        for a in self.aspects:
            self.option_aspect.children['!menu'].add_command(
                label=a, command=lambda x=a: self.prepare_canvas(aspect=x))

        self.button_save_video = ttk.Button(
            self.master, text="Crop and Save video", command=self.event_save_videos)

        self.var_option = tk.StringVar(value=OptionList.CENTER)
        self.option_crop = ttk.OptionMenu(self.frame_control, self.var_option)
        for op in OptionList().get():
            self.option_crop.children['!menu'].add_command(
                label=op, command=lambda x=op: self.event_change_option(x))

        self.notebook_custom = ttk.Notebook(self.frame_custom)
        self.tab_size = ttk.Frame(self.notebook_custom)
        self.tab_position = ttk.Frame(self.notebook_custom)

        label_width = ttk.Label(self.tab_size, text='Width:')
        label_height = ttk.Label(self.tab_size, text='Height:')
        label_x = ttk.Label(self.tab_position, text='X:')
        label_y = ttk.Label(self.tab_position, text='Y:')
        self.spin_width = ttk.Spinbox(
            self.tab_size, from_=0, command=self.event_spin_rect, width=4)
        self.spin_height = ttk.Spinbox(
            self.tab_size, from_=0, command=self.event_spin_rect, width=4)
        self.spin_x = ttk.Spinbox(
            self.tab_position, from_=0, command=self.event_spin_rect, width=4)
        self.spin_y = ttk.Spinbox(
            self.tab_position, from_=0, command=self.event_spin_rect, width=4)

        #frame main
        self.frame_control.grid(row=0, column=0, sticky='nswe')
        self.frame_custom.grid(row=0, column=1, sticky='nswe')
        self.frame_preview.grid(row=1, column=0, columnspan=2)
        self.button_save_video.grid(row=2, column=0, columnspan=2)

        #frame control
        self.button_choose_video.grid(row=0, column=0)
        self.text_filepaths.grid(sticky='nwe')
        self.scroll_filepaths.grid(row=1, sticky='nwe')
        self.frame_text.grid(row=0, column=1, rowspan=3, sticky='ns')
        self.option_aspect.grid(row=1, column=0)
        self.option_crop.grid(row=2, column=0)

        #frame preview
        self.canvas_video_before.grid(row=0, column=0, padx=10)
        self.canvas_video_after.grid(row=0, column=1, padx=10)
        label_video_before.grid(row=1, column=0, pady=5)
        label_video_after.grid(row=1, column=1, pady=5)

        #frame custom
        self.notebook_custom.add(self.tab_size, text="Size")
        self.notebook_custom.add(self.tab_position, text="Position")
        self.notebook_custom.pack(fill=tk.BOTH)
        label_width.grid(row=0, column=0)
        self.spin_width.grid(row=0, column=1)
        label_height.grid(row=1, column=0)
        self.spin_height.grid(row=1, column=1)
        label_x.grid(row=0, column=0)
        self.spin_x.grid(row=0, column=1)
        label_y.grid(row=1, column=0)
        self.spin_y.grid(row=1, column=1)


        self.prepare_canvas(aspect='16:9')

    def event_add_videos(self):
        filepaths = fdiag.askopenfilenames(
            parent=self.master,
            filetypes=[(k, v) for (k, v) in self.filetypes.items()],
            defaultextension='.mp4')
        if filepaths:
            for fpath in filepaths:
                video = VideoData(fpath)
                if video.is_ok():
                    video.extract_image(self.aspect)
                    video.set_crop(self.var_option.get())
                    self.option_video.children['!menu'].add_command(
                        label=video.filename,
                        command=lambda x=len(self.videos): self.prepare_canvas(x))
                    self.text_filepaths.insert(
                        tk.END, video.filepath + linesep)
                    self.videos.append(video)
            self.text_filepaths.config(height=len(self.videos))
            self.frame_preview.config(labelwidget=self.option_video)
            self.prepare_canvas(idx=len(self.videos)-1)

    def event_save_videos(self):
        if self.videos:
            directory = fdiag.askdirectory(
                parent=self.master, initialdir=path.expanduser("~"))
            if directory:
                self.text_filepaths.delete('0.0', tk.END)
                self.clear_canvas()

    def clear_canvas(self):
        self.frame_preview.config(labelwidget=None)

    def prepare_canvas(self, idx=None, aspect=None):
        if aspect:
            self.var_aspect.set(aspect)
            self.aspect = self.aspects[aspect]
            self.dim_canvas.set_dimension(
                height=int(self.dim_canvas.size.width/self.aspect))
            self.dim_canvas.set_dimension(y=self.dim_canvas.size.height/2)
            self.canvas_video_before.config(height=self.dim_canvas.size.height)
            self.canvas_video_after.config(height=self.dim_canvas.size.height)
        if not idx is None:
            self.show_idx = idx
        if self.videos:
            video = self.videos[self.show_idx]
            self.var_video.set(video.filename)
            if self.image_canvas_before:
                self.canvas_video_before.itemconfig(
                    self.image_canvas_before,
                    image=video.get_image(size=self.dim_canvas.get_size()))
                self.canvas_video_before.coords(
                    self.image_canvas_before,
                    *self.dim_canvas.get_position())
            else:
                self.image_canvas_before = self.canvas_video_before.create_image(
                    *self.dim_canvas.get_position(),
                    image=video.get_image(size=self.dim_canvas.get_size()))
            self.update_canvas()

    def update_canvas(self):
        if self.videos:
            video = self.videos[self.show_idx]
            option = video.get_option()
            self.var_option.set(option)

            rect_dim = self.set_spin(video.get_crop())
            video_pos = video.get_position()
            rect_bbox = self._rect2canvas(
                rect_dim, 
                video_pos, 
                video.get_resize_factor()).get_bbox()
            if self.image_canvas_after:
                self.canvas_video_after.itemconfig(
                    self.image_canvas_after,
                    image=video.get_image(crop=True))
                self.canvas_video_after.coords(
                    self.image_canvas_after,
                    *self.dim_canvas.get_position())
                self.canvas_video_before.coords(
                    self.rect_croparea, *rect_bbox)
            else:
                self.image_canvas_after = self.canvas_video_after.create_image(
                    *self.dim_canvas.get_position(),
                    image=video.get_image(crop=True))
                self.rect_croparea = self.canvas_video_before.create_rectangle(
                    *rect_bbox, width=3, outline='red')

    def event_change_option(self, option):
        self.var_option.set(option)
        if self.videos:
            self.videos[self.show_idx].set_crop(option)
            self.update_canvas()

    def event_spin_rect(self):
        if self.videos:
            dim_new = self.set_spin(
                Dimensions(
                    pos_x=self.spin_x.get(),
                    pos_y=self.spin_y.get(),
                    width=self.spin_width.get(),
                    height=self.spin_height.get()))
            self.var_option.set(OptionList.CUSTOM)
            video = self.videos[self.show_idx]
            video.set_crop(option=OptionList.CUSTOM, crop_dim=dim_new)
            self.update_canvas()

    def _rect2canvas(self, rect_dim, video_pos, factor):
        pos_rect = rect_dim.get_position()
        return Dimensions(
            width=rect_dim.size.width*factor,
            height=rect_dim.size.height*factor,
            pos_x=pos_rect.x * factor + video_pos.x,
            pos_y=pos_rect.y * factor + video_pos.y
        )

    def set_spin(self, rect_dim):
        max_width, max_height = self.videos[self.show_idx].get_size()
        self.spin_height.set(int(rect_dim.size.height))
        self.spin_width.set(int(rect_dim.size.width))
        if (dx := rect_dim.position.x + rect_dim.size.width/2 - max_width) > 0:
            rect_dim.position.x -= dx
        self.spin_x.set(int(rect_dim.position.x))
        if (dy := rect_dim.position.y + rect_dim.size.height/2 - max_height) > 0:
            rect_dim.position.y -= dy
        self.spin_y.set(int(rect_dim.position.y))
        self.spin_height.config({
            'to': max_height})
        self.spin_width.config({
            'to': max_width})
        self.spin_x.config({
            'from': rect_dim.size.width/2,
            'to': max_width - rect_dim.size.width/2})
        self.spin_y.config({
            'from': rect_dim.size.height/2,
            'to': max_height - rect_dim.size.height/2})

        return rect_dim

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()

    TOP = 'Top'
    BOTTOM = 'Bottom'
    LEFT = 'Left'
    RIGHT = 'Right'
    CUSTOM = 'Custom'

    @classmethod
    def get(cls):
        attr = cls.__dict__
        out = []
        for a in attr:
            if not callable(getattr(cls, a)):
                if not a.startswith("__"):
                    out.append(attr[a])
        return out


class Dimensions:

    class Size:

        def __init__(self, width=0, height=0):
            self.width = width
            self.height = height
            

        def __iter__(self):
            yield self.width
            yield self.height

        def __repr__(self):
            dic = self.__dict__
            keys = [k for k in dic.keys() if k[0] != "_"]
            return json.dumps({
                'class': self.__class__.__name__, 
                'fields': dict([(k, dic[k]) for k in keys])}, indent=4)


    class Position:

        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

        def __iter__(self):
            yield self.x
            yield self.y

        def __repr__(self):
            dic = self.__dict__
            keys = [k for k in dic.keys() if k[0] != "_"]
            return json.dumps({
                'class': self.__class__.__name__, 
                'fields': dict([(k, dic[k]) for k in keys])}, indent=4)

    def __init__(self, pos_x=0, pos_y=0, width=0, height=0):
        self.position = Dimensions.Position(pos_x, pos_y)
        self.size = Dimensions.Size(width, height)

    def set_size(self, width, height):
        self.set_dimension(width=width, height=height)

    def get_size(self):
        return self.size

    def set_position(self, x, y):
        self.set_dimension(x=x, y=y)

    def get_position(self):
        return self.position

    def get_bbox(self):
        return (int(self.position.x - self.size.width/2),
                int(self.position.y - self.size.height/2),
                int(self.position.x + self.size.width/2),
                int(self.position.y + self.size.height/2))

    def set_dimension(self, width=None, height=None, x=None, y=None):
        if not width is None:
            self.size.width = width
        if not height is None:
            self.size.height = height
        if not x is None:
            self.position.x = x
        if not y is None:
            self.position.y = y

    def __repr__(self):
        return json.dumps({
            'class': self.__class__.__name__, 
            'fields': {
                self.position.__class__.__name__: json.loads(str(self.position)), 
                self.size.__class__.__name__: json.loads(str(self.size))}}, indent=4)

class VideoData:

    class Mode:
        WIDE = 2
        TALL = 1
        FIT = 0

        def __init__(self):
            self._current = None

        def set(self, mode):
            self._current = mode
            self._set_options()

        def _set_options(self):
            self._options = [OptionList.CENTER, OptionList.CUSTOM]
            if self._current == self.WIDE:
                self._options[1: 1] = [
                    OptionList.LEFT, OptionList.RIGHT]
            if self._current == self.TALL:
                self._options[1: 1] = [
                    OptionList.TOP, OptionList.BOTTOM]

        def get_options(self):
            if self._current is None:
                return None
            return self._options

        def get(self):
            return self._current

        def check(self, option):
            return option in self._options

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename, self._fileext = path.splitext(filepath)
        self.filename = path.basename(self.filename)
        self._dim_crop = Dimensions()
        self._dim_tk = Dimensions()
        self._video = cv2.VideoCapture(filepath)
        self._mode = VideoData.Mode()
        self._option = OptionList.CENTER
        self._frames = None
        self._resize_factor = 1

    def is_ok(self):
        return self._video.isOpened()

    def extract_image(self, aspect, random_frame=True):
        self._aspect = aspect
        if not self._frames:
            self._frames = int(self._video.get(cv2.CAP_PROP_FRAME_COUNT))
            self._width = int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if random_frame:
            self._video.set(cv2.CAP_PROP_POS_FRAMES,
                            random.randrange(self._frames))
        status, frame = self._video.read()
        if status:
            self._image = Image.fromarray(frame)
            self._ratio = self._check_ratio(self._width, self._height)
            if not self._ratio:
                self._mode.set(VideoData.Mode.FIT)
            else:
                if self._ratio > 1:
                    self._mode.set(VideoData.Mode.WIDE)
                else:
                    self._mode.set(VideoData.Mode.TALL)

    def get_image(self, size=None, crop=False):
        if crop:
            if size:
                self._size_border = size
            image_cropped = self._image.crop(self._dim_crop.get_bbox())
            if ratio_cropped := self._check_ratio(*self._size_border):
                if ratio_cropped > self._aspect:
                    width_output = self._size_border.width
                    height_output = int(width_output/ratio_cropped)
                else:
                    height_output = self._size_border.height
                    width_output = int(height_output*ratio_cropped)
            else:
                width_output, height_output = tuple(self._size_border)
            self._image_tk_cropped =  ImageTk.PhotoImage(
                image_cropped.resize((width_output, height_output)))
            return self._image_tk_cropped
        else:
            if size:
                if self._mode.get() == VideoData.Mode.FIT:
                    self._dim_tk.set_size(size.width, size.height)
                    self._dim_tk.set_position(0, 0)
                if self._mode.get() == VideoData.Mode.WIDE:
                    self._dim_tk.set_size(
                        width=size.width,
                        height=int(size.width/self._ratio))
                    self._dim_tk.set_position(
                        x=0,
                        y=(size.height - self._dim_tk.size.height)/2)
                if self._mode.get() == VideoData.Mode.TALL:
                    self._dim_tk.set_size(
                        height=size.height,
                        width=int(size.height*self._ratio))
                    self._dim_tk.set_position(
                        x=(size.width - self._dim_tk.size.width)/2,
                        y=0)
                self._image_tk = ImageTk.PhotoImage(
                    self._image.resize(self._dim_tk.get_size()))
                self._size_border = size
                self._aspect = size.width/size.height
                self._resize_factor = self._dim_tk.size.width/self._width
            return self._image_tk

    def set_crop(self, crop_dim):
        self._dim_crop = crop_dim

    def get_crop(self, option=None, crop_dim=None):
        if option == OptionList.CUSTOM:
            self.set_crop(crop_dim)
        else:
            if self._mode.check(option):
                dim = Dimensions()
                self._option = option
                if self._mode.get() == VideoData.Mode.FIT:
                    if option == OptionList.CENTER:
                        dim.set_dimension(
                            width=self._width,
                            height=self._height,
                            x=self._width/2,
                            y=self._height/2)
                if self._mode.get() == VideoData.Mode.WIDE:
                    if option == OptionList.CENTER:
                        dim.set_dimension(
                            height=self._height,
                            width=self._height*self._aspect,
                            x=self._width/2,
                            y=self._height/2)
                    if option == OptionList.LEFT:
                        dim.set_size(
                            height=self._height,
                            width=self._height*self._aspect)
                        dim.set_position(
                            x=dim.size.width/2,
                            y=self._height/2)
                    if option == OptionList.RIGHT:
                        dim.set_size(
                            height=self._height,
                            width=self._height*self._aspect)
                        dim.set_position(
                            x=self._width - dim.size.width/2,
                            y=self._height/2)
                if self._mode.get() == VideoData.Mode.TALL:
                    if option == OptionList.CENTER:
                        dim.set_dimension(
                            width=self._width,
                            height=self._width/self._aspect,
                            x=self._width/2,
                            y=self._height/2)
                    if option == OptionList.BOTTOM:
                        dim.set_size(
                            width=self._width,
                            height=self._width/self._aspect)
                        dim.set_position(
                            x=self._width/2,
                            y=self._height - dim.size.height/2)
                    if option == OptionList.TOP:
                        dim.set_size(
                            width=self._width,
                            height=self._width/self._aspect)
                        dim.set_position(
                            x=self._width/2,
                            y=dim.size.height/2)
                self.set_crop(dim)
        return self._dim_crop

    def get_position(self):
        return self._dim_tk.get_position()

    def get_size(self):
        return Dimensions.Size(self._width, self._height)

    def get_option(self):
        return self._option
    
    def get_resize_factor(self):
        return self._resize_factor

    def process(self):
        self._video.release()

    def _check_ratio(self, w, h):
        if w/h/self._aspect == 1:
            return False
        return w/h


class App:

    def __init__(self, master):
        self.master = master
        self.videos = []
        self.show_idx = 0

        self.filetypes = {
            'MP4': '.mp4',
            'WEBM': '.webm',
            'MPEG': '.mpeg .mpg',
            'AVI': '.avi',
            'Any': '.*'
        }

        self.aspects = {
            '16:9': 16/9,
            '16:10': 16/10,
            '4:3': 4/3
        }

        self.aspect = 1
        self.dim_canvas = Dimensions(width=320, height=0, pos_x=160, pos_y=0)
        self.image_canvas_after = None
        self.image_canvas_before = None

        self.frame_control = ttk.Frame(self.master)
        self.frame_custom = ttk.Frame(self.master)
        self.frame_text = ttk.Frame(self.frame_control)

        self.var_video = tk.StringVar()
        self.option_video = ttk.OptionMenu(
            self.master, variable=self.var_video)
        self.frame_preview = ttk.LabelFrame(
            self.master, text='Preview', labelwidget=None)

        self.scroll_filepaths = ttk.Scrollbar(
            self.frame_text, orient=tk.HORIZONTAL)
        self.text_filepaths = tk.Text(
            self.frame_text, height=1, width=30,
            xscrollcommand=self.scroll_filepaths.set, wrap=tk.NONE)
        self.button_choose_video = ttk.Button(
            self.frame_control, text="Choose video..", command=self.event_add_videos)
        self.scroll_filepaths.config(command=self.text_filepaths.xview)

        self.canvas_video_before = tk.Canvas(
            self.frame_preview, bg='black',
            width=self.dim_canvas.size.width, height=self.dim_canvas.size.height,
            relief=tk.SUNKEN)
        label_video_before = ttk.Label(self.frame_preview, text='Before')
        self.canvas_video_after = tk.Canvas(
            self.frame_preview, bg='black',
            width=self.dim_canvas.size.width, height=self.dim_canvas.size.height,
            relief=tk.SUNKEN)
        label_video_after = ttk.Label(self.frame_preview, text='After')

        self.var_aspect = tk.StringVar()
        self.option_aspect = ttk.OptionMenu(
            self.frame_control, self.var_aspect)
        for a in self.aspects:
            self.option_aspect.children['!menu'].add_command(
                label=a, command=lambda x=a: self.prepare_canvas(aspect=x))

        self.button_save_video = ttk.Button(
            self.master, text="Crop and Save video", command=self.event_save_videos)

        self.var_option = tk.StringVar(value=OptionList.CENTER)
        self.option_crop = ttk.OptionMenu(self.frame_control, self.var_option)
        for op in OptionList().get():
            self.option_crop.children['!menu'].add_command(
                label=op, command=lambda x=op: self.event_change_option(x))

        self.spin_width = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)
        self.spin_height = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)
        self.spin_x = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)
        self.spin_y = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)

        self.frame_control.grid(row=0, column=0)
        self.frame_custom.grid(row=0, column=1)
        self.frame_preview.grid(row=1, column=0, columnspan=2)

        self.button_choose_video.grid(row=0, column=0)
        self.text_filepaths.grid(sticky='nwe')
        self.scroll_filepaths.grid(row=1, sticky='nwe')
        self.frame_text.grid(row=0, column=1, rowspan=3, sticky='ns')
        self.option_aspect.grid(row=1, column=0)
        self.option_crop.grid(row=2, column=0)

        self.canvas_video_before.grid(row=0, column=0, padx=10)
        self.canvas_video_after.grid(row=0, column=1, padx=10)
        label_video_before.grid(row=1, column=0, pady=5)
        label_video_after.grid(row=1, column=1, pady=5)

        self.spin_width.pack()
        self.spin_height.pack()
        self.spin_x.pack()
        self.spin_y.pack()

        self.button_save_video.grid(row=2, column=0, columnspan=2)

        self.prepare_canvas(aspect='16:9')

    def event_add_videos(self):
        filepaths = fdiag.askopenfilenames(
            parent=self.master,
            filetypes=[(k, v) for (k, v) in self.filetypes.items()],
            defaultextension='.mp4')
        if filepaths:
            for fpath in filepaths:
                video = VideoData(fpath)
                if video.is_ok():
                    video.extract_image(self.aspect)
                    self.option_video.children['!menu'].add_command(
                        label=video.filename,
                        command=lambda x=len(self.videos): self.prepare_canvas(x))
                    self.text_filepaths.insert(
                        tk.END, video.filepath + linesep)
                    self.videos.append(video)
            self.text_filepaths.config(height=len(self.videos))
            self.frame_preview.config(labelwidget=self.option_video)
            self.prepare_canvas(idx=len(self.videos)-1)

    def event_save_videos(self):
        if self.videos:
            directory = fdiag.askdirectory(
                parent=self.master, initialdir=path.expanduser("~"))
            if directory:
                self.text_filepaths.delete('0.0', tk.END)
                self.clear_canvas()

    def clear_canvas(self):
        self.frame_preview.config(labelwidget=None)

    def prepare_canvas(self, idx=None, aspect=None):
        if aspect:
            self.var_aspect.set(aspect)
            self.aspect = self.aspects[aspect]
            self.dim_canvas.set_dimension(
                height=int(self.dim_canvas.size.width/self.aspect))
            self.dim_canvas.set_dimension(y=self.dim_canvas.size.height/2)
            self.canvas_video_before.config(height=self.dim_canvas.size.height)
            self.canvas_video_after.config(height=self.dim_canvas.size.height)
        if not idx is None:
            self.show_idx = idx
        if self.videos:
            video = self.videos[self.show_idx]
            self.var_video.set(video.filename)
            if self.image_canvas_before:
                self.canvas_video_before.itemconfig(
                    self.image_canvas_before,
                    image=video.get_image(size=self.dim_canvas.get_size()))
                self.canvas_video_before.coords(
                    self.image_canvas_before,
                    *self.dim_canvas.get_position())
            else:
                self.image_canvas_before = self.canvas_video_before.create_image(
                    *self.dim_canvas.get_position(),
                    image=video.get_image(size=self.dim_canvas.get_size()))
            self.update_canvas()

    def update_canvas(self):
        if self.videos:
            video = self.videos[self.show_idx]
            if option:
                rect_dim = video.get_crop()
                video_pos = video.get_position()
                rect_bbox = self._rect2canvas(
                    rect_dim, 
                    video_pos, 
                    video.get_resize_factor()).get_bbox()
            if self.image_canvas_after:
                self.canvas_video_after.itemconfig(
                    self.image_canvas_after,
                    image=video.get_image(crop=True))
                self.canvas_video_after.coords(
                    self.image_canvas_after,
                    *self.dim_canvas.get_position())
                self.canvas_video_before.coords(
                    self.rect_croparea, *rect_bbox)
            else:
                self.image_canvas_after = self.canvas_video_after.create_image(
                    *self.dim_canvas.get_position(),
                    image=video.get_image(crop=True))
                self.rect_croparea = self.canvas_video_before.create_rectangle(
                    *rect_bbox, width=3, outline='red')

    def event_change_option(self, option):
        self.var_option.set(option)
        self.update_canvas(option)

    def event_spin_rect(self):
        if self.videos:
            self.var_option.set(OptionList.CUSTOM)
            video = self.videos[self.show_idx]
            video.set_crop()

    def _rect2canvas(self, rect_dim, video_dim, factor):
        pos_rect = rect_dim.get_position()
        pos_vid = video_dim.get_position()
        return Dimensions(
            width=rect_dim.size.width*factor,
            height=rect_dim.size.height*factor,
            pos_x=pos_rect.x * factor + pos_vid.x,
            pos_y=pos_rect.y * factor + pos_vid.y
        )
    '''
        posx_spin = int(self.spin_x.get())
        posy_spin = int(self.spin_y.get())
        width_spin = int(self.spin_width.get())
        height_spin = int(self.spin_height.get())
        if (dx := posx_spin + width_spin/2 - self.width_input) > 0:
            self.spin_x.set(int(posx_spin - dx))
        if (dy := posy_spin + height_spin/2 - self.height_input) > 0:
            self.spin_y.set(int(posy_spin - dy))
        self.spin_x.config({
            'from': 0 + width_spin/2,
            'to': self.width_input - width_spin/2
        })
        self.spin_y.config({
            'from': 0 + height_spin/2,
            'to': self.height_input - height_spin/2
        })

        factor = self.width_imagetk/self.width_input
        width_rect = width_spin * factor
        height_rect = height_spin * factor
        posx_rect = posx_spin * factor - width_rect/2 + self.posx_imagetk
        posy_rect = (self.height_input - posy_spin) * \
            factor - height_rect/2 + self.posy_imagetk

        self.canvas_video_before.coords(
            self.rect_croparea,
            posx_rect,
            posy_rect,
            posx_rect + width_rect,
            posy_rect + height_rect)
        self.update_canvas_after()
    '''


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()
