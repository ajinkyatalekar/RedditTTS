# RedditTTS

## What It Does
This Python app scrapes popular Reddit posts and comments and creates ready-to-upload entertaining videos with background music, text-to-speech, 
and screenshots of the post and top comments. :sparkles:  
  
**TL;DR** it makes those Reddit text-to-speech videos that have taken over YouTube, TikTok, FaceBook, and everywhere else for you.

## Usage
1. Create your own Reddit Bot [here](https://www.reddit.com/prefs/apps/), by selecting *'Personal Use Script'* and note down the `client id` and `client secret`.  
2. Download the latest release for this app.
3. Now open *src/config.json* and insert the `client id` and `client secret` you just made. Then run *RedditTTS.py*.  
*IMPORTANT: Select a background video*. Also update perameters like `subreddit`, `posts` and `comments` to get posts from the subreddit of your choice and a video will
be generated in the */out* folder ~! :smile:  
The */out* folder also contains a .txt file containing the information about the post.

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
