from praw import Reddit
import json

class RedditAPI:

    # Auth and Setup
    def __init__(self):
        print("Logging into Reddit...")
        with open('user_data.json') as json_file:
            data = json.load(json_file)
        self.reddit = Reddit(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            user_agent="rTTS 2.0"
        )
        print("Login successful.")

    def fetchPosts(self, subreddit, num_of_posts):
        # Verifying subreddit
        exists = True
        try:
            self.reddit.subreddits.search_by_name(subreddit, exact=True)
        except:
            print("Invalid subreddit.")
            exists = False
            return

        # Getting posts
        self.posts = self.reddit.subreddit(subreddit).hot()
        return self.posts
    
    def getPosts(self):
        return self.posts