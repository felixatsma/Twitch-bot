#!/usr/bin/python
import sys
import socket
import re
import time

user   = "catz0rzbot"
passwd = (open("passwd", "r")).read()
server = "irc.twitch.tv"
port   = 6667
chan   = "#sir_catz0rz"

owner  = "sir_catz0rz"
mods   = ["catz0rzbot"]

irc    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

com_dic = []

def irc_connect(server, port):
    """
    Connects to the Twitch irc servers, to the channel specified in 'chan'
    Prints the response to the attempted connection, this should just be the
    Twitch welcome message.
    """
    print("connecting to : " + server + ":" + str(port))
    print("channel       : " + chan)
    irc.connect((server, port))
    irc.send(("USER catz0rzbot - - :catz0rzbot\n").encode())
    irc.send(("PASS " + passwd + "\n").encode())
    irc.send(("NICK " + user + "\n").encode())
    irc.send(("JOIN " + chan + "\n").encode())
    response = irc.recv(2040)
    print(response.decode('unicode_escape'))
    send("/me is now online")

def send(msg):
    """
    Posts a message in the connected channel.
    """
    irc.send(("PRIVMSG #sir_catz0rz :" + msg + "\n").encode())
    print("catz0rzbot\t: " + msg)

def irc_read():
    """
    Read loop that reads messages posted in the channel and recovers the
    username and message.
    All commands are specified in here.

    TODO: add !addcom command that adds simple text response commands stored
          in a dictionary.

    TODO: seperate words in message.
    """
    regex = re.compile(r'^:([^\s]+)!.*#[^\s]+ :(.*)\r\n$')
    print("Chat:")
    while True:
        chat = irc.recv(2040)
        mesg = regex.findall(chat.decode())
        if len(mesg) != 0:
            usr  = mesg[0][0]
            txt  = mesg[0][1]
            #if (mesg[0][2])
            if (len(str(usr)) > 7):
                print(str(usr) + "\t: " + str(txt))
            else:
                print(str(usr) + "\t\t: " + str(txt))
            if txt == "!ping":
                send("pong")
            elif txt == "!marco":
                send("polo")
            elif txt == "!time":
                send(time.asctime(time.localtime(time.time())))
            elif txt == "!birthday":
                send("Happy birthday " + usr + "!")
            if txt[0] == "!" and \
               usr == owner or usr in mods:
                if txt == "!stop":
                    send("/me is now offline")
                    print("User " + str(usr) + " called !stop")
                    break
                elif txt == "!addmod":
                    pass
                    #mods.append(mesg[arg])

def irc_exit():
    """
    Closes the irc connection.
    """
    print("exiting...")
    irc.send(("PART $sir_catz0rz\n").encode())
    irc.send(("QUIT\n").encode())
    irc.close()

def main():
    """
    Initializes connection and read loop.
    """
    irc_connect(server, port)
    irc_read()
    irc_exit()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        send("/me is now offline")
        irc_exit()
        sys.exit()
