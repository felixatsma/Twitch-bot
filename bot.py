#!/usr/bin/env python3

import sys
import socket
import re
import time
import json

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

command_dict = {}
data = {}


def load_data():
    """
    Loads data from data.json into dictionaries.
    """
    global data
    global command_dict
    with open("data.json") as f:
        file = json.load(f)
    data = file["data"]
    command_dict = file["commands"]
    print(command_dict)


def dump_data():
    """
    Dumps (potentially updated) data from dictionaries in data.json when the
    bot is closed.
    """
    with open("data.json", "w") as f:
        json.dump({"data": data, "commands": command_dict}, f)


def irc_connect():
    """
    Connects to the Twitch irc servers, to the channel specified in 'chan'
    Prints the response to the attempted connection, this should just be the
    Twitch welcome message.
    """
    print("connecting to : " + data["server"] + ":" + str(data["port"]))
    print("channel       : " + data["chan"])
    irc.connect((data["server"], data["port"]))
    irc.send(("USER %s - - :%s\n" % (data["user"], data["user"])).encode())
    irc.send(("PASS " + data["passwd"] + "\n").encode())
    irc.send(("NICK " + data["user"] + "\n").encode())
    irc.send(("JOIN " + data["chan"] + "\n").encode())
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
            if txt[0] == "!" and usr == data["owner"] or usr in data["mods"]:
                print(txt)
                if txt == "!stop":
                    send("/me is now offline")
                    print("User " + str(usr) + " called !stop")
                    break
                elif txt == "!addmod":
                    if args[0] in data["mods"]:
                        send("User is already mod!")
                    else:
                        data["mods"].append(args[0])
                        send("Mod added")
                elif txt == "!addcom":
                    command_dict["!" + args[0]] = " ".join(args[1:])
                    send("Command added")


def irc_exit():
    """
    Closes the irc connection.
    """
    print("exiting...")
    irc.send(("PART $%s\n" % data["chan"][1:]).encode())
    irc.send(("QUIT\n").encode())
    irc.close()


def main():
    """
    Initializes connection and read loop.
    """
    load_data()
    irc_connect()
    irc_read()
    irc_exit()
    dump_data()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        send("/me is now offline")
        irc_exit()
        dump_data()
        sys.exit()
    except Exception as e:
        print("ERROR: ", e)
        send("/me is now offline")
        irc_exit()
        dump_data()
        sys.exit()
