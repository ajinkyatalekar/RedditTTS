import src.lib.tkinter as tk
from src.lib.tkinter import filedialog
import src.lib.json as json
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
        self.vidPath = "null"
        self.quality=1
        self.shorts=True
        with open(path+'/src/config.json') as json_file:
            self.config = json.load(json_file)

    def loop(self):

        self.frame2 = tk.Frame( width=800)
        self.frame2.pack()
        self.frame1 = tk.Frame( width=800)
        self.frame1.pack()

        tk.Label(self.frame2, text="Reddit Client ID: ").pack()
        self.client_id=tk.Entry(self.frame2, width=30)
        self.client_id.insert(0, self.config['client_id'])
        self.client_id.pack()

        tk.Label(self.frame2, text="Reddit Client Secret: ").pack()
        self.client_secret=tk.Entry(self.frame2, width=30)
        self.client_secret.insert(0, self.config['client_secret'])
        self.client_secret.pack()

        tk.Label(self.frame2, text="(If you don't have a Reddit Client, you can get it here: https://www.reddit.com/prefs/apps)").pack()

        tk.Label(self.frame2, text="Subreddit: ").pack()
        self.subreddit=tk.Entry(self.frame2, width=30)
        self.subreddit.insert(0, "askreddit")
        self.subreddit.pack()

        tk.Label(self.frame2, text="Number of Posts: ").pack()
        self.posts=tk.Entry(self.frame2, width=30)
        self.posts.insert(0, "1")
        self.posts.pack()

        tk.Label(self.frame2, text="Number of Comments: ").pack()
        self.comments=tk.Entry(self.frame2, width=30)
        self.comments.insert(0, "0")
        self.comments.pack()

        tk.Label(self.frame2, text="Skipping posts: ").pack()
        self.skipPosts=tk.Entry(self.frame2, width=30)
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

        config = {
            "client_id":self.client_id.get(),
            "client_secret":self.client_secret.get()
        }
        with open(path+"/src/config.json", "w") as outfile:
            json.dump(config, outfile)

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