# Misc
import json
import random
import os
import sys
import threading
from src.lib.shutil import rmtree
# GUI
import src.lib.tkinter as tk
from src.lib.tkinter import filedialog
# Reddit API
from src.lib.praw import Reddit
# Screenshot Maker
from src.lib.selenium import webdriver
from src.lib.selenium.webdriver.common.by import By
from src.lib.webdriver_manager.chrome import ChromeDriverManager
# TTS, Audio Editor, and Video Editor
from src.lib.gtts import gTTS
from src.lib.pydub import AudioSegment
# Video Generator
import src.lib.moviepy.editor as mp
from src.lib.moviepy.video.fx.all import crop
from src.lib.json import load

# Get current file path
path = os.path.dirname(os.path.abspath(__file__))
app_path = path+'/src'

# Console log
class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass

# GUI Code
class GUI:

    def __init__(self):
        print("Running GUI.")
        self.root = tk.Tk()
        self.vidPath = "null"
        self.quality=1
        self.shorts=False
        with open(path+'/src/config.json') as json_file:
            self.config = json.load(json_file)

    def loop(self):
        self.root.title('RedditTTS v1.0')
        self.root.state('zoomed')
        self.frame1 = tk.Frame(width=800)
        self.frame1.pack()
        self.frame3 = tk.Frame( width=800)
        self.frame3.pack()
        tk.Label(self.frame1, text="RedditTTS", font=("Arial", 20)).pack()
        tk.Label(self.frame1, text="IMPORTANT: The app skips NSFW posts. So you might not get a video if post is NSFW...").pack()
        tk.Label(self.frame1, text="Reddit Client ID: ").pack()
        self.client_id=tk.Entry(self.frame1, width=30)
        self.client_id.insert(0, self.config['client_id'])
        self.client_id.pack()

        tk.Label(self.frame1, text="Reddit Client Secret: ").pack()
        self.client_secret=tk.Entry(self.frame1, width=30)
        self.client_secret.insert(0, self.config['client_secret'])
        self.client_secret.pack()

        tk.Label(self.frame1, text="(If you don't have a Reddit app, you can get it here: https://www.reddit.com/prefs/apps)").pack()

        tk.Label(self.frame1, text="Subreddit: ").pack()
        self.subreddit=tk.Entry(self.frame1, width=30)
        self.subreddit.insert(0, "askreddit")
        self.subreddit.pack()

        tk.Label(self.frame1, text="Number of Posts: ").pack()
        self.posts=tk.Entry(self.frame1, width=30)
        self.posts.insert(0, "1")
        self.posts.pack()

        tk.Label(self.frame1, text="Number of Comments: ").pack()
        self.comments=tk.Entry(self.frame1, width=30)
        self.comments.insert(0, "0")
        self.comments.pack()

        tk.Label(self.frame1, text="Skipping posts: ").pack()
        self.skipPosts=tk.Entry(self.frame1, width=30)
        self.skipPosts.insert(0, "0")
        self.skipPosts.pack()

        vidSelect = tk.Button(self.root, text="Change Background Video", command=self.selFile)
        tk.Label(self.root, text="If video path is 'null', a video with black background will be made.").pack()
        vidSelect.pack()
        run = tk.Button(self.root, text="Run", command=self.startAppPre, fg="white", bg="green", padx=20, pady=5)
        run.pack()

        self.frame2 = tk.Frame(height=100, width=50)
        self.frame2.pack()
        # Log
        t = tk.Text(self.frame2, width=100, height=50, bg="black", fg="white")
        t.pack()
        pl = PrintLogger(t)
        sys.stdout = pl
        print("Progress will be logged here.")

        self.updateLabels()
        self.root.mainloop()

    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)

    def selFile(self):
        for widget in self.frame3.winfo_children():
            widget.destroy()

        filename = filedialog.askopenfilename(initialdir="/", title="Change Background Video",
        filetypes=(("videos", "*.mp4"), ("all files", "*.*")))
        if filename != "":
            self.vidPath=filename
        
        self.updateLabels()
        
    def startAppPre(self):
        self.refresh()
        threading.Thread(target=self.startApp).start()

    def startApp(self):
        # Main
        dat = {
            "subreddit":self.subreddit.get(), 
            "posts":int(self.posts.get()), 
            "comments":int(self.comments.get()), 
            "skipPosts":int(self.skipPosts.get()), 
            "quality":int(self.quality), 
            "shorts":self.shorts, 
            "vidPath": str(self.vidPath),
            "u18": True
        }
        with open(path+"/src/dat.json", "w") as outfile:
            json.dump(dat, outfile)

        config = {
            "client_id":self.client_id.get(),
            "client_secret":self.client_secret.get()
        }
        with open(path+"/src/config.json", "w") as outfile:
            json.dump(config, outfile)

        rTTS = RedditTTS()
        rTTS.run()
        tk.Label(self.frame2, text="Done! see 'out/' folder for the final video.").pack()

    def updateLabels(self):
        tk.Label(self.frame3, text="Current Background Video Path: "+self.vidPath).pack()

