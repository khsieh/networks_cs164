from user import User

class Tweet:
    """A Twitter Post
        Attributes:
            message: < 140 char string 
            tags:   the tags associate with the tweet
    """
    def __init__(self,user, msg, tags):
        self.author = user
        self.message = msg #msg content
        self.htags = tags #list of tags
        self.masterIndex = None
        return

    def printTweet(self):
        print "====================================="
        print "@" + self.author.username
        print self.message
        print ' '.join(self.htags)
        print "====================================="
        return

    # def add_hash(self):
    #     self.htags = ["#" + h for h in self.htags if h[0] is not '#']
    #     return