import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
#import ffmpeg
import cv2
import random
#import youtube_dl as ydl
from PIL import ImageTk, Image
 
class App:

    class Mode:
        WIDE = 0
        TALL = 1
        FIT = 2

        def __init__(self):
            self._current = None
        
        def set(self, mode):
            assert mode in [d for d in self.__dict__ if not d.startswith("__")]
            self._current = mode

        def get_options(self):
            if self._current == self.WIDE:
                pass
            if self._current == self.FIT:
                pass
            if self._current == self.TALL:
                pass
        

    def __init__(self, master):
        self.master = master
        self.width = 320
        self.height = 180
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
        self.option_crop = ttk.OptionMenu(self.master, variable=self.var_option)



        self.button_choose_video.pack()
        self.entry_video_edit.pack()

        self.button_save_video.pack()

        self.canvas_video_before.pack()
        self.canvas_video_after.pack()

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
                def check_ratio(self, w, h):
                    if w*9/16/h == 1:
                        return False
                    return w/h

                self.image = Image.fromarray(frame)
                if not (ratio := self.check_ratio(self.w_in, self.h_in)):
                    self.image_in = ImageTk.PhotoImage(self.image.resize((self.width, self.height)))
                    self._mode.set(self.Mode.FIT)
                else:
                    if ratio > 1:
                        self.image_in = ImageTk.PhotoImage(self.image.resize((self.width, int(self.width/ratio))))
                        self._mode.set(self.Mode.WIDE)
                    else:
                        self.image_in = ImageTk.PhotoImage(self.image.resize((int(self.height*ratio), self.height)))
                        self._mode.set(self.Mode.TALL)
            self.canvas_video_before.create_image(self.width/2, self.height/2, image=self.image_in)
        finally:
            video.release()

    
    def set_options(self):
        options = []
        if self._mode == self.Mode.FIT:
            options = 
    

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    #ydl.YoutubeDL({}).download(["https://www.youtube.com/watch?v=Dpp_BSKAt4U"])

    root.mainloop()
