# pylint: disable=attribute-defined-outside-init, C0114, C0115, C0116, invalid-name, unused-argument
from structs import *
from video import *
import tkinter.filedialog as fdiag
import tkinter as tk
import tkinter.ttk as ttk
from os import path, linesep
import cv2


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
        self.rect_croparea = None

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
            self.frame_text, height=1, width=50,
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
            self.master, text="Crop and Save videos", command=self.event_save_videos)

        self.var_option = tk.StringVar(value=OptionList.CENTER)
        self.option_crop = ttk.OptionMenu(self.frame_control, self.var_option)
        for op in OptionList().get():
            self.option_crop.children['!menu'].add_command(
                label=op, command=lambda x=op: self.event_change_option(x))

        self.notebook_custom = ttk.Notebook(self.frame_custom)
        self.tab_size = ttk.Frame(self.notebook_custom)
        self.tab_position = ttk.Frame(self.notebook_custom)

        self.var_check_aspect = tk.DoubleVar()
        self.check_aspect = ttk.Checkbutton(self.tab_size, onvalue=1.0, offvalue=0.0, text='Lock aspect', command=self.event_check_aspect, variable=self.var_check_aspect)

        label_width = ttk.Label(self.tab_size, text='Width:')
        label_height = ttk.Label(self.tab_size, text='Height:')
        label_x = ttk.Label(self.tab_position, text='X:')
        label_y = ttk.Label(self.tab_position, text='Y:')
        self.spin_width = ttk.Spinbox(
            self.tab_size, from_=0, command=self.event_spin_width, width=4)
        self.spin_width.bind("<Up>", lambda _: return None)
        self.spin_width.bind("<Down>", lambda _: return None)
        self.spin_height = ttk.Spinbox(
            self.tab_size, from_=0, command=self.event_spin_height, width=4)
        self.spin_height.bind("<Up>", lambda _: return None)
        self.spin_height.bind("<Down>", lambda _: return None)
        self.spin_x = ttk.Spinbox(
            self.tab_position, from_=0, command=self.event_spin_rect, width=4)
        self.spin_x.bind("<Up>", lambda _: return None)
        self.spin_x.bind("<Down>", lambda _: return None)
        self.spin_y = ttk.Spinbox(
            self.tab_position, from_=0, command=self.event_spin_rect, width=4)
        self.spin_y.bind("<Up>", lambda _: return None)
        self.spin_y.bind("<Down>", lambda _: return None)

        self.master.bind("<Key>", self.event_key)

        # frame main
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.frame_control.grid(row=0, column=0, sticky='nwse')
        self.frame_custom.grid(row=0, column=1, sticky='nse')
        self.frame_preview.grid(row=1, column=0, columnspan=2, sticky='nswe')
        self.button_save_video.grid(row=2, column=0, columnspan=2, sticky='we')

        # frame control
        self.frame_control.columnconfigure(1, weight=1)
        self.button_choose_video.grid(row=0, column=0)
        self.text_filepaths.grid(sticky='nwe')
        self.scroll_filepaths.grid(row=1, sticky='nwe')
        self.frame_text.grid(row=0, column=1, rowspan=3, sticky='ns')
        self.option_aspect.grid(row=1, column=0)
        self.option_crop.grid(row=2, column=0)

        # frame preview
        self.canvas_video_before.grid(row=0, column=0, padx=10, sticky='wens')
        self.canvas_video_after.grid(row=0, column=1, padx=10, sticky='nswe')
        label_video_before.grid(row=1, column=0, pady=5, sticky='n')
        label_video_after.grid(row=1, column=1, pady=5, sticky='n')

        # frame custom
        self.notebook_custom.add(self.tab_size, text="Size")
        self.notebook_custom.add(self.tab_position, text="Position")
        self.notebook_custom.pack(fill=tk.BOTH)
        label_width.grid(row=0, column=0)
        self.spin_width.grid(row=0, column=1)
        label_height.grid(row=1, column=0)
        self.spin_height.grid(row=1, column=1)
        self.check_aspect.grid(row=0,column=2,rowspan=2)
        label_x.grid(row=0, column=0)
        self.spin_x.grid(row=0, column=1)
        label_y.grid(row=1, column=0)
        self.spin_y.grid(row=1, column=1)

        self.frame_custom.grid_remove()

        self.prepare_canvas(aspect='16:9')

    def event_key(self, event):
        if self.videos:
            key = event.keysym
            if key=='Left':
                if self.notebook_custom.index('current') == 0:
                    self.spin_width.event_generate("<<Decrement>>")
                else:
                    self.spin_x.event_generate("<<Decrement>>")
            if key=='Right':
                if self.notebook_custom.index('current') == 0:
                    self.spin_width.event_generate("<<Increment>>")
                else:
                    self.spin_x.event_generate("<<Increment>>")
            if key=='Down':
                if self.notebook_custom.index('current') == 0:
                    self.spin_height.event_generate("<<Decrement>>")
                else:
                    self.spin_y.event_generate("<<Decrement>>")
            if key=='Up':
                if self.notebook_custom.index('current') == 0:
                    self.spin_height.event_generate("<<Increment>>")
                else:
                    self.spin_y.event_generate("<<Increment>>")

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
            self.frame_custom.grid()

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
            self.check_aspect.config(onvalue=self.aspect)
            self.var_check_aspect.set(self.aspect)
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
            rect_bbox = self._rect2canvas(rect_dim).get_bbox()
            if self.image_canvas_after and self.rect_croparea:
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
            v = self.videos[self.show_idx]
            h = v.get_size().height
            dim_new = self.set_spin(
                Dimensions(
                    pos_x=int(self.spin_x.get()),
                    pos_y=h - int(self.spin_y.get()),
                    width=int(self.spin_width.get()),
                    height=int(self.spin_height.get())))
            v.set_crop(
                option=OptionList.CUSTOM, crop_dim=dim_new)
            self.update_canvas()

    def _rect2canvas(self, rect_dim):
        video_pos = self.videos[self.show_idx].get_position()
        factor = self.videos[self.show_idx].get_resize_factor()
        pos_rect = rect_dim.get_position()
        return Dimensions(
            width=rect_dim.size.width*factor,
            height=rect_dim.size.height*factor,
            pos_x=pos_rect.x * factor + video_pos.x,
            pos_y=pos_rect.y * factor + video_pos.y)

    def set_spin(self, rect_dim):
        max_width, max_height = self.videos[self.show_idx].get_size()
        self.spin_height.set(int(rect_dim.size.height))
        self.spin_width.set(int(rect_dim.size.width))
        if (dx := rect_dim.position.x + rect_dim.size.width/2 - max_width) > 0:
            rect_dim.position.x -= dx
        self.spin_x.set(int(rect_dim.position.x))
        if (dy := rect_dim.position.y + rect_dim.size.height/2 - max_height) > 0:
            rect_dim.position.y -= dy
        self.spin_y.set(max_height - int(rect_dim.position.y))
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

    def event_check_aspect(self):
        if self.var_check_aspect.get():
            asp = int(self.spin_width.get())/int(self.spin_height.get())
            self.check_aspect.config(onvalue=asp)
            self.var_check_aspect.set(asp)

    def event_spin_height(self):
        if self.videos:
            if asp:=self.var_check_aspect.get():
                w = int(self.spin_width.get())
                h = int(self.spin_height.get())
                if h*asp > self.videos[self.show_idx].get_size().width:
                    self.spin_height.set(int(w/asp))
                else:
                    self.spin_width.set(int(h*asp))
            self.event_spin_rect()

    def event_spin_width(self):
        if self.videos:
            if asp:=self.var_check_aspect.get():
                w = int(self.spin_width.get())
                h = int(self.spin_height.get())
                if w/asp > self.videos[self.show_idx].get_size().height:
                    self.spin_width.set(int(h*asp))
                else:
                    self.spin_height.set(int(w/asp))
            self.event_spin_rect()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()
