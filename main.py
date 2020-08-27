import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
import cv2
import random
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
                self._options[1:1] = [App.OptionList.LEFT, App.OptionList.RIGHT]
            if self._current == self.TALL:
                self._options[1:1] = [App.OptionList.TOP, App.OptionList.BOTTOM]
        
        def get_options(self):
            if self._current is None:
                return None
            return self._options

        def get(self):
            return self._current

    def __init__(self, master):
        self.master = master
        self.width = 320
        self.height = 180
        self.aspect = 16/9
        self._mode = self.Mode()

        self.ASPECTS = [
            '16:9',
            '16:10',
            '4:3'
        ]
        
        self.var_video_edit = tk.StringVar()
        self.entry_video_edit = ttk.Entry(self.master, textvariable=self.var_video_edit)
        self.button_choose_video = ttk.Button(self.master, text="Choose video..", command=self.event_choose_video)

        self.button_save_video = ttk.Button(self.master, text="Crop and Save video", command=self.event_save_video)

        self.canvas_video_before = tk.Canvas(self.master, bg='black', width=self.width, height=self.height, relief=tk.SUNKEN)
        self.canvas_video_after = tk.Canvas(self.master, bg='black', width=self.width, height=self.height, relief=tk.SUNKEN)


        self.var_option = tk.StringVar()
        self.var_option.trace("w", self.event_option_change)
        self.option_crop = ttk.OptionMenu(self.master, self.var_option)



        self.button_choose_video.pack()
        self.entry_video_edit.pack()

        self.button_save_video.pack()

        self.canvas_video_before.pack()
        self.canvas_video_after.pack()

        self.option_crop.pack()

    def event_choose_video(self):
        f = fdiag.askopenfilename(parent=self.master)
        if f:
            self.var_video_edit.set(f)
            self.extract_frame(f)

    def event_save_video(self):
        f = fdiag.asksaveasfilename(parent=self.master)
        if f:
            print(f)

    def extract_frame(self, path_video):
        video = cv2.VideoCapture(path_video, 0)
        try:
            frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.w_in  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.h_in = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video.set(cv2.CAP_PROP_POS_FRAMES, random.randrange(int(frames_count/2)))
            ok, frame = video.read()
            if ok:
                def check_ratio(w, h):
                    if w*9/16/h == 1:
                        return False
                    return w/h
                self.ratio_in = check_ratio(self.w_in, self.h_in)
                self.image = Image.fromarray(frame)
                if not self.ratio_in:
                    self.image_in = ImageTk.PhotoImage(self.image.resize((self.width, self.height)))
                    self._mode.set(self.Mode.FIT)
                else:
                    if self.ratio_in > 1:
                        self.image_in = ImageTk.PhotoImage(self.image.resize((self.width, int(self.width/self.ratio_in))))
                        self._mode.set(self.Mode.WIDE)
                    else:
                        self.image_in = ImageTk.PhotoImage(self.image.resize((int(self.height*self.ratio_in), self.height)))
                        self._mode.set(self.Mode.TALL)
            self.canvas_video_before.create_image(self.width/2, self.height/2, image=self.image_in)
            self.rect_croparea = self.canvas_video_before.create_rectangle(0,0,0,0, fill='', outline='red', width=5)
            self.set_options()
        finally:
            video.release()

    
    def set_options(self):
        self.option_crop.children['!menu'].delete(0,'end')
        options = self._mode.get_options()
        for op in options:
            self.option_crop.children['!menu'].add_command(label=op, command=lambda x=op : self.var_option.set(x))
        self.var_option.set(options[0])

    def event_option_change(self, *args):
        if (option := self.var_option.get()) == App.OptionList.CUSTOM:
            pass
        else:
            if self._mode.get() == App.Mode.FIT:
                if option == App.OptionList.CENTER:
                    self.x_crop = 0
                    self.y_crop = 0
                    self.w_crop = self.width
                    self.h_crop = self.height
            if self._mode.get() == App.Mode.WIDE:
                if option == App.OptionList.CENTER:
                    self.h_crop = self.width/self.ratio_in
                    self.w_crop = self.h_crop*self.aspect
                    self.x_crop = (self.width - self.w_crop)/2
                    self.y_crop = (self.height - self.h_crop)/2
                if option == App.OptionList.LEFT:
                    self.h_crop = self.width/self.ratio_in
                    self.w_crop = self.h_crop*self.aspect
                    self.x_crop = 0
                    self.y_crop = (self.height - self.h_crop)/2
                if option == App.OptionList.RIGHT:
                    self.h_crop = self.width/self.ratio_in
                    self.w_crop = self.h_crop*self.aspect
                    self.x_crop = self.width - self.w_crop
                    self.y_crop = (self.height - self.h_crop)/2
            if self._mode.get() == App.Mode.TALL:
                if option == App.OptionList.CENTER:
                    self.w_crop = self.height*self.ratio_in
                    self.h_crop = self.w_crop/self.aspect
                    self.x_crop = (self.width - self.w_crop)/2
                    self.y_crop = (self.height - self.h_crop)/2
                if option == App.OptionList.TOP:
                    self.w_crop = self.height*self.ratio_in
                    self.h_crop = self.w_crop/self.aspect
                    self.x_crop = (self.width - self.w_crop)/2
                    self.y_crop = 0
                if option == App.OptionList.BOTTOM:
                    self.w_crop = self.height*self.ratio_in
                    self.h_crop = self.w_crop/self.aspect
                    self.x_crop = (self.width - self.w_crop)/2
                    self.y_crop = self.height - self.h_crop
            self.canvas_video_before.coords(self.rect_croparea, self.x_crop, self.y_crop, self.x_crop + self.w_crop, self.y_crop + self.h_crop)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()
