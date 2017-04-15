import socket
import select
import sys
import time
import os
import threading
import cPickle as pickle
from thread import *
from user import User
from tweet import Tweet

HOST = 'localhost'   #Symbolic name meaning all available ineterfaces
PORT = 4367          #Arbitrary non-privilleged port
clientlist = []      #list of all connected sockets
tweeterlist = []     #list of all users, user.status = Online/Offline
allTweets = []       #for making hashtag search easier...


''' login(vlidate_user,conn)
    receive username and password form client app
    goes through list of Twitter Clients to validate the user/pw pair
'''
#fix fail cases messages
def login(vlidate_user, conn):
    i = 0
    for user_i in tweeterlist:
        if user_i.username == vlidate_user.username:
            if user_i.password == vlidate_user.password:
                print "login success! user " + user_i.username + "is online"
                user_i.status = True #set this user to be online
                #update user's connected socket
                # user_i.conn_sock = conn 
                conn.send("SUCCESS:" + user_i.username + ":" + user_i.password)
                return user_i
            else:
                conn.send("FAILED:pwd incorrect")
                return
        i += 1
        if i > len(tweeterlist):
            break
    conn.send("FAILED:")
    return

''' welcome_message(curr_user)
    return the len of the offline messages
    gets call every loop from client menu
'''
def welcome_message(curr_user):
    sdata = "SUCCESS:" + str(len(curr_user.offline_tweets))
    return sdata

''' offline_tweets(curr_user, conn)
    get the curr_user's list of offline tweets
    move the list to allTweets once sent
'''
def all_offline_tweets(curr_user, conn):
    offlineTweets = []
    for ot in curr_user.offline_tweets:
        offlineTweets.append(ot)
        curr_user.tweets.append(ot)

    #clear offline tweets for current user
    curr_user.update_unread_messages([])

    #send list over pickle jar!
    jar = pickle.dumps(offlineTweets)
    conn.send(jar)
    return curr_user

''' get_sublist
    return a lis of strings
    string contians all the subscriptons of curr_user
'''
def get_sublist(curr_user,conn):
    sublist = []
    for s in curr_user.subs:
        sublist.append(s.username)

    jar = pickle.dumps(sublist)
    conn.send(jar)
    return

def get_list_all(curr_user, conn):
    all_user = []
    for u in tweeterlist:
        if u.username is not curr_user.username:
            all_user.append(u)

    jar = pickle.dumps(all_user)
    conn.send(jar)
    return

''' offline_sub(curr_user, sub_to_get, conn)
    go through the offline_tweets
        get all tweets from sub_to_get
        sub_to_get is the author of the tweet
    send over pickle
    remove sent tweets from offline_tweets of curr_user
'''
def offline_sub(curr_user, sub_to_get, conn):
    tweets_to_send = []
    tweets_to_keep = []
    # print "insdie important funct"
    for t2s in curr_user.offline_tweets:
        if t2s.author == sub_to_get:
            tweets_to_send.append(t2s)
            curr_user.tweets.append(t2s)
        else:
            tweets_to_keep.append(t2s)

    jar = pickle.dumps(tweets_to_send)
    conn.send(jar)
    curr_user.update_unread_messages(tweets_to_keep)
    return

''' make_post(tweet_data, curr_user)
    receive tweet message and hashtags from client
    -make a Tweet post, add to master allTweets and client's tweets
    -send back to client and all of the client's followers
'''
def make_post(tweet_data, curr_user):
    # t_data_split = tweet_data.split(':')
    '''tweet_data contains:
        tweet_data[0] == "POST": used for menu checking commands
        tweet_data[1] == Author of tweet
        tweet_data[2] == Tweet message: the tweet content string
        tweet_data[3] == hashtags: the hash tags separated by space
    '''
    tweet_author = curr_user
    tweet_content = tweet_data[2]
    htags = tweet_data[3].split()
    #construct the tweet to add
    tweet_to_add = Tweet(tweet_author, tweet_content,htags)
    #add to user's tweet list
    curr_user.tweets.append(tweet_to_add)
    #add to global tweet list 
    allTweets.append(tweet_to_add)

    #add to follower's list to display
    for f in tweeterlist:
        if f in curr_user.subs:
            if f.status is False:
                f.offline_tweets.append(tweet_to_add)
            else:
                f.tweets.append(tweet_to_add)

    sdata = "SUCCESS:POST"
    return sdata

''' post_live(curr_user)
    generate a list of Tweets to send to the client
    send list over socket using pickle
'''
def post_live(curr_user, conn):
    liveTweets = []
    for t in curr_user.tweets:
        if t.author == curr_user.username or t.author in curr_user.subs:
            liveTweets.append(t)
    jar = pickle.dumps(liveTweets)
    conn.send(jar)
    return

''' htag_search(query_tag, conn)
    pickle send the top ten tweets with the query_tag
    if less than ten send it anyway :3
'''
def htag_search(query_tag, conn):
    found_tags = []
    for tw in allTweets:
        for tg in tw.htags:
            if tg == query_tag:
                found_tags.append(tw)
                if len(found_tags) == 10:
                    break

    jar = pickle.dumps(found_tags)
    conn.send(jar)
    return

''' logout(curr_user, conn)
    log the current user out of the server
    remove conn socket from list
    change status to false
'''
def logout(curr_user, conn):
    if curr_user in tweeterlist:
        #change status to false
        curr_user.status = False
        # curr_user.conn_sock = None
        #remove conn form clientlist
    if conn in clientlist:
        clientlist.remove(conn)
    conn.send("SUCCESS:LOGOUT")
    return

