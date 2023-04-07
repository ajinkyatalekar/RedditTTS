from shutil import rmtree
from lib.moviepy.editor import *
import math
from lib.gtts import gTTS
import json
import re
from lib.moviepy.audio.fx.volumex import volumex
from lib.moviepy.video.fx.resize import resize
from lib.moviepy.video.fx.loop import loop

class VideoGenerator:
    
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu|me)"
    digits = "([0-9])"
    def split_into_sentences(self,text):
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(self.prefixes,"\\1<prd>",text)
        text = re.sub(self.websites,"<prd>\\1",text)
        text = re.sub(self.digits + "[.]" + self.digits,"\\1<prd>\\2",text)
        if "..." in text: text = text.replace("...","<prd><prd><prd>")
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + self.alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(self.acronyms+" "+self.starters,"\\1<stop> \\2",text)
        text = re.sub(self.alphabets + "[.]" + self.alphabets + "[.]" + self.alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(self.alphabets + "[.]" + self.alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+self.suffixes+"[.] "+self.starters," \\1<stop> \\2",text)
        text = re.sub(" "+self.suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + self.alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]

        if (len(sentences)==0):
            sentences.append(text)
        return sentences
    
    def cleanArray(self,arr):
        newArr = []
        for i in range(len(arr)):
            if (re.search('[a-zA-Z0-9]', arr[i])!=None):
                newArr.append(arr[i])
        return newArr
        
        
    def generateVideo(self, post, comments, bg_path=""):

        with open("post_data.json") as f:
            file = json.load(f)
            subreddit_name = file["subreddit"]

        selftext_exists = True
        if len(post.selftext) == 0:
            selftext_exists = False


        # Audio Generation
        if not os.path.exists("temp/audio"):
            os.makedirs("temp/audio")
        if not os.path.exists("out"):
            os.makedirs("out")

        post_title_array = self.split_into_sentences(post.title)
        post_title_array = self.cleanArray(post_title_array)
        for i in range(len(post_title_array)):
            self.generateAudio(post_title_array[i], "temp/audio/post_title_"+str(i)+".mp3")

        if (selftext_exists):
            post_selftext_array = self.split_into_sentences(post.selftext)
            post_selftext_array = self.cleanArray(post_selftext_array)
            for i in range(len(post_selftext_array)):
                self.generateAudio(post_selftext_array[i], "temp/audio/post_selftext_"+str(i)+".mp3")

        audio_speed_mult = 1
        
        # Video Generation
        final_video_clips = []
        
        header_margin_height = 50
        post_title_height = math.ceil(len(post.title)/98)*35
        post_selftext_height = math.ceil(len(post.selftext)/138)*25+30
        footer_margin_height = 50
        post_total_height = header_margin_height+post_title_height+post_selftext_height+footer_margin_height
        post_width = 1920

        background = ColorClip(size =(post_width, post_total_height), color =[24, 24, 24])

        curr_h = 30
        curr_w = 100

        upvote_icon = ImageClip('src/upvote.png').resize(0.3).set_position((20,curr_h))
        score = post.score
        if (score < 1000):
            score = str(score)
            left = 18
        else:
            score = int(score/1000)
            score = str(score)+"k"
            left = 26
        like_num = TextClip(score, fontsize=20, color="white", font="Verdana-Bold").set_position((left,curr_h+36))
        downvote_icon = ImageClip('src/downvote.png').resize(0.3).set_position((20,curr_h+62))

        header = TextClip("r/"+subreddit_name, fontsize=20, color="white", font="Verdana-Bold").set_position((curr_w,curr_h))
        header2 = TextClip(" ● Posted by u/" + post.author.name, fontsize=20, color="RGB(165, 164, 164)", font="Verdana").set_position((curr_w+header.size[0],curr_h))
        
        
        
        post_array = []
        completed = ""
        for i in range(len(post_title_array)):
            post_title_audio = AudioFileClip("temp/audio/post_title_"+str(i)+".mp3").fx(vfx.speedx, audio_speed_mult)
            dur = post_title_audio.duration

            completed+=post_title_array[i].strip()+" "
            post_title = TextClip(completed, fontsize=35, color="white", font="Verdana", size=(post_width-200, post_total_height), method="caption", align="North-West").set_position((curr_w,curr_h+40))
                
            upvote_icon = upvote_icon.set_duration(dur)
            like_num = like_num.set_duration(dur)
            downvote_icon = downvote_icon.set_duration(dur)
            background = background.set_duration(dur)
            header = header.set_duration(dur)
            header2 = header2.set_duration(dur)
            post_title = post_title.set_duration(dur)

            post_clip = CompositeVideoClip([background, header, header2, post_title, upvote_icon, downvote_icon, like_num])
            post_clip = post_clip.set_audio(post_title_audio)

            post_array.append(post_clip)
        
        curr_h += 40+25+post_title_height

        completed = ""
        if (selftext_exists):
            for i in range(len(post_selftext_array)):
                post_selftext_audio = AudioFileClip("temp/audio/post_selftext_"+str(i)+".mp3").fx(vfx.speedx, audio_speed_mult)
                dur = post_selftext_audio.duration

                completed+=post_selftext_array[i].strip() + " "
                post_selftext = TextClip(completed, fontsize=25, color="white", font="Verdana", size=(post_width-200, post_total_height), method="caption", align="North-West").set_position((curr_w,curr_h))
                    
                upvote_icon = upvote_icon.set_duration(dur)
                like_num = like_num.set_duration(dur)
                downvote_icon = downvote_icon.set_duration(dur)
                background = background.set_duration(dur)
                header = header.set_duration(dur)
                header2 = header2.set_duration(dur)
                post_title = post_title.set_duration(dur)
                post_selftext = post_selftext.set_duration(dur)

                post_clip = CompositeVideoClip([background, header, header2, post_title, upvote_icon, downvote_icon, like_num, post_selftext])
                post_clip = post_clip.set_audio(post_selftext_audio)

                post_array.append(post_clip)
        
        post_final_clip = concatenate_videoclips(post_array)

        final_video_clips.append(post_final_clip)

        for comment_num in range(len(comments)):
            final_video_clips.append(self.comment_video(comments[comment_num]))


        if (bg_path==""):
            abs_background = ColorClip(size =(1920, 1080), color =[5, 5, 5])

            for clip_num in range(len(final_video_clips)):
                final_video_clips[clip_num] = CompositeVideoClip([abs_background.set_duration(final_video_clips[clip_num].duration), final_video_clips[clip_num].set_position("center", "center")])

            final = concatenate_videoclips(final_video_clips, method="compose")
        else:
            tot_dur = 0
            for i in range(len(final_video_clips)):
                tot_dur+=final_video_clips[i].duration

            dur = 0

            final = loop(VideoFileClip("bg_vid.mp4"), duration=tot_dur)
            for i in range(len(final_video_clips)):
                final = CompositeVideoClip([final, resize(final_video_clips[i], width=final.size[0]*0.9).set_position("center", "center").set_start(dur)])
                dur+=final_video_clips[i].duration

            final = final.set_end(dur)


        background_audio = AudioFileClip("src/bg1.mp3").set_duration(final.duration)
        background_audio = volumex(background_audio, 0.2)
        final.audio = CompositeAudioClip([final.audio, background_audio])

        final.write_videofile('out/out.mp4',fps=24)

        if os.path.exists("temp/audio"):
            rmtree("temp/audio")

    def comment_video(self, comment, get_frame=False, path=""):
        if not os.path.exists("temp/audio"):
            os.makedirs("temp/audio")
        if not os.path.exists("temp/img"):
            os.makedirs("temp/img")
        if not os.path.exists("out"):
            os.makedirs("out")
            
        comments = [comment]
        comment_num = 0
        
        comments_array = []
        for j in range(len(comments)):
            comment_array = self.split_into_sentences(comments[j].body)
            comment_array = self.cleanArray(comment_array)
            comments_array.append(comment_array)
            for i in range(len(comment_array)):
                self.generateAudio(comment_array[i], "temp/audio/comment_"+str(j)+"_"+str(i)+".mp3")

        comment_vid_arr = []
        
        comment_width = 1920
        comment_height= 67 + math.ceil(len(comments[comment_num].body)/150)*25 + 20 + 50
        curr_h = 30
        curr_w = 60


        bg = ColorClip(size =(comment_width, comment_height), color =[24, 24, 24])

        avatar = ImageClip('src/avatar.png').resize(0.23).set_position([12, curr_h-6])

        comment_title = TextClip(comments[comment_num].author.name, fontsize=20, color="white", font="Verdana-Bold").set_position([curr_w, curr_h+1])
        comment_title2 = TextClip(" ● 6 hr. ago", fontsize=20, color="RGB(165, 164, 164)", font="Verdana").set_position([curr_w+comment_title.size[0], curr_h])

        curr_h += comment_title.size[1]+15

        line = ColorClip(size=(4,comment_height-50), color=[84,84,82]).set_position([30, curr_h+5])
        
        comment_body_height = math.ceil(len(comments[comment_num].body)/150)*25
        margin = 15

        curr_w -= 5
        upvote_icon = ImageClip('src/upvote.png').resize(0.3).set_position((curr_w,curr_h+comment_body_height+margin))
        score = comments[comment_num].score
        if (score >= 1000):
            score = int(score/1000)
            score = str(score)+"k"
            left = 0
        else:
            score = str(score)
            left = 5
        like_num = TextClip(score, fontsize=20, color="white", font="Verdana-Bold").set_position((curr_w+upvote_icon.size[0]+10,curr_h+comment_body_height+5+margin))

        downvote_icon = ImageClip('src/downvote.png').resize(0.3).set_position((curr_w+upvote_icon.size[0]+like_num.size[0]+15+left,curr_h+comment_body_height+margin))

        share_icon = ImageClip('src/share.png').resize(0.4).set_position((curr_w+upvote_icon.size[0]+like_num.size[0]+20+downvote_icon.size[0]+5,curr_h+comment_body_height+margin))


        curr_w += 5
        completed = ""
        for i in range(len(comments_array[comment_num])):
            comment_audio = AudioFileClip("temp/audio/comment_"+str(comment_num)+"_"+str(i)+".mp3").fx(vfx.speedx, 1.0)
            dur = comment_audio.duration
            completed += comments_array[comment_num][i].strip() + " "
            comment_selftext = TextClip(completed, fontsize=22, color="white", font="Verdana", size=(comment_width-200, comment_height), method="caption", align="North-West").set_position((curr_w,curr_h))

            comment_clip = CompositeVideoClip([bg.set_duration(dur), comment_title.set_duration(dur), comment_title2.set_duration(dur), comment_selftext.set_duration(dur), upvote_icon.set_duration(dur), like_num.set_duration(dur), downvote_icon.set_duration(dur), share_icon.set_duration(dur),line.set_duration(dur), avatar.set_duration(dur)])
            comment_clip = comment_clip.set_audio(comment_audio)
            comment_vid_arr.append(comment_clip)
        
        final_comment_clip = concatenate_videoclips(comment_vid_arr)

        if (get_frame):
            final_comment_clip.save_frame(path, t = final_comment_clip.duration-1)
        else:
            return final_comment_clip;


    def generateAudio(self, text, out_path):
        aud = gTTS(text=text, lang="en", slow=False, tld="ca")
        aud.save(out_path)