# Video Generator Code
class RedditTTS:

    # Auth and Setup
    def __init__(self):
        print("Logging in Reddit...")
        with open(app_path+'/config.json') as json_file:
            data = load(json_file)
        self.reddit = Reddit(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            user_agent="rTTS 2.0"
        )
        self.subs = []
        print("Logged in successfully!")

    # Running the entire thing
    def run(self):
        with open(app_path+'/dat.json') as json_file:
            data = load(json_file)
        self.getSubmissions(subreddit=data["subreddit"], posts=data["posts"], comments=data["comments"], skipPosts=data["skipPosts"], u18 = data["u18"])
        self.genImages()
        self.genAudio()
        self.genVideo(quality=data["quality"], shorts=data["shorts"], vidPath=data["vidPath"])

    # Get Submissions from specified subreddit
    def getSubmissions(self, subreddit='askreddit', posts=3, comments=0, skipPosts=0, u18=True):
        print("Checking if subreddit exists...")
        exists = True
        try:
            self.reddit.subreddits.search_by_name(subreddit, exact=True)
        except:
            exists = False
            return

        print("Subreddit Exists! Fetching posts...")

        submissions = iter(self.reddit.subreddit(subreddit).hot(limit=posts))
        for i in range(skipPosts):
            next(submissions)

        for submission in submissions:
            if (u18 and submission.over_18 == True):
                print("NSFW post detected! Skipping this post.")
                continue
            
            c = []
            post = self.reddit.submission(submission.id)
            for comment in post.comments[0:comments]:
                c.append({
                    'body': comment.body,
                    'link': 'https://www.reddit.com' + comment.permalink,
                })

            self.subs.append({
                'title': submission.title,
                'selftext': submission.selftext,
                'id': submission.id,
                'subreddit': subreddit,
                'comment': c
            })
            print("Fetching posts complete!")

    def genImages(self):
        print("Generating images...")
        options = webdriver.ChromeOptions()
        # Using Custom Profile with Reddit account logged in to bypass NSFW popups -> Change <user> to your name
        # options.add_argument(r"--user-data-dir=C:/Users/<user>/AppData/Local/Google/Chrome/User Data")
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        for sub in self.subs:
            driver.get('https://www.reddit.com/'+sub['id'])

            path = app_path+'/temp/' + sub['id']
            if not os.path.exists(path):
                os.makedirs(path)

            # element = driver.find_element_by_class_name("Post")
            element = driver.find_element(by=By.CLASS_NAME, value='Post')
            element.screenshot(app_path+'/temp/' + sub['id'] + '/title.png')

            i = 0
            for comment in sub['comment']:
                driver.get(comment['link'])
                element = driver.find_element(by=By.CLASS_NAME, value='Comment')
                element.screenshot(app_path+'/temp/' + sub['id'] + '/' + str(i) + 'com.png')
                i = i+1
        driver.quit()
        print("Successfully generated images!")

    def genAudio(self):
        print("Generating audio...")
        for sub in self.subs:
            # TTS
            audioString = ''
            audioString += sub['title'] + "."
            audioString += sub['selftext'] + "."

            aud = gTTS(text=audioString, lang='en', slow=False, tld='ca')

            path = app_path+'/temp/' + sub['id']
            if not os.path.exists(path):
                os.makedirs(path)

            aud.save(app_path+'/temp/' + sub['id'] + '/tts.mp3')

            i = 0
            for comment in sub['comment']:
                aud = gTTS(text=comment['body']+'.', lang='en', slow=False, tld='ca')
                aud.save(app_path+'/temp/' + sub['id'] + '/' + str(i) + 'com.mp3')
                i = i+1
            print("Successfully generated audio!")

    def genVideo(self, quality=1, shorts=False, vidPath=app_path+"/video/vid.mp4"):
        print("Generating video...")
        for sub in self.subs:
            if (vidPath == "null"):
                videoclip = mp.VideoFileClip("src/video/color.mp4")
            else:
                videoclip = mp.VideoFileClip(vidPath)

            # videoclip = videoclip.resize(quality)
            audioclip = mp.AudioFileClip(app_path+'/temp/' + sub['id'] + '/tts.mp3')

            titleVid = (mp.ImageClip(app_path+'/temp/' + sub['id'] + '/title.png')
                .set_duration(audioclip.duration)
                .resize(width=640*quality)
                .set_pos(("center","center"))
            )

            for i in range(len(sub['comment'])):
                aud = mp.AudioFileClip(app_path+'/temp/' + sub['id'] + '/' + str(i) + 'com.mp3')
                vid = (mp.ImageClip(app_path+'/temp/' + sub['id'] + '/' + str(i) + 'com.png')
                    .set_duration(aud.duration)
                    .resize(width=640*quality)
                    .set_pos(("center","center"))
                )

                audioclip = mp.concatenate_audioclips([audioclip, aud])
                titleVid = mp.concatenate_videoclips([titleVid, vid])

            titleVid = titleVid.set_pos(("center","center"))
            start = random.randint(0, int(videoclip.duration-titleVid.duration))
            end = start + titleVid.duration
            videoclip = videoclip.subclip(start, end)
            
            audioclip.write_audiofile(app_path+'/temp/' + sub['id'] + '/fintts.mp3')

            # Layer BG Music
            sound1 = AudioSegment.from_file(app_path+"/temp/" + sub['id'] + "/fintts.mp3", format="mp3")
            sound2 = AudioSegment.from_file(app_path+"/audio/" + os.listdir(app_path+"/audio")[random.randint(0,len(os.listdir(app_path+"/audio"))-1)], format="mp3")
            overlay = sound1.overlay(sound2, position=0, loop=True)
            overlay.export(app_path+"/temp/" + sub['id'] + "/finalAudio.mp3", format="mp3")


            outPath = os.path.normpath(app_path + os.sep + os.pardir)
            path = outPath+'/out/' + sub['id']
            if not os.path.exists(path):
                os.makedirs(path)

            final = mp.CompositeVideoClip([videoclip, titleVid])

            if (shorts):
                w,h = final.size
                final = crop(final,  x_center=w/2 , y_center=h/2, width=w/2, height=h)

            final = final.set_audio(mp.AudioFileClip(app_path+'/temp/' + sub['id'] + '/finalAudio.mp3'))

            if (shorts):
                final.write_videofile(outPath+'/out/' + sub['id'] + '/' + sub['id'] + '_s.mp4')
            else:
                final.write_videofile(outPath+'/out/' + sub['id'] + '/' + sub['id'] + '.mp4')

            f = open(outPath+'/out/' + sub['id'] + "/info" + ".txt", "a")
            f.write("Title: " + sub['title']
            + "\nSubreddit: " + sub['subreddit'])
            f.close()

            rmtree(app_path+"/temp/" + sub['id'])
        path = app_path+'/temp'
        if os.path.exists(path):
            rmtree(app_path+"/temp")
        print("Done! see 'out/' folder for the final video.")

gui = GUI()
gui.loop()