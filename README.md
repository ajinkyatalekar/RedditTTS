# RedditTTS

## What It Does
This Python app scrapes popular Reddit posts and comments and creates ready-to-upload entertaining videos with background music, text-to-speech, 
and screenshots of the post and top comments. :sparkles:  
  
**TL;DR** it makes those Reddit text-to-speech videos that have taken over YouTube, TikTok, FaceBook, and everywhere else for you.

## Usage
1. Create your own Reddit Bot [here](https://www.reddit.com/prefs/apps/) and note down the `client id` and `client secret`.  
2. Now, in the *src/config.json* file, put in your bot's `client_id`, `client_secret` which the bot will use
while scraping Reddit.  
3. Add default video file to *src/video* and name it `bgFull.mp4` (You can skip this and choose a different video on launch).
4. Finally, install all the required libraries mentioned below and you're ready to go!
5. Now open *RedditTTS.py* and update perameters like `subreddit`, `posts` and `comments` to get posts from the subreddit of your choice and a video will
be generated in the */out* folder ~! :smile:

## Libraries Used
All of these are included with the app, except `ffmpeg`. If missing, just download it [here](https://ffmpeg.org/download.html). 
- `praw` to scrape Reddit posts.  
- `selenium` and `webdriver_manager` to generate screenshots of the posts.  
- `gtts` and `pydub` to generate audio.  
- `moviepy` to generate video.  
- `ffmpeg` and `ffprobe` to generate video.

## Future Plans
- Once the script is finalized, make a GUI App to make using this ultra easy.:dizzy: &rarr; Done! ✅
- Make libraries local, allowing app to be run without installing the whole list of modules. &rarr; Done! ✅
- Use the Reddit API directly instead of praw to improve performance {Current working on this :exclamation:}. 

## Contributors
Ajinkya Talekar | CS Student at University at Buffalo | [ajinkyatalekar.github.io](https://ajinkyatalekar.github.io)
