## Imports
# Misc
import random
import os
# Reddit API
import praw
# Screenshot Maker
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
# TTS, Audio Editor, and Video Editor
from gtts import gTTS
from pydub import AudioSegment
import moviepy.editor as mp
import config

class RedditTTS:
    # Auth and Setup
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
            username=config.username,
            password=config.password
        )
        self.subs = []

    # Get Submissions from specified subreddit
    def getSubmissions(self, subreddit='askreddit', posts=3, comments=0, skipPosts=0, u18=False):
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
                'comment': c
            })

    def genImages(self):
        options = webdriver.ChromeOptions()
        # Using Custom Profile to bypass NSFW popups
        # options.add_argument(r"--user-data-dir=C:/Users/ajink/AppData/Local/Google/Chrome/User Data")
        # options.add_argument(r'--profile-directory="Default"')
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        for sub in self.subs:
            driver.get('https://www.reddit.com/'+sub['id'])

            path = 'temp/' + sub['id']
            if not os.path.exists(path):
                os.makedirs(path)

            # element = driver.find_element_by_class_name("Post")
            element = driver.find_element(by=By.CLASS_NAME, value='Post')
            element.screenshot('temp/' + sub['id'] + '/title.png')

            i = 0
            for comment in sub['comment']:
                driver.get(comment['link'])
                element = driver.find_element(by=By.CLASS_NAME, value='Comment')
                element.screenshot('temp/' + sub['id'] + '/' + str(i) + 'com.png')
                i = i+1
        driver.quit()

    def genAudio(self):
        for sub in self.subs:
            # TTS
            audioString = ''
            audioString += sub['title'] + "."
            audioString += sub['selftext'] + "."

            aud = gTTS(text=audioString, lang='en', slow=False, tld='ca')

            path = 'temp/' + sub['id']
            if not os.path.exists(path):
                os.makedirs(path)

            aud.save('temp/' + sub['id'] + '/tts.mp3')

            i = 0
            for comment in sub['comment']:
                aud = gTTS(text=comment['body']+'.', lang='en', slow=False, tld='ca')
                aud.save('temp/' + sub['id'] + '/' + str(i) + 'com.mp3')
                i = i+1

    def genVideo(self, quality=1):
        for sub in self.subs:
            videoclip = mp.VideoFileClip("src/video/bgFull.mp4")
            videoclip = videoclip.resize(quality)
            audioclip = mp.AudioFileClip('temp/' + sub['id'] + '/tts.mp3')

            titleVid = (mp.ImageClip('temp/' + sub['id'] + '/title.png')
                .set_duration(audioclip.duration)
                .resize(width=640*quality)
                .set_pos(("center","center"))
            )

            for i in range(len(sub['comment'])):
                aud = mp.AudioFileClip('temp/' + sub['id'] + '/' + str(i) + 'com.mp3')
                vid = (mp.ImageClip('temp/' + sub['id'] + '/' + str(i) + 'com.png')
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
            
            audioclip.write_audiofile('temp/' + sub['id'] + '/fintts.mp3')

            # Layer BG Music
            sound1 = AudioSegment.from_file("temp/" + sub['id'] + "/fintts.mp3", format="mp3")
            sound2 = AudioSegment.from_file("src/audio/bg" + str(random.randint(1,2)) + ".mp3", format="mp3")
            overlay = sound1.overlay(sound2, position=0, loop=True)
            overlay.export("temp/" + sub['id'] + "/finalAudio.mp3", format="mp3")
            finaud = mp.AudioFileClip('temp/' + sub['id'] + '/finalAudio.mp3')
            
            videoclip.audio = finaud

            path = 'out/' + sub['id']
            if not os.path.exists(path):
                os.makedirs(path)

            final = mp.CompositeVideoClip([videoclip, titleVid])
            final.write_videofile('out/' + sub['id'] + '/' + sub['id'] + '.mp4')

            f = open('out/' + sub['id'] + "/ytMeta" + ".txt", "a")
            f.write(sub['title'])
            f.close()
        
    def printSubmissions(self):
        for i in self.subs:
            print(i['title'], i['selftext'])

## Executing Everything
rTTS=RedditTTS()
rTTS.getSubmissions(subreddit='jokes', posts=5, comments=3, skipPosts=2)
rTTS.printSubmissions()
rTTS.genImages()
rTTS.genAudio()
rTTS.genVideo(quality=1)