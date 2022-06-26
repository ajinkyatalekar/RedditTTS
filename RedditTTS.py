import tkinter as tk
from tkinter import filedialog
import json
import os
import sys

if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(__file__))
    

class GUI:
    def __init__(self):
        print(path)
        self.root = tk.Tk()
        self.vidPath = path+"/src/video/vid.mp4"
        self.quality=1
        self.shorts=True

    def loop(self):
        self.frame1 = tk.Frame( width=800)
        self.frame1.pack()
        self.frame2 = tk.Frame( width=800)
        self.frame2.pack()

        tk.Label(self.frame2, text="Subreddit: ").pack()
        self.subreddit=tk.Entry(self.frame2, width=10)
        self.subreddit.insert(0, "askreddit")
        self.subreddit.pack()

        tk.Label(self.frame2, text="Number of Posts: ").pack()
        self.posts=tk.Entry(self.frame2, width=10)
        self.posts.insert(0, "1")
        self.posts.pack()

        tk.Label(self.frame2, text="Number of Comments: ").pack()
        self.comments=tk.Entry(self.frame2, width=10)
        self.comments.insert(0, "0")
        self.comments.pack()

        tk.Label(self.frame2, text="Skipping posts: ").pack()
        self.skipPosts=tk.Entry(self.frame2, width=10)
        self.skipPosts.insert(0, "0")
        self.skipPosts.pack()

        vidSelect = tk.Button(self.root, text="Change Background Video", command=self.selFile)
        vidSelect.pack()
        run = tk.Button(self.root, text="Run", command=self.startApp)
        run.pack()

        self.frame3 = tk.Frame(height=0, width=0)
        self.frame3.pack()

        self.updateLabels()
        self.root.mainloop()

    def selFile(self):
        for widget in self.frame1.winfo_children():
            widget.destroy()

        filename = filedialog.askopenfilename(initialdir="/", title="Change Background Video",
        filetypes=(("videos", "*.mp4"), ("all files", "*.*")))
        if filename != "":
            self.vidPath=filename
        
        self.updateLabels()
        
    def startApp(self):
        dat = {
            "subreddit":self.subreddit.get(), 
            "posts":int(self.posts.get()), 
            "comments":int(self.comments.get()), 
            "skipPosts":int(self.skipPosts.get()), 
            "quality":int(self.quality), 
            "shorts":self.shorts, 
            "vidPath": str(self.vidPath)
        }

        with open(path+"/src/dat.json", "w") as outfile:
            json.dump(dat, outfile)

        appPath = path+"/src/script.py"
        globals={"__file__": appPath,
            "__name__": "__main__",}
        with open(appPath, 'rb') as file:
            exec(compile(file.read(), appPath, 'exec'), globals, None)
        tk.Label(self.frame3, text="Done!").pack()

    def updateLabels(self):
        tk.Label(self.frame1, text="Current Video Path: "+self.vidPath).pack()
        
gui = GUI()
gui.loop()