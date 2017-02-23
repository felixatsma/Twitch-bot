import socket

user   = "catz0rzbot"
passwd = (open("passwd", "r")).read()
server = "irc.twitch.tv"
port   = 6667
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def irc_connect(server, port):
    print("connecting to: " + server + ":" + str(port))
    irc.connect((server, port))
    irc.send(("USER - - - :-\n").encode())
    irc.send(("PASS " + passwd + "\n").encode())
    irc.send(("NICK " + user + "\n").encode())
    irc.send(("JOIN #sir_catz0rz\n").encode())
    response = irc.recv(2040)
    print(response.decode('unicode_escape'))

def irc_input():
    quit = False
    while not quit:
        command = input("-> ")
        if command == "q" or command == "x":
            quit = True
            break
        irc.send(("PRIVMSG #sir_catz0rz :" + command + "\n").encode())

def irc_exit():
    irc.send(("PART $sir_catz0rz\n").encode())
    irc.send(("QUIT\n").encode())
    irc.close()

def main():
    irc_connect(server, port)
    irc_input()
    irc_exit

if __name__ == "__main__":
    main()
