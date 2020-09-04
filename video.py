from os import path
from structs import *
import random
from PIL import ImageTk, Image
import cv2

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
            if ratio_cropped := self._check_ratio(*self._dim_crop.get_size()):
                if ratio_cropped > self._aspect:
                    width_output = self._size_border.width
                    height_output = int(width_output/ratio_cropped)
                else:
                    height_output = self._size_border.height
                    width_output = int(height_output*ratio_cropped)
            else:
                width_output, height_output = tuple(self._size_border)
            self._image_tk_cropped = ImageTk.PhotoImage(
                image_cropped.resize((width_output, height_output)))
            return self._image_tk_cropped
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
            self._option = option
            if crop_dim:
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