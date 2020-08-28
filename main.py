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

        self.frame_control =  ttk.Frame(self.master)
        self.frame_custom = ttk.Frame(self.master)
        self.frame_preview = ttk.LabelFrame(self.master, text='Preview')

        self.var_video_edit = tk.StringVar()
        self.entry_video_edit = ttk.Entry(
            self.frame_control, textvariable=self.var_video_edit)
        self.button_choose_video = ttk.Button(
            self.frame_control, text="Choose video..", command=self.event_choose_video)

        self.button_save_video = ttk.Button(
            self.master, text="Crop and Save video", command=self.event_save_video)

        self.canvas_video_before = tk.Canvas(
            self.frame_preview, bg='black',
            width=self.width_canvas, height=self.height_canvas,
            relief=tk.SUNKEN)
        label_video_before = ttk.Label(self.frame_preview, text='Before')
        self.canvas_video_after = tk.Canvas(
            self.frame_preview, bg='black',
            width=self.width_canvas, height=self.height_canvas,
            relief=tk.SUNKEN)
        label_video_after = ttk.Label(self.frame_preview, text='After')

        self.var_option = tk.StringVar()
        self.var_option.trace("w", self.event_option_change)
        self.option_crop = ttk.OptionMenu(self.frame_control, self.var_option)

        self.spin_width = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)
        self.spin_height = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)
        self.spin_x = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)
        self.spin_y = ttk.Spinbox(
            self.frame_custom, from_=0, command=self.event_spin_rect, width=4)

        self.button_choose_video.pack()
        self.entry_video_edit.pack()

        self.option_crop.pack()
        self.frame_control.grid(row=0, column=0)
        self.frame_custom.grid(row=0, column=1)

        self.frame_preview.grid(row=1, column=0, columnspan=2)
        self.canvas_video_before.grid(row=0,column=0, padx=10)
        self.canvas_video_after.grid(row=0, column=1, padx=10)
        label_video_before.grid(row=1, column=0, pady=5)
        label_video_after.grid(row=1, column=1, pady=5)

        self.spin_width.pack()
        self.spin_height.pack()
        self.spin_x.pack()
        self.spin_y.pack()

        self.button_save_video.grid(row=2, column=0, columnspan=2)
        self.frame_custom.grid_remove()

    def event_choose_video(self):
        filename_in = fdiag.askopenfilename(parent=self.master)
        if filename_in:
            self.var_video_edit.set(filename_in)
            self.extract_frame(filename_in)

    def event_save_video(self):
        filename_out = fdiag.asksaveasfilename(parent=self.master)
        if filename_out:
            print(filename_out)

    def check_ratio(self, w, h):
        if w/h/self.aspect == 1:
            return False
        return w/h

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
                self.image_input = Image.fromarray(frame)
                if not (ratio_input := self.check_ratio(self.width_input, self.height_input)):
                    self.width_imagetk = self.width_canvas
                    self.height_imagetk = self.height_canvas
                    self._mode.set(self.Mode.FIT)
                else:
                    if ratio_input > 1:
                        self.width_imagetk = self.width_canvas
                        self.height_imagetk = int(
                            self.width_canvas/ratio_input)
                        self._mode.set(self.Mode.WIDE)
                    else:
                        self.height_imagetk = self.height_canvas
                        self.width_imagetk = int(
                            self.height_canvas*ratio_input)
                        self._mode.set(self.Mode.TALL)

            self.prepare_canvas_before()
            self.prepare_canvas_after()
            self.set_options()
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
        self.imagetk_output = None
        self.image_croppped = self.canvas_video_after.create_image(
            self.width_canvas/2, self.height_canvas/2, image=self.imagetk_input)

    def update_canvas_after(self):
        posx_spin = int(self.spin_x.get())
        posy_spin = int(self.spin_y.get())
        width_spin = int(self.spin_width.get())
        height_spin = int(self.spin_height.get())
        x0 = posx_spin - width_spin/2
        y0 = self.height_input - posy_spin - height_spin/2
        x1 = x0 + width_spin
        y1 = y0 + height_spin
        image_output = self.image_input.crop((x0, y0, x1, y1))
        if not (ratio_output := self.check_ratio(width_spin, height_spin)):
            width_output = self.width_canvas
            height_output = self.height_canvas
        else:
            if ratio_output > self.aspect:
                width_output = self.width_canvas
                height_output = int(self.width_canvas/ratio_output)
            else:
                height_output = self.height_canvas
                width_output = int(self.height_canvas*ratio_output)
        self.imagetk_output = ImageTk.PhotoImage(image_output.resize((width_output, height_output)))
        self.canvas_video_after.itemconfig(self.image_croppped, image=self.imagetk_output)

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
            self.frame_custom.grid()
        else:
            self.frame_custom.grid_remove()
            if self._mode.get() == App.Mode.FIT:
                if option == App.OptionList.CENTER:
                    width_spin = self.width_input
                    height_spin = self.height_input
                    posx_spin = self.width_input/2
                    posy_spin = self.height_input/2
            if self._mode.get() == App.Mode.WIDE:
                if option == App.OptionList.CENTER:
                    height_spin = self.height_input
                    width_spin = self.height_input*self.aspect
                    posx_spin = self.width_input/2
                    posy_spin = self.height_input/2
                if option == App.OptionList.LEFT:
                    height_spin = self.height_input
                    width_spin = self.height_input*self.aspect
                    posx_spin = width_spin/2
                    posy_spin = self.height_input/2
                if option == App.OptionList.RIGHT:
                    height_spin = self.height_input
                    width_spin = self.height_input*self.aspect
                    posx_spin = self.width_input - width_spin/2
                    posy_spin = self.height_input/2
            if self._mode.get() == App.Mode.TALL:
                if option == App.OptionList.CENTER:
                    width_spin = self.width_input
                    height_spin = width_spin/self.aspect
                    posx_spin = self.width_input/2
                    posy_spin = self.height_input/2
                if option == App.OptionList.TOP:
                    width_spin = self.width_input
                    height_spin = width_spin/self.aspect
                    posx_spin = self.width_input/2
                    posy_spin = self.height_input - height_spin/2
                if option == App.OptionList.BOTTOM:
                    width_spin = self.width_input
                    height_spin = width_spin/self.aspect
                    posx_spin = self.width_input/2
                    posy_spin = height_spin/2
            self.spin_width.set(int(width_spin))
            self.spin_height.set(int(height_spin))
            self.spin_x.set(int(posx_spin))
            self.spin_y.set(int(posy_spin))
            self.event_spin_rect()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()
