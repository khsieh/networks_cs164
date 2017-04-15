class User:
    """The Twitter User
        Attributes:
            username: the Twitter handle of the user
            password: password for the login 
            message_list: list of messages.
            subs: list of other users that self subscribes to.
    """
    def __init__(self, usr, pwd):
        self.username = usr
        self.password = pwd
        self.tweets = [] #tweets to display in live_tweets
        self.offline_tweets = []
        self.subs = []
        self.followers = [] #Extra Credit
        self.status = False
        # self.index = None
        # self.conn_sock = None
        return

    def __eq__(self, other):
        return self.username == other

    def update_unread_messages(self, new_list):
        self.offline_tweets = []
        self.offline_tweets = new_list
        return

    def printInfo(self):
        print "username: @" + self.username
        print "subs: "
        for s in self.subs:
            print '\t' + s.username

        # print "followers: "
        # for f in self.followers:
        #     print '\t' + f.username
        return

    def  subscribe(self, other):
        if other not in self.subs:
            self.subs.append(other)
        return