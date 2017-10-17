#!/usr/bin/env python3

import sys
import socket
import re
import time

user = "catz0rzbot"
passwd = open("passwd", "r").read()
server = "irc.twitch.tv"
port = 6667
chan = "#sir_catz0rz"

owner = "sir_catz0rz"
mods = ["catz0rzbot"]

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

command_dict = {}


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
    Commands are processed in here.
    """
    regex = re.compile(r'^:([^\s]+)!.*#[^\s]+ :(.*)\r\n$')
    print("Chat:")
    while True:
        chat = irc.recv(2040)
        mesg = regex.findall(chat.decode())
        if len(mesg) != 0:
            usr = mesg[0][0]
            txt = mesg[0][1].split()[0]
            args = mesg[0][1].split()[1:]

            if (len(str(usr)) > 7):
                print(str(usr) + "\t: " + str(txt))
            else:
                print(str(usr) + "\t\t: " + str(txt))

            if txt in command_dict:
                send(command_dict[txt])
            elif txt == "!time":
                send(time.asctime(time.localtime(time.time())))
            elif txt == "!birthday":
                send("Happy birthday " + usr + "!")

            # Mod commands
            if txt[0] == "!" and usr == owner or usr in mods:
                print(txt)
                if txt == "!stop":
                    send("/me is now offline")
                    print("User " + str(usr) + " called !stop")
                    break
                elif txt == "!addmod":
                    mods.append(args[0])
                elif txt == "!addcom":
                    if args[0] in command_dict:
                        send("Command already exists!")
                    else:
                        add_com(args[0], " ".join(args[1:]))


def read_comms():
    """
    Reads commands from 'comms' file into command_dict dictionary.
    """
    comms = (open("comms", "r")).readlines()

    for line in comms:
        command_dict.update({line.split()[0]: " ".join(line.split()[1:])})


def add_com(com, text):
    """
    Adds command to command_dict and 'comms' file.
    """
    comms = (open("comms", "a"))
    command_dict.update({"!" + com: text})
    comms.write("!%s %s\n" % (com, text))
    send("Command added succesfully.")


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
    read_comms()
    irc_connect(server, port)
    irc_read()
    irc_exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        send("/me is now offline")
        irc_exit()
        sys.exit()
    except Exception as e:
        print("ERROR: ", e)
        send("/me is now offline")
        irc_exit()
        sys.exit()
