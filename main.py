import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
import os
import youtube_dl as ydl

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

    def event_choose_video(self):
        f = fdiag.askopenfilename(parent=self.master)
        if f:
            self.var_video_edit.set(f)

    def event_save_video(self):
        f = fdiag.asksaveasfilename(parent=self.master)
        if f:
            print(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    with ydl.YouTubeDL({}) as y:
        y.download("https://www.youtube.com/watch?v=668nUCeBHyY")

    root.mainloop()
