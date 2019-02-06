#!/usr/bin/env python3

import sys
import socket
import re
import time
import json

class Twitch_bot:
    def __init__(self, data_file):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.data_file = data_file
        self.command_dict, self.data = self.load_data()

    def load_data(self):
        """
        Loads data from data.json into dictionaries.
        """
        with open(self.data_file) as f:
            file = json.load(f)

        command_dict = file["commands"]
        data = file["data"]

        return command_dict, data

    def dump_data(self):
        """
        Dumps (potentially updated) data from dictionaries in data.json when the
        bot is closed.
        """
        with open(self.data_file, "w") as f:
            json.dump({"data": self.data, "commands": self.command_dict}, f)


    def irc_connect(self):
        """
        Connects to the Twitch irc servers, to the channel specified in 'chan'
        Prints the response to the attempted connection, this should just be the
        Twitch welcome message.
        """
        print("connecting to : " + self.data["server"] + ":" + str(self.data["port"]))
        print("channel       : " + self.data["chan"])
        self.irc.connect((self.data["server"], self.data["port"]))
        self.irc.send(("USER %s - - :%s\n" % (self.data["user"],
                                              self.data["user"])).encode())
        self.irc.send(("PASS " + self.data["passwd"] + "\n").encode())
        self.irc.send(("NICK " + self.data["user"] + "\n").encode())
        self.irc.send(("JOIN " + self.data["chan"] + "\n").encode())
        response = self.irc.recv(2040)
        print(response.decode('unicode_escape'))
        self.send("/me is now online")


    def send(self, msg):
        """
        Posts a message in the connected channel.
        """
        self.irc.send(("PRIVMSG %s :%s\n" % (self.data["chan"],
                                              msg)).encode())
        print("%s\t: %s" % (self.data["user"], msg))


    def irc_read(self):
        """
        Read loop that reads messages posted in the channel and recovers the
        username and message.
        Commands are processed in here.
        """
        regex = re.compile(r'^:([^\s]+)!.*#[^\s]+ :(.*)\r\n$')

        print("Chat:")
        while True:
            chat = self.irc.recv(2040)
            mesg = regex.findall(chat.decode())

            if len(mesg) != 0:
                usr = mesg[0][0]
                txt = mesg[0][1].split()[0]
                args = mesg[0][1].split()[1:]

                if (len(str(usr)) > 7):
                    print(str(usr) + "\t: " + str(txt))
                else:
                    print(str(usr) + "\t\t: " + str(txt))

                if txt in self.command_dict:
                    self.send(self.command_dict[txt])
                elif txt == "!time":
                    self.send(time.asctime(time.localtime(time.time())))
                elif txt == "!birthday":
                    self.send("Happy birthday " + usr + "!")

                # Mod commands
                if txt[0] == "!" and usr == self.data["owner"] or usr in self.data["mods"]:
                    print(txt)
                    if txt == "!stop":
                        self.send("/me is now offline")
                        print("User " + str(usr) + " called !stop")
                        break
                    elif txt == "!addmod":
                        if args[0] in self.data["mods"]:
                            self.send("User is already mod!")
                        else:
                            self.data["mods"].append(args[0])
                            self.send("Mod added")
                    elif txt == "!addcom":
                        self.command_dict["!" + args[0]] = " ".join(args[1:])
                        self.send("Command added")


    def irc_exit(self):
        """
        Closes the irc connection.
        """
        print("exiting...")
        self.irc.send(("PART $%s\n" % self.data["chan"][1:]).encode())
        self.irc.send(("QUIT\n").encode())
        self.irc.close()


    def run(self):
        """
        Initializes connection and read loop.
        If an exception occurs, it neatly exits and stores new commands.
        """
        try:
            self.load_data()
            self.irc_connect()
            self.irc_read()
            self.irc_exit()
            self.dump_data()
        except KeyboardInterrupt:
            self.send("/me is now offline")
            self.irc_exit()
            self.dump_data()
        except Exception as e:
            print("ERROR: ", e)
            self.send("/me is now offline")
            self.irc_exit()
            self.dump_data()


if __name__ == "__main__":
    bot = Twitch_bot('data.json')
    bot.run()
