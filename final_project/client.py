import socket #for sockets
import sys    #for exit
import os
import getpass
import time
import cPickle as pickle
from thread import *
from user import User
from tweet import Tweet

HOST = 'localhost'
PORT = 4367
# s = None

def clearScreen():
    os.system('clear')

''' offline_messages(curr_user)
    Display the messages that the user missed when he's offline
    only callled when the user chooses the menu option "View offline messages"
    another option for subs specific
    "OFFLINE:user_name"
    if user_name == self, retrive all ot
    if user_name == other, validate then retrive ot
'''
def offline_messages(curr_user):
    status = None
    while True:
        print "========== OFFLINE MESSAGES ========="
        print "|                                   |"
        print "|     1. All Offline Messages    (A)|"
        print "|     2. Specific Subscription   (S)|"
        print "|                                   |"
        print "=====================================" 
        offline_option = raw_input("Enter an option\n\t> ")
        #ALL offline messages
        if offline_option == "1" or offline_option == "A" or offline_option == "a":
            command = "ALL_OFFLINE:" + curr_user
            ss.send(command)
            #pickle recv
            rdata = pickle.loads(ss.recv(4096))
            for r in rdata:
                r.printTweet()
            status = "SUCCESS"

        #specific subscription
        elif offline_option == "2" or offline_option == "S" or offline_option == "s":
            command = "GET_SUBLIST:" + curr_user
            ss.send(command)
            #pickle recv
            rdata = pickle.loads(ss.recv(4096))
            print "=========== SUBSCRIPTIONS ==========="
            if len(rdata) > 0:
                for r in rdata:
                    print '\t' + r
            else:
                print "you have 0 subscriptions!"
                print "Use the Edit Subscriptions option in the MENU to add subscriptions!"
                return
            print "=====================================" 
            sub_to_get = raw_input("Enter username to check offline messages from\n\t> ")

            if sub_to_get in rdata:
                command = "OFFLINE_SUB:" + sub_to_get
                ss.send(command)
                #pickle recv!!
                rdata = pickle.loads(ss.recv(4096))
                #print tweets
                for r in rdata:
                    r.printTweet()
                status = "SUCCESS"
            else:
                print "Invalid username!"
                status = "FAILED"
        elif offline_option == "CANCEL":
            break
        if status == "SUCCESS":
            raw_input("Press any key to continue")
            break #break out of while loop
    return


'''
'''
def edit_subs(curr_user):
    status = None
    while True:
        print "========== OFFLINE MESSAGES ========="
        print "|                                   |"
        print "|     1. Add Subscription        (A)|"
        print "|     2. Drop Subscription       (D)|"
        print "|                                   |"
        print "=====================================" 
        sub_option = raw_input("Enter an option\n\t> ")
        #add a subscription
        if sub_option == '1' or sub_option == 'A' or sub_option == 'a':
            command = "GET_LIST_ALL"
            ss.send(command)
            available_users = pickle.loads(ss.recv(4096))
            user_to_sub = raw_input("Enter username to follow\n\t> ")
            if user_to_sub in available_users: #if valid user
                print "user @" + user_to_sub + " found!"
                command = "ADD_SUB:" + user_to_sub
                ss.send(command)
                rdata = ss.recv(1024)
                pdata = rdata.split(':')
                status = pdata[0] #SUCCESS or FAIL
                # print "in if statement:" + status
            else: #if invalid user
                print "user @" + user_to_sub + " not found!"
        #drop a subsription
        elif sub_option == '2' or sub_option == 'D' or sub_option == 'd':
            command = "GET_SUBLIST:" + curr_user
            ss.send(command)
            sublist = pickle.loads(ss.recv(4096))
            print "=========== SUBSCRIPTIONS ==========="
            if len(sublist) > 0:
                for r in sublist:
                    print "\t@" + r
            else:
                print "you have 0 subscriptions!"
                print "Use the Edit Subscriptions option in the MENU to add subscriptions!"
                time.sleep(1)
                return
            print "=====================================" 
            sub_to_drop = raw_input("Enter username to unfollow\n\t> ")
            if sub_to_drop in sublist:
                command = "DROP_SUB:" + sub_to_drop
                ss.send(command)
                rdata = ss.recv(1024)
                pdata = rdata.split(':')
                status = pdata[0]
        if status == "SUCCESS":
            print pdata[1] + " SUCCESSFUL"
            break
        elif status == "FAILED":
            print "ERROR " + pdata[1] + " FAILED"
            break
    time.sleep(1)
    return

