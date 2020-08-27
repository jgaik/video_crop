#pylint: disable=attribute-defined-outside-init, C0114, C0115, C0116, invalid-name, unused-argument
import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
import random
import cv2
from PIL import ImageTk, Image


class App:

    class OptionList:
        CENTER = 'Center'
        CUSTOM = 'Custom'
        LEFT = 'Left'
        RIGHT = 'Right'
        TOP = 'Top'
        BOTTOM = 'Bottom'

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
            self._options = [App.OptionList.CENTER, App.OptionList.CUSTOM]
            if self._current == self.WIDE:
                self._options[1:1] = [
                    App.OptionList.LEFT, App.OptionList.RIGHT]
            if self._current == self.TALL:
                self._options[1:1] = [
                    App.OptionList.TOP, App.OptionList.BOTTOM]

        def get_options(self):
            if self._current is None:
                return None
            return self._options

        def get(self):
            return self._current

    def __init__(self, master):
        self.master = master
        self._mode = self.Mode()

        self.aspects = {
            '16:9': 16/9,
            '16:10': 16/10,
            '4:3': 4/3
        }

        self.aspect = self.aspects['16:9']
        self.width_canvas = 320
        self.height_canvas = int(self.width_canvas/self.aspect)

        self.var_video_edit = tk.StringVar()
        self.entry_video_edit = ttk.Entry(
            self.master, textvariable=self.var_video_edit)
        self.button_choose_video = ttk.Button(
            self.master, text="Choose video..", command=self.event_choose_video)

        self.button_save_video = ttk.Button(
            self.master, text="Crop and Save video", command=self.event_save_video)

        self.canvas_video_before = tk.Canvas(
            self.master, bg='black',
            width=self.width_canvas, height=self.height_canvas,
            relief=tk.SUNKEN)
        self.canvas_video_after = tk.Canvas(
            self.master, bg='black',
            width=self.width_canvas, height=self.height_canvas,
            relief=tk.SUNKEN)

        self.var_option = tk.StringVar()
        self.var_option.trace("w", self.event_option_change)
        self.option_crop = ttk.OptionMenu(self.master, self.var_option)

        self.spin_width = ttk.Spinbox(
            self.master, from_=0, command=self.event_spin_rect)
        self.spin_height = ttk.Spinbox(
            self.master, from_=0, command=self.event_spin_rect)
        self.spin_x = ttk.Spinbox(
            self.master, from_=0, command=self.event_spin_rect)
        self.spin_y = ttk.Spinbox(
            self.master, from_=0, command=self.event_spin_rect)

        self.button_choose_video.pack()
        self.entry_video_edit.pack()

        self.button_save_video.pack()

        self.canvas_video_before.pack()
        self.canvas_video_after.pack()

        self.option_crop.pack()
        self.spin_width.pack()
        self.spin_height.pack()
        self.spin_x.pack()
        self.spin_y.pack()

    def event_choose_video(self):
        filename_in = fdiag.askopenfilename(parent=self.master)
        if filename_in:
            self.var_video_edit.set(filename_in)
            self.extract_frame(filename_in)

    def event_save_video(self):
        filename_out = fdiag.asksaveasfilename(parent=self.master)
        if filename_out:
            print(filename_out)

    def extract_frame(self, path_video):
        video = cv2.VideoCapture(path_video)
        try:
            frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.width_input = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height_input = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video.set(cv2.CAP_PROP_POS_FRAMES,
                      random.randrange(int(frames_count)))
            status, frame = video.read()
            if status:
                def check_ratio(w, h):
                    if w/h/self.aspect == 1:
                        return False
                    return w/h
                self.ratio_input = check_ratio(
                    self.width_input, self.height_input)
                self.image_input = Image.fromarray(frame)
                if not self.ratio_input:
                    self.width_imagetk = self.width_canvas
                    self.height_imagetk = self.height_canvas
                    self._mode.set(self.Mode.FIT)
                else:
                    if self.ratio_input > 1:
                        self.width_imagetk = self.width_canvas
                        self.height_imagetk = int(
                            self.width_canvas/self.ratio_input)
                        self._mode.set(self.Mode.WIDE)
                    else:
                        self.height_imagetk = self.height_canvas
                        self.width_imagetk = int(
                            self.height_canvas*self.ratio_input)
                        self._mode.set(self.Mode.TALL)

            self.prepare_canvas_before()
            self.set_options()
            self.prepare_canvas_after()
        finally:
            video.release()

    def prepare_canvas_before(self):
        self.posx_imagetk = (self.width_canvas - self.width_imagetk)/2
        self.posy_imagetk = (self.height_canvas - self.height_imagetk)/2
        self.imagetk_input = ImageTk.PhotoImage(
            self.image_input.resize((self.width_imagetk, self.height_imagetk)))
        self.canvas_video_before.create_image(
            self.width_canvas/2, self.height_canvas/2, image=self.imagetk_input)
        self.rect_croparea = self.canvas_video_before.create_rectangle(
            0, 0, 0, 0, fill='', outline='red', width=3)

    def prepare_canvas_after(self):
        pass

    def set_options(self):
        self.option_crop.children['!menu'].delete(0, 'end')
        options = self._mode.get_options()
        for op in options:
            self.option_crop.children['!menu'].add_command(
                label=op, command=lambda x=op: self.var_option.set(x))
        self.var_option.set(options[0])
        self.spin_x.config({'to': self.width_input})
        self.spin_y.config({'to': self.height_input})
        self.spin_width.config({'to': self.width_input})
        self.spin_height.config({'to': self.height_input})

    def event_option_change(self, *args):
        if (option := self.var_option.get()) == App.OptionList.CUSTOM:
            pass
        else:
            if self._mode.get() == App.Mode.FIT:
                if option == App.OptionList.CENTER:
                    self.posx_crop = 0
                    self.posy_crop = 0
                    self.width_crop = self.width_imagetk
                    self.height_crop = self.height_imagetk
            if self._mode.get() == App.Mode.WIDE:
                if option == App.OptionList.CENTER:
                    self.height_crop = self.height_imagetk
                    self.width_crop = self.height_crop*self.aspect
                    self.posx_crop = (self.width_canvas - self.width_crop)/2
                    self.posy_crop = (self.height_canvas - self.height_crop)/2
                if option == App.OptionList.LEFT:
                    self.height_crop = self.height_imagetk
                    self.width_crop = self.height_crop*self.aspect
                    self.posx_crop = 0
                    self.posy_crop = (self.height_canvas - self.height_crop)/2
                if option == App.OptionList.RIGHT:
                    self.height_crop = self.height_imagetk
                    self.width_crop = self.height_crop*self.aspect
                    self.posx_crop = self.width_canvas - self.width_crop
                    self.posy_crop = (self.height_canvas - self.height_crop)/2
            if self._mode.get() == App.Mode.TALL:
                if option == App.OptionList.CENTER:
                    self.width_crop = self.width_imagetk
                    self.height_crop = self.width_crop/self.aspect
                    self.posx_crop = (self.width_canvas - self.width_crop)/2
                    self.posy_crop = (self.height_canvas - self.height_crop)/2
                if option == App.OptionList.TOP:
                    self.width_crop = self.width_imagetk
                    self.height_crop = self.width_crop/self.aspect
                    self.posx_crop = (self.width_canvas - self.width_crop)/2
                    self.posy_crop = 0
                if option == App.OptionList.BOTTOM:
                    self.width_crop = self.width_imagetk
                    self.height_crop = self.width_crop/self.aspect
                    self.posx_crop = (self.width_canvas - self.width_crop)/2
                    self.posy_crop = self.height_canvas - self.height_crop
            self.canvas2spin()
            self.change_croparea()

    def event_spin_rect(self):
        posx_spin = int(self.spin_x.get())
        posy_spin = int(self.spin_y.get())
        width_spin = int(self.spin_width.get())
        height_spin = int(self.spin_height.get())
        if (dx := posx_spin + width_spin/2 - self.width_input) > 0:
            self.spin_x.set(int(posx_spin - dx))
        if (dy := posy_spin + height_spin/2 - self.height_input) > 0:
            self.spin_y.set(int(posy_spin - dy))
        self.spin_x.config({
            'from': 0 + width_spin/2 - 1,
            'to': self.width_input - width_spin/2 + 1
        })
        self.spin_y.config({
            'from': 0 + height_spin/2 - 1,
            'to': self.height_input - height_spin/2 + 1
        })
        self.spin2canvas()
        self.change_croparea()

    def canvas2spin(self):
        factor = self.width_input/self.width_imagetk

        self.spin_width.set(int(self.width_crop*factor))
        self.spin_height.set(int(self.height_crop*factor))
        self.spin_x.set(
            int((self.posx_crop - self.posx_imagetk + self.width_crop/2)*factor))
        self.spin_y.set(
            int(self.height_input - (self.posy_crop -
                                     self.posy_imagetk + self.height_crop/2) * factor))

    def spin2canvas(self):
        factor = self.width_imagetk/self.width_input
        posx_spin = int(self.spin_x.get())
        posy_spin = int(self.spin_y.get())
        width_spin = int(self.spin_width.get())
        height_spin = int(self.spin_height.get())

        self.width_crop = width_spin * factor
        self.height_crop = height_spin * factor
        self.posx_crop = posx_spin * factor - self.width_crop/2 + self.posx_imagetk
        self.posy_crop = (self.height_input - posy_spin) * \
            factor - self.height_crop/2 + self.posy_imagetk

    def change_croparea(self):
        self.canvas_video_before.coords(
            self.rect_croparea,
            self.posx_crop,
            self.posy_crop,
            self.posx_crop + self.width_crop,
            self.posy_crop + self.height_crop)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()
