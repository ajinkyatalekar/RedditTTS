from data.RedditAPI import *
from data.VideoGenerator import *
import lib.tkinter as tk

class GUI:

    def __init__(self):
        with open('user_data.json') as json_file:
            self.config = json.load(json_file)
        with open('post_data.json') as file:
            self.post_data = json.load(file)
        self.chosen_post = -1
        self.chosen_comments = []
        self.start = 0
        self.videoGenerator = VideoGenerator()

    def client_info(self):
        self.root = tk.Tk()
        self.root.title('RedditTTS v2.0')
        self.root.state('zoomed')

        self.client_info_frame = tk.Frame(self.root)
        self.title = tk.Frame(self.root)

        tk.Label(self.title, text="RedditTTS v2.0", font=("Verdana", 20)).pack()

        tk.Label(self.title, text="", font=("Verdana", 10)).pack()

        tk.Label(self.client_info_frame, text="Client ID: ", font=("Verdana", 15)).pack()
        self.client_id=tk.Entry(self.client_info_frame, width=30)
        self.client_id.insert(0, self.config['client_id'])
        self.client_id.pack()


        tk.Label(self.client_info_frame, text="Client Secret: ", font=("Verdana", 15)).pack()
        self.client_secret=tk.Entry(self.client_info_frame, width=30)
        self.client_secret.insert(0, self.config['client_secret'])
        self.client_secret.pack()


        tk.Label(self.client_info_frame, text="", font=("Verdana", 10)).pack()

        tk.Button(self.client_info_frame, text="Login", command=self.login).pack()

        self.title.pack()
        self.client_info_frame.pack()
        self.root.mainloop()

    def login(self):
        config = {
            "client_id":self.client_id.get(),
            "client_secret":self.client_secret.get()
        }

        with open("user_data.json", "w") as outfile:
            json.dump(config, outfile)

        self.api = RedditAPI()
        self.get_posts()
    
    def get_posts(self):
        self.done_comments = False
        self.client_info_frame.destroy()
        self.subreddit_frame = tk.Frame(self.root)
        self.subreddit_frame_2 = tk.Frame(self.root)
        self.posts_frame= tk.Frame(self.root)
        self.posts_frame_lower = tk.Frame(self.root)

        
        tk.Label(self.subreddit_frame, text="Subreddit: ", font=("Verdana", 15)).pack()
        self.sub_name=tk.Entry(self.subreddit_frame, width=30)
        self.sub_name.insert(0, self.post_data['subreddit'])
        self.sub_name.pack()
        tk.Button(self.subreddit_frame, text="Browse Posts", command=self.display_posts).pack()

        tk.Label(self.subreddit_frame_2, text="", font=("Verdana", 10)).pack()
        tk.Label(self.subreddit_frame_2, text="OR", font=("Verdana", 15)).pack()
        tk.Label(self.subreddit_frame_2, text="", font=("Verdana", 10)).pack()
        
        tk.Label(self.subreddit_frame_2, text="Submission ID: ", font=("Verdana", 15)).pack()
        self.sub_id=tk.Entry(self.subreddit_frame_2, width=30)
        self.sub_id.pack()
        tk.Button(self.subreddit_frame_2, text="Get Comments for Particular Post", command=self.particular_post_helper).pack()


        tk.Label(self.subreddit_frame, text="", font=("Verdana", 10)).pack()

        self.subreddit_frame.pack()
        self.subreddit_frame_2.pack()
        self.posts_frame.pack()

    def display_posts(self):
        self.posts_frame.destroy()
        self.posts_frame_lower.destroy()
        self.posts_frame = tk.Frame(self.root)
        self.subreddit_frame_2.destroy()

        post_data = {
            "subreddit": self.sub_name.get(),
            "num_of_posts": 15
        }

        with open("post_data.json", "w") as outfile:
            json.dump(post_data, outfile)


        tk.Label(self.posts_frame, text="Choose a post to make a video of:", font=("Verdana", 15)).pack()

        tk.Label(self.posts_frame, text="", font=("Verdana", 15)).pack()

        postBuilder = self.api.fetchPosts(post_data["subreddit"], post_data["num_of_posts"])

        self.posts = []
        self.start = -5
        for post in postBuilder:
            self.posts.append(post)

        self.posts_frame.pack()
        self.posts_frame_lower = tk.Frame(self.root)
        self.posts_frame_lower.pack()

        self.display_posts_helper()

    def display_posts_helper(self):
        posts = self.posts
        self.start += 5
        start = self.start

        self.posts_frame_lower.destroy()
        self.posts_frame_lower = tk.Frame(self.root)

        titles = [posts[start].title, posts[start+1].title, posts[start+2].title, posts[start+3].title, posts[start+4].title]
        selftexts = [posts[start].selftext, posts[start+1].selftext, posts[start+2].selftext, posts[start+3].selftext, posts[start+4].selftext]

        for i in range(len(titles)):
            titles[i] = titles[i].replace('\n', '')
            selftexts[i] = selftexts[i].replace('\n', '')
            if (len(titles[i])>161):
                titles[i] = titles[i][0:160] + "....."
            if (len(selftexts[i])>161):
                selftexts[i] = selftexts[i][0:160] + "....."

        self.postRadio = tk.IntVar()

        tk.Radiobutton(self.posts_frame_lower, text = titles[0], font=("Verdana-Bold", 15), variable=self.postRadio, value=1).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = selftexts[0], font=("Verdana", 15)).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = "", font=("Verdana", 15)).pack(anchor="w")

        tk.Radiobutton(self.posts_frame_lower, text= titles[1], font=("Verdana-Bold", 15), variable=self.postRadio, value=2).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = selftexts[1], font=("Verdana", 15)).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = "", font=("Verdana", 15)).pack(anchor="w")

        tk.Radiobutton(self.posts_frame_lower, text= titles[2], font=("Verdana-Bold", 15), variable=self.postRadio, value=3).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = selftexts[2], font=("Verdana", 15)).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = "", font=("Verdana", 15)).pack(anchor="w")

        tk.Radiobutton(self.posts_frame_lower, text= titles[3], font=("Verdana-Bold", 15), variable=self.postRadio, value=4).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = selftexts[3], font=("Verdana", 15)).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = "", font=("Verdana", 15)).pack(anchor="w")
        
        tk.Radiobutton(self.posts_frame_lower, text= titles[4], font=("Verdana-Bold", 15), variable=self.postRadio, value=5).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = selftexts[4], font=("Verdana", 15)).pack(anchor="w")
        tk.Label(self.posts_frame_lower, text = "", font=("Verdana", 15)).pack(anchor="w")
        
        tk.Button(self.posts_frame_lower, text="More Posts", command=self.display_posts_helper).pack()
        tk.Label(self.posts_frame_lower, text="", font=("Verdana", 15)).pack()
        tk.Button(self.posts_frame_lower, text="Done! Select Comments", command=self.choose_post).pack()

        self.posts_frame_lower.pack()
    
    def choose_post(self):
        self.chosen_post = -1

        self.chosen_post = self.posts[self.start+self.postRadio.get()-1]
        
        if (self.chosen_post!=-1):
            self.start = -5
            self.display_comments()

    def particular_post_helper(self):
        self.chosen_post = self.api.reddit.submission(id=self.sub_id.get())
        print(self.chosen_post.title)
        self.display_comments()

    def display_comments(self):
        self.subreddit_frame_2.destroy()
        self.start += 5
        start = self.start

        self.posts_frame_lower.destroy()
        self.posts_frame_lower = tk.Frame(self.root)

        comments = []
        for i in range(8):
            comments.append(self.chosen_post.comments[start+i].body)

        for i in range(len(comments)):
            comments[i] = comments[i].replace('\n', '')
            if (len(comments[i])>161):
                comments[i] = comments[i][0:160] + "....."


        # self.videoGenerator.comment_video(self.chosen_post.comments[start], True, "temp/img/1.png")
        # imge1 = Image.open("temp/img/1.png")
        # img1 = ImageTk.PhotoImage(imge1.resize((1000, math.ceil(imge1.height*800/imge1.width))))
        # tk.Label(self.posts_frame_lower, image = img1).pack()

        self.comm1 = tk.IntVar()
        tk.Checkbutton(self.posts_frame_lower, text = comments[0], font=("Verdana", 15), variable=self.comm1).pack()

        
        # self.videoGenerator.comment_video(self.chosen_post.comments[start+1], True, "temp/img/2.png")
        # imge2 = Image.open("temp/img/2.png")
        # img2 = ImageTk.PhotoImage(imge2.resize((1000, math.ceil(imge2.height*800/imge2.width))))
        # tk.Label(self.posts_frame_lower, image = img2).pack()

        self.comm2 = tk.IntVar()
        tk.Checkbutton(self.posts_frame_lower, text = comments[1], font=("Verdana", 15), variable=self.comm2).pack()


        # self.videoGenerator.comment_video(self.chosen_post.comments[start+2], True, "temp/img/3.png")
        # imge3 = Image.open("temp/img/3.png")
        # img3 = ImageTk.PhotoImage(imge3.resize((1000, math.ceil(imge3.height*800/imge3.width))))
        # tk.Label(self.posts_frame_lower, image = img3).pack()
        
        self.comm3 = tk.IntVar()
        tk.Checkbutton(self.posts_frame_lower, text = comments[2], font=("Verdana", 15), variable=self.comm3).pack()

        # self.videoGenerator.comment_video(self.chosen_post.comments[start+3], True, "temp/img/4.png")
        # imge4 = Image.open("temp/img/4.png")
        # img4 = ImageTk.PhotoImage(imge4.resize((1000, math.ceil(imge4.height*800/imge4.width))))
        # tk.Label(self.posts_frame_lower, image = img4).pack()

        self.comm4 = tk.IntVar()
        tk.Checkbutton(self.posts_frame_lower, text = comments[3], font=("Verdana", 15), variable=self.comm4).pack()

        # self.videoGenerator.comment_video(self.chosen_post.comments[start+4], True, "temp/img/5.png")
        # imge5 = Image.open("temp/img/5.png")
        # img5 = ImageTk.PhotoImage(imge5.resize((1000, math.ceil(imge5.height*800/imge5.width))))
        # tk.Label(self.posts_frame_lower, image = img5).pack()

        self.comm5 = tk.IntVar()
        tk.Checkbutton(self.posts_frame_lower, text = comments[4], font=("Verdana", 15), variable=self.comm5).pack()
        
        tk.Button(self.posts_frame_lower, text="More Comments", command=self.comment_helper).pack()
        tk.Label(self.posts_frame_lower, text="", font=("Verdana", 15)).pack()
        tk.Label(self.posts_frame_lower, text="Previously chosen comments: "+str(len(self.chosen_comments)), font=("Verdana", 15)).pack()
        tk.Button(self.posts_frame_lower, text="Done! Generate Video!", command=self.comment_helper_2).pack()

        self.posts_frame_lower.pack()

    def comment_helper_2(self):
        self.done_comments = True
        self.comment_helper()

    def comment_helper(self):
        if (self.comm1.get()==1):
            self.chosen_comments.append(self.chosen_post.comments[self.start])
        if (self.comm2.get()==1):
            self.chosen_comments.append(self.chosen_post.comments[self.start+1])
        if (self.comm3.get()==1):
            self.chosen_comments.append(self.chosen_post.comments[self.start+2])
        if (self.comm4.get()==1):
            self.chosen_comments.append(self.chosen_post.comments[self.start+3])
        if (self.comm5.get()==1):
            self.chosen_comments.append(self.chosen_post.comments[self.start+4])
        
        if os.path.exists("temp/img"):
            rmtree("temp/img")
        if (not self.done_comments):
            self.display_comments()
        elif (self.chosen_post!=-1):
            self.start = -5
            self.make_video()
    

    def make_video(self):
        videoGenerator = VideoGenerator()
        videoGenerator.generateVideo(self.chosen_post, self.chosen_comments)
        self.root.destroy()
        gui = GUI()
        gui.client_info()

# gui = GUI()
# gui.client_info()