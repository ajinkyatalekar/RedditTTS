## Imports
# Misc
import random
import os
from shutil import rmtree
# Reddit API
from praw import Reddit
# Screenshot Maker
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
# TTS, Audio Editor, and Video Editor
from gtts import gTTS
from pydub import AudioSegment
# Video Generator
import moviepy.editor as mp
from moviepy.video.fx.all import crop
from json import load
import sys

if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

class RedditTTS:
    # Auth and Setup
    def __init__(self):
        with open(app_path+'/config.json') as json_file:
            data = load(json_file)
        self.reddit = Reddit(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            user_agent=data['user_agent'],
            username=data['username'],
            password=data['password']
        )
        self.subs = []

    # Get Submissions from specified subreddit
    def getSubmissions(self, subreddit='askreddit', posts=3, comments=0, skipPosts=0, u18=False):
        exists = True
        try:
            self.reddit.subreddits.search_by_name(subreddit, exact=True)
        except:
            exists = False
            return

        print("Subreddit Exists; Fetching posts")

        submissions = iter(self.reddit.subreddit(subreddit).hot(limit=posts))
        for i in range(skipPosts):
            next(submissions)

        for submission in submissions:
            if (u18 and submission.over_18 == True):
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

    def genImages(self):
        options = webdriver.ChromeOptions()
        # Using Custom Profile with Reddit account logged in to bypass NSFW popups -> Change <user> to your name
        # options.add_argument(r"--user-data-dir=C:/Users/<user>/AppData/Local/Google/Chrome/User Data")
        # options.add_argument(r'--profile-directory="Default"')
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

    def genAudio(self):
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

    def genVideo(self, quality=1, shorts=False, vidPath=app_path+"/video/vid.mp4"):
        for sub in self.subs:
            videoclip = mp.VideoFileClip(vidPath)
            videoclip = videoclip.resize(quality)
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
            sound2 = AudioSegment.from_file(app_path+"/audio/" + os.listdir(app_path+"/audio")[random.randint(0,len(os.listdir("audio"))-1)], format="mp3")
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

            # if (shorts):
            #     final.write_videofile(app_path+'/../out/' + sub['id'] + '/' + sub['id'] + '_s.mp4')
            # else:
            #     final.write_videofile(app_path+'/../out/' + sub['id'] + '/' + sub['id'] + '.mp4')

            # f = open(app_path+'/../out/' + sub['id'] + "/dat" + ".txt", "a")
            # f.write("Title: " + sub['title']
            # + "\nSubreddit: " + sub['subreddit'])
            # f.close()

            rmtree(app_path+"/temp/" + sub['id'])
        rmtree(app_path+"/temp")

def run(subreddit, posts, comments, skipPosts, quality, shorts, vidPath):
    rTTS=RedditTTS()
    rTTS.getSubmissions(subreddit=subreddit, posts=posts, comments=comments, skipPosts=skipPosts)
    rTTS.genImages()
    rTTS.genAudio()
    rTTS.genVideo(quality=quality, shorts=shorts, vidPath=vidPath)

with open(app_path+'/dat.json') as json_file:
    data = load(json_file)

run(data["subreddit"],data["posts"],data["comments"],data["skipPosts"],data["quality"],data["shorts"],data["vidPath"])