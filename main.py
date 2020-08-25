import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
import os
#import ffmpeg
import cv2
#import youtube_dl as ydl
from PIL import ImageTk, Image
 
class App:

    def __init__(self, master):
        self.master = master
        
        self.var_video_edit = tk.StringVar()
        self.entry_video_edit = ttk.Entry(self.master, textvariable=self.var_video_edit)
        self.button_choose_video = ttk.Button(self.master, text="Choose video..", command=self.event_choose_video)

        self.button_save_video = ttk.Button(self.master, text="Crop and Save video", command=self.event_save_video)

        self.canvas_video_before = tk.Canvas(self.master)
        self.canvas_video_after = tk.Canvas(self.master)

        self.button_choose_video.pack()
        self.entry_video_edit.pack()

        self.button_save_video.pack()

        self.canvas_video_before.pack()

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
            video.set(cv2.CAP_PROP_POS_FRAMES, int(frames_count/2))
            ok, frame = video.read()
            if ok:
                self.image = ImageTk.PhotoImage(Image.fromarray(frame))
            self.canvas_video_before.create_image(640, 480, image=self.image)
        finally:
            video.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    #ydl.YoutubeDL({}).download(["https://www.youtube.com/watch?v=668nUCeBHyY"])

    root.mainloop()
#https://www.pyimagesearch.com/2016/05/23/opencv-with-tkinter/