''' post_new_message(curr_user)
    Prompt user for a tweet post, check if the message is under 140 characters
    re-prompt the user if it is over char count.
    prompt for hashtags
'''
def post_new_message(curr_user):
    command = None
    while True:
        tweet = raw_input("What's happening? \n\t> ")
        if tweet == "CANCEL":
            command = "CANCEL:"
            break
        if len(tweet) > 140:
            print "Tweet exceeding 140 characters!\n"
        else:
            while True:
                htag = raw_input("Enter the Hashtags with \'#\', separate by spaces: \n\t> ")
                if htag == "CANCEL":
                    command = "CANCEL:"
                    break
                else:
                    command = "POST:" + curr_user + ":" + tweet + ":" + htag
                    break
            break
    return command

'''
    A user can search for a hashtag and he will get last 10 tweets containing that
    hashtag.
'''
def hashtag_search(curr_user):
    query_tag = raw_input("Enter the hashtag you want to search \n\t> ")
    command = "HTAG_SEARCH:" + query_tag
    ss.send(command)

    rdata = pickle.loads(ss.recv(4096))
    if len(rdata) <= 0:
        print "No Tweets fround with " + query_tag + "!"
    else:
        for r in rdata:
            r.printTweet()

    raw_input("Press anything to continue > ")
    return


''' live_tweets(curr_user)
    function that prints out the last 10 tweets in the subs list
    use pickle to recv the list of tweets to display
    call printTweets on the list
    used in menu, before printing out opotions
'''
def live_tweets(curr_user):
    #query server for a list of tweets to display
    query = "LIVE:" + curr_user
    ss.send(query)
    rdata = pickle.loads(ss.recv(4096))#pickle recv
    #UNPICKLE!
    for r in rdata:
        r.printTweet()
        # print r

def welcom_message(curr_user):
    print "Welcome: @" + curr_user + "!"
    command = "WELCOME:" + curr_user
    ss.send(command)
    rdata = ss.recv(1024).strip()
    pdata = rdata.split(":")
    print "You have " + pdata[1] + " unread messages"

def menu(curr_user):
    while True:
        #command get declared and reset
        command = None
        clearScreen()
        #Welcome message with number of offline messages
        welcom_message(curr_user)
        #live tweets?
        live_tweets(curr_user) #print in function
        print "================ MENU ==============="
        print "|                                   |"
        print "|     1. View Offline Messages   (O)|"
        print "|     2. Edit Subscriptions      (E)|"
        print "|     3. Post a Message          (P)|"
        print "|     4. Hashtag Search          (H)|"
        print "|     5. Log out                 (L)|"
        print "|                                   |"
        print "| type \"CANCEL\" to return to MENU   |" #the extra \ character mang
        print "=====================================" 
        
        #functions set up commands 
        user_option = raw_input("Enter an option:\n\t> ")
        if user_option == "1" or user_option == "O" or user_option == "o":
            command = offline_messages(curr_user)

        elif user_option == "2" or user_option == "E" or user_option == "e":
            command = edit_subs(curr_user)

        elif user_option == "3" or user_option == "P" or user_option == "p":
            command = post_new_message(curr_user)

        elif user_option == "4" or user_option == "H" or user_option == "h":
            hashtag_search(curr_user) #print in function

        elif user_option == "5" or user_option == "L" or user_option == "l":
            print "Logging out..."
            #send server logout msg
            command = "LOGOUT:" + curr_user#.username
        else:
            print "Error: Invalid Option!"
            time.sleep(0.5)
        
        #talk to server 
        if command is not None:
            #send command to server to process
            ss.send(command)

            #recev from server and parse for success or fail
            rdata = ss.recv(4096).strip() #received data
            pdata = rdata.split(':') #parsed data
            # print pdata #debugging print
            if pdata[0] == "FAILED":
                print "ERROR: " + pdata[1]
            elif pdata[0] == "SUCCESS":
                print pdata[1] + " SUCCESSFUL"
                if pdata[1] == "LOGOUT":
                    break
    return

def login():
    while True:
        login = raw_input("Enter username: ")
        pw = getpass.getpass("Enter password: ")
        
        #send tmp_user to server to validate
        user_to_validate = "LOGIN:" + login + ":" + pw
        ss.send(user_to_validate)
        while True:
            print "Loading..."
            rdata = ss.recv(2048).strip() #received data

            if not rdata:
                print "Disconnected from server!!"
                break
            else:
                pdata = rdata.split(':') #parsed data
                if pdata[0] == "SUCCESS":
                    print "Login Success! " + pdata[1] + " " + pdata[2]
                    # validated_user = pdata[1] #User(pdata[1], pdata[2])
                    return pdata[1]
                else:
                    print "Incorrect username or password!\n"
                    break
        #end while

    #end while

if __name__ == "__main__":
    global ss #server_socket
    #setup connection to server
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.settimeout(10)

    # connet to host
    try:
        ss.connect((HOST,PORT))
    except: 
        print "Failure to connect to HOST"
        sys.exit()


    curr_user = login()

    # print "\nWelcome "  + curr_user.username + "!"
    # print "your password is: " + curr_user.password + "\n"
    
    menu(curr_user)
