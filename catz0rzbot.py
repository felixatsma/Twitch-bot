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
mods   = []

irc    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def irc_connect(server, port):
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

def irc_input():
    while True:
        command = input("-> ")
        if command == "q" or command == "x":
            break
        send(command)

def send(msg):
    irc.send(("PRIVMSG #sir_catz0rz :" + msg + "\n").encode())
    print("catz0rzbot\t: " + msg)

def irc_read():
    regex = re.compile(r'^:([^\s]+)!.*#[^\s]+ :(.*)\r\n$')
    print("Chat:")
    while True:
        chat = irc.recv(2040)
        mesg = regex.findall(chat.decode())
        if len(mesg) != 0:
            if (len(str(mesg[0][0])) > 7):
                print(str(mesg[0][0]) + "\t: " + str(mesg[0][1]))
            else:
                print(str(mesg[0][0]) + "\t\t: " + str(mesg[0][1]))
            if mesg[0][1][0] == "!" and mesg[0][0] == owner or mesg[0][0] in mods:
                if mesg[0][1] == "!stop":
                    send("/me is now offline")
                    print("User " + str(mesg[0][0]) + " called !stop")
                    break
                elif mesg[0][1] == "!ping":
                    send("pong")
                elif mesg[0][1] == "!marco":
                    send("polo")
                elif mesg[0][1] == "!time":
                    send(time.asctime(time.localtime(time.time())))
                elif mesg[0][1] == "!birthday":
                    send("Happy birthday " + mesg[0][0] + "!")
                time.sleep(2)

def irc_exit():
    print("exiting...")
    irc.send(("PART $sir_catz0rz\n").encode())
    irc.send(("QUIT\n").encode())
    irc.close()

def main():
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
