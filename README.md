# RedditTTS

## What It Does
This Python app scrapes popular Reddit posts and comments and creates ready-to-upload entertaining videos with background music, text-to-speech, 
and screenshots of the post and top comments. :sparkles:  
  
**TL;DR** it makes those Reddit text-to-speech videos that have taken over YouTube, TikTok, FaceBook, and everywhere else for you.


https://user-images.githubusercontent.com/91043799/197539273-705efa33-5a63-4e44-9826-08f21a98c2a8.mov


## Usage
*NOTE: You need ffmpeg installed on your computer for this to work.*
1. Create your own Reddit Bot [here](https://www.reddit.com/prefs/apps/), by selecting *'Personal Use Script'* and note down the `client id` and `client secret`.
2. Download the latest release for this app.
3. Run *RedditTTS.py* and enter your `cliend id` and `client secret`.  
Also update perameters like `subreddit`, `posts` and `comments` to get posts from the subreddit of your choice and a video will
be generated in the */out* folder ~! :smile:  
The */out* folder also contains a .txt file containing the information about the post.

https://user-images.githubusercontent.com/91043799/197540358-fb9a456e-f404-4f96-b0f7-ca5278b78cad.mov

## Libraries Used
All of these are included with the app, except `ImageMagick` and `ffmpeg`. If missing, just download them here: [ImageMagick](https://wiki.python.org/moin/ImageMagick#:~:text=PythonMagick%20is%20the%20Python%20binding,a%20large%20variety%20of%20formats.) and [ffmpeg](https://ffmpeg.org/download.html). 
- `praw` to scrape Reddit posts.  
- `ImageMagick` to generate screenshots of the posts.  
- `gtts` to generate audio.  
- `moviepy` to generate video.  
- `ffmpeg` and `ffprobe` to generate video.

## Future Plans
- Once the script is finalized, make a GUI App to make using this ultra easy.:dizzy: &rarr; Done! ✅
- Make libraries local, allowing app to be run without installing the whole list of modules. &rarr; Done! ✅
- Use the Reddit API directly instead of praw to improve performance {Current working on this :exclamation:}. 

## Contributors
Ajinkya Talekar | CS Student at University at Buffalo | [ajinkyatalekar.github.io](https://ajinkyatalekar.github.io)