def add_sub(curr_user, user_to_sub):
    status = None
    print "CURRENT: " + curr_user.username
    print "SUB: "  + user_to_sub
    for u in tweeterlist:
        if u.username == user_to_sub:
            curr_user.subscribe(u)
            status = "SUCCESS:"
            return status
    status = "FAILED:"
    return status

def drop_sub(curr_user, user_to_drop):
    status = None
    for u in curr_user.subs:
        if u.username == user_to_drop:
            curr_user.subs.remove(u)
            status = "SUCCESS:"
            return status
    status = "FAILED:"
    return status

#main client function thread.
def clientthread(conn):
    curr_user = None
    print "------------------------------------------------"
    while True:
        rdata = conn.recv(1024) #received data
        pdata = rdata.split(':') #parsed data
        print "received data: " + rdata
        print "------------------------------------------------"

        #setup replies to send back
        sdata =  None #initialize and reset
        if pdata[0] == "LOGIN": #set current user
            user_to_validate = User(pdata[1],pdata[2])
            curr_user = login(user_to_validate,conn)
            #send in function. Set current user for clientthread
        
        elif pdata[0] == "WELCOME":
            sdata = welcome_message(curr_user)
        
        elif pdata[0] == "ALL_OFFLINE": #retrive the list of offline tweets to print 
            all_offline_tweets(curr_user,conn) #pickle send!
            # curr_user.update_unread_messages([])
        
        elif pdata[0] == "GET_SUBLIST": # get the list of subs of curr_user
            get_sublist(curr_user, conn) #pickle send!

        elif pdata[0] == "GET_LIST_ALL":
            get_list_all(curr_user,conn)
        
        elif pdata[0] == "OFFLINE_SUB": #get the sub_to_get in offline_tweets
            offline_sub(curr_user,pdata[1], conn) #pickle send!
        
        elif pdata[0] == "POST": #make a Tweet, send to live clients
            sdata = make_post(pdata, curr_user)
       
        elif pdata[0] == "LIVE": #display live tweets
            post_live(curr_user,conn) #pickle send!
       
        elif pdata[0] == "ADD_SUB":
            sdata = add_sub(curr_user, pdata[1])
        
        elif pdata[0] == "DROP_SUB":
            sdata = drop_sub(curr_user, pdata[1])
        
        elif pdata[0] == "HTAG_SEARCH": #search top 10 tweets with the given hashtag
            htag_search(pdata[1],conn) #pickle send!
        
        elif pdata[0] == "LOGOUT":
            logout(curr_user, conn)
            break

        else:
            conn.send("FAILED:Invalid command")
        
        #send if there's something in sdata
        if sdata is not None:
            conn.send(sdata)
    conn.close()
    return
        
def exec_command(command):
    if command == "messagecount":
        print "Total Message Count: " + str(len(allTweets))
    elif command == "usercount":
        online_count = 0
        for o in tweeterlist:
            if o.status:
                online_count += 1
        print "Total Users Online: " + str(online_count)
    elif command == "stored count:":
        offline_count = 0
        for u in tweeterlist:
            for t in u.offline_tweets:
                offline_count += 1
        print "Total Stored Tweets: " + str(offline_count)
    elif command == "newuser":
        new_uname = raw_input("Enter new username")
        new_pwd = raw_input("Enter password")
        for u in tweeterlist:
            if new_uname == u.username:
                print"username already existed!"
                return
        tweeterlist.append(User(new_uname, new_pwd))
    elif command == "exit": 
        print "shutting server down..."
        ss.close()
        sys.exit()

def process():
    while True:
        conn, addr = ss.accept()

        # read_sockets,write_sockets,error_sockets = select.select(my_data.socket_dict,[],[])

        # for sock in read_sockets:
        #   if sock == sys.stdin: 
        #     command = sys.stdin.readline().strip()
        # if raw_input("> "):
        #     exec_command(command)

        print "Connection esablished with: " + addr[0] + ':' + str(addr[1])
        clientlist.append(conn)
        start_new_thread(clientthread , (conn,))
        #exit command
        #check client list command
        time.sleep(2)

#main function, takes care of socket setup
#connecting multiple users.
if __name__ == "__main__":
    global ss #server_socket
    #Socket setup
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try: #socket binding
        ss.bind((HOST, PORT))
    except socket.error, msg:
        print 'Bind failed. Error: ' + str(msg[0]) + ' Message ' + msg[1] + '\n'
        sys.exit()
    #Socket Listening
    ss.listen(10)
    print "Socket now Listening... on port: " + str(PORT) + '\n'

    #this is messy...
    #generate hardcoded list of users
    tweeterlist.append(User("Kevin","123456"))
    tweeterlist.append(User("Aria","654321"))
    tweeterlist.append(User("Kyle", "55555"))
    
    # #hard coded
    tweeterlist[0].subs.append(tweeterlist[1])
    # tweeterlist[1].subs.append(tweeterlist[0])
    # tweeterlist[2].subs.append(tweeterlist[0])
    # # tweeterlist[0].followers.append(tweeterlist[1])
    # tweeterlist[0].followers.append(tweeterlist[2])
    # tweeterlist[1].followers.append(tweeterlist[0])


    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()
    while True:
        command = raw_input('\n\t> ')
        exec_command(command)
    ss.close()
