#! /usr/bin/env python
#
#$Author: ee364b07 $
#$Date: 2011-04-29 10:14:45 -0400 (Fri, 29 Apr 2011) $
#$Revision: 24293 $
#$HeadURL: svn+ssh://ece364sv@ecegrid-lnx/home/ecegrid/a/ece364sv/svn/S11/students/ee364b07/Lab13/eceIRC-XP.py $
#$Id: eceIRC-XP.py 24293 2011-04-29 14:14:45Z ee364b07 $

import irclib
import sys
import string
import threading
from Tkinter import *
from tkMessageBox import * 
from tkSimpleDialog import *
from PIL import Image, ImageTk
import re
import getpass

# This program uses 2 image files
####################################
################GUI#################
####################################
#
# Doesnt clean after /part if you are in another channel
# Do I need Top of List and end of list???
# Sort list after '@' in channel :when u do +o

# Server Window
class ServerStatus(Tk):
    def __init__(Self):
        Tk.__init__(Self)
        Self.config(bg="white")
        Self.title('Server Status')
        Self.geometry('700x450+50+44')
        Self.entryChat = Entry(Self, foreground="green", bg="black", font=("Helvetica", 14, "bold"))
        Self.scroll = Scrollbar(Self, bg="white")
        Self.text = Text(Self, yscrollcommand=Self.scroll.set, bg="black", foreground="red", font=("Helvetica", 12))
        Self.scroll.config(command=Self.text.yview)
        Self.scroll.pack(side=RIGHT, fill=Y)
        Self.text.pack(fill=BOTH, side=TOP, expand=TRUE)
        Self.entryChat.pack(fill=X,side=BOTTOM, expand=FALSE)
        Self.entryChat.bind("<Return>", Self.Command)
        Self.protocol("WM_DELETE_WINDOW", closeMe)
	Self.text.config(state=DISABLED)
	
	Self.UserName = getpass.getuser()

	Self.topMenu = Menu(Self, bg='black', foreground='green')
	##Make sure about .config?##
	Self.config(menu=Self.topMenu)

	Self.fileMenu = Menu(Self)
	Self.fileMenu.add_command(label="Connect", command=Self.connectTo)
	Self.fileMenu.add_command(label="Disconnect", command=Self.disconnectFrom)
	Self.fileMenu.add_separator()
	Self.fileMenu.add_command(label="Select Server...", command=Self.askServer)
	Self.fileMenu.add_command(label="Exit", command=closeMe)
	Self.topMenu.add_cascade(label="File", menu=Self.fileMenu)

	Self.CommandMenu_Server = Menu(Self)
	Self.CommandMenu_Server.add_command(label="Get Channel Listing...", command=Self.callList)
	Self.CommandMenu_Server.add_command(label="Change Nick...", command=Self.askNick)
	Self.CommandMenu = Menu(Self)
	Self.CommandMenu.add_cascade(label="Server Related", menu=Self.CommandMenu_Server)

	Self.CommandMenu_Channel = Menu(Self)
	Self.CommandMenu_Channel.add_command(label="Join Channel...", command=Self.askJoinChannel)
	Self.CommandMenu_Channel.add_command(label="Part Channel...", command=Self.askPartChannel)
	Self.CommandMenu_Channel.add_separator()
	Self.CommandMenu_Channel.add_command(label="Kick User...", command=Self.askKick)
	Self.CommandMenu.add_cascade(label="Channel Related", menu=Self.CommandMenu_Channel)
	Self.topMenu.add_cascade(label="Commands", menu=Self.CommandMenu)

	Self.HelpMenu = Menu(Self)
	Self.HelpMenu.add_command(label="About", command=aboutIRC)
	Self.topMenu.add_cascade(label="Help", menu=Self.HelpMenu)	
	
	#Disable buttons	
	Self.fileMenu.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(1, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(4, state=DISABLED)
	Self.CommandMenu_Server.entryconfig(1, state=DISABLED)

    def callList(Self):
    	ChannelListWindow.ChannelName.delete(0, END)
        ChannelListWindow.deiconify()
	ChannelListWindow.lift()
        server.list()

    def askNick(Self):
	Temp = askstring("Nickname", "Enter you nickname:")
	if Temp == None:
	    showwarning("Error","No username was inputed!")
	    #Self.UserName = getpass.getuser()
	else:
	    if server.is_connected() == 0:
	        Self.UserName = Temp
	    elif server.is_connected() == 1:
		server.nick(Temp)
    def askKick(Self):
	kickChannel = askstring("Kick Channel", "Enter the name of channel you want to kick a client from:")
        kickNick = askstring("Kick Name", "Enter the name of client you want to kick:")
	kickReason = askstring("Kick Reason", "Enter the reason for kick:")
	if kickChannel == None or kickNick == None or kickReason == None:
	    showwarning("Error","Input all three elements!")
        server.kick(kickChannel, kickNick, kickReason)	
    def askPartChannel(Self):
	pChannel = askstring("Part Channel", "Enter a name of channel to part(leave):")
	if pChannel == None:
	    return
	server.part(pChannel)
        try:
            ChannelDic[pChannel].destroy()
        except KeyError:
            pass
        else:
            del ChannelDic[pChannel]

    def askJoinChannel(Self):
	jChannel = askstring("Join Channel", "Enter a name of channel to join:")
	if jChannel == None:
	    return
	elif (jChannel.lower() not in ChannelDic) and  (jChannel[0] == '#'):
            ChannelDic[jChannel.lower()] = Channel(jChannel)
            server.join(jChannel)
	elif jChannel.lower() in ChannelDic:
	    ChannelDic[jChannel.lower()].lift()
	
    def askServer(Self):
	Self.Address = askstring("Server", "Enter the server name:")

    def disconnectFrom(Self):
	#Disable buttons	
	Self.fileMenu.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(1, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(4, state=DISABLED)
	Self.CommandMenu_Server.entryconfig(1, state=DISABLED)
	for Key in ChannelDic.keys():
	    server.part(Key)
	    ChannelDic[Key].destroy()
	    del ChannelDic[Key]
	for Key in PrivateDic.keys():
	    PrivateDic[Key].destroy()
	    del PrivateDic[Key]
	server.disconnect()	

    def connectTo(Self):
	if Self.Address == None:
	    showwarning("Connection Error","No Server name has been provided")
	    return
	try:
	    server.connect(Self.Address, 6667, Self.UserName)
	except irclib.ServerConnectionError:
	    showwarning("Connection Error","Server doesnt exist! Try again")
	    Self.Address = 'ecegrid-lnx.ecn.purdue.edu'
	else:
	    Self.title("%s - %s" % (Self.UserName, Self.Address))
	
	#Enable buttons	
	Self.fileMenu.entryconfig(2, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(1, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(2, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(4, state=NORMAL)
	Self.CommandMenu_Server.entryconfig(1, state=NORMAL)

    def Command(Self, event):
        global ChannelDic
        String = Self.entryChat.get()
        
        if String == '':
            pass
        elif String[0] == '/':
            Temp = String.split()
            if len(Temp) == 2:
                if Temp[0] == '/join':
                    if (Temp[1].lower() not in ChannelDic) and  (Temp[1][0] == '#'):
                        ChannelDic[Temp[1].lower()] = Channel(Temp[1])
                        server.join(Temp[1])
                if Temp[0] == '/part':
                    server.part(Temp[1])
                    try:
                        ChannelDic[Temp[1]].destroy()
                    except KeyError:
                        pass
                    else:
                        del ChannelDic[Temp[1]]
            if Temp[0] == '/exit':
                closeMe() 
            elif Temp[0] == '/list':
    		ChannelListWindow.ChannelName.delete(0, END)
                ChannelListWindow.deiconify()
	        ChannelListWindow.lift()
                server.list()
            elif Temp[0] == '/kick':
                kickChannel = Temp[1]
                kickNick = Temp[2]
		kickReason = ' '.join(Temp[3:])
                server.kick(kickChannel, kickNick, kickReason)
	    elif Temp[0] == '/whois':
		usrList = Temp[1:]
		server.whois(usrList)
	    elif Temp[0] == '/mode':
		ChanName = Temp[1]
		String = ' '.join(Temp[2:])
		server.mode(ChanName, String)
	    elif Temp[0] == '/nick':
		newNick = Temp[1]
		if server.is_connected() == 0:
		    Self.UserName == newNick
		elif server.is_connected() == 1:
	            server.nick(newNick)
	    elif Temp[0] == '/server':
		server.disconnect()
		Self.Address = Temp[1]
		### DEFAULT USERNAME ###
		try:
		    server.connect(serverAddress, 6667, 'Umadbra')
		except irclib.ServerConnectionError:
		    showwarning("Connection Error","Server doesnt exist! Try again")
	    elif Temp[0] == '/topic':
		chanName = Temp[1]
		newTopic = ' '.join(Temp[2:])
		server.topic(chanName, newTopic)
	    elif Temp[0] == '/notice':
		noticeNick = Temp[1]
		noticeText = ' '.join(Temp[2:])
		server.notice(noticeNick, noticeText)
       		Self.text.config(state=NORMAL)
        	Self.text.tag_config("privnoticeChatSS", foreground="green", font=("Helvetica", 12,"bold"))
        	Self.text.insert(END, "-> -%s- %s\n" %(noticeNick, noticeText), "privnoticeChatSS")
        	Self.text.yview(END)
        	Self.text.config(state=DISABLED)
            elif Temp[0] == '/msg' and len(Temp) >= 3:
                Nick = Temp[1]
		skipChar = len(Temp[0]) + len(Nick) + 2
                Message = String[skipChar:]
		server.privmsg(Nick,Message)
                privmsgAction(Nick, Message,server.get_nickname())
        Self.entryChat.delete(0, END)

# Channel Window
class Channel(Toplevel):
    def __init__(Self, ChannelName):
        Toplevel.__init__(Self)

        Self.protocol("WM_DELETE_WINDOW", Self.partMe)
        Self.ChannelName = ChannelName
        Self.title(ChannelName)
        Self.scrollText = Scrollbar(Self, bg="light grey")
        Self.scrollName = Scrollbar(Self, bg="light grey")
        Self.text = Text(Self, yscrollcommand=Self.scrollText.set, bg="white", font=("Helvetica", 14))
        Self.scrollText.config(command=Self.text.yview)
        Self.entryChat = Entry(Self, bg="white", fg="blue", font=("Helvetica", 14))
        Self.name = Listbox(Self, bg="white", fg="maroon")
        Self.scrollName.config(command=Self.name.yview)
        Self.scrollName.pack(side=RIGHT, fill=Y)
        Self.name.pack(side=RIGHT, fill=Y)
        Self.scrollText.pack(side=RIGHT, fill=Y)
        Self.text.pack(fill=BOTH, side=TOP,expand=TRUE)
        Self.entryChat.pack(fill=X, side=BOTTOM, expand=FALSE)
        Self.entryChat.bind("<Return>", Self.MsgOrNot)
        Self.name.bind("<Double-Button-1>", Self.DoubleClick1)


	Self.text.config(state=DISABLED)
	
	#Self.UserName = getpass.getuser()

	Self.topMenu = Menu(Self, bg='black', foreground='green')
        Self.config(bg="white", cursor='circle',menu=Self.topMenu)

	Self.fileMenu = Menu(Self)
	Self.fileMenu.add_command(label="Connect", command=Self.connectTo)
	Self.fileMenu.add_command(label="Disconnect", command=Self.disconnectFrom)
	Self.fileMenu.add_separator()
	Self.fileMenu.add_command(label="Select Server...", command=Self.askServer)
	Self.fileMenu.add_command(label="Exit", command=closeMe)
	Self.topMenu.add_cascade(label="File", menu=Self.fileMenu)

	Self.CommandMenu_Server = Menu(Self)
	Self.CommandMenu_Server.add_command(label="Get Channel Listing...", command=Self.callList)
	Self.CommandMenu_Server.add_command(label="Change Nick...", command=Self.askNick)
	Self.CommandMenu = Menu(Self)
	Self.CommandMenu.add_cascade(label="Server Related", menu=Self.CommandMenu_Server)

	Self.CommandMenu_Channel = Menu(Self)
	Self.CommandMenu_Channel.add_command(label="Join Channel...", command=Self.askJoinChannel)
	Self.CommandMenu_Channel.add_command(label="Part Channel...", command=Self.askPartChannel)
	Self.CommandMenu_Channel.add_separator()
	Self.CommandMenu_Channel.add_command(label="Kick User...", command=Self.askKick)
	Self.CommandMenu.add_cascade(label="Channel Related", menu=Self.CommandMenu_Channel)
	Self.topMenu.add_cascade(label="Commands", menu=Self.CommandMenu)

	Self.HelpMenu = Menu(Self)
	Self.HelpMenu.add_command(label="About", command=aboutIRC)
	Self.topMenu.add_cascade(label="Help", menu=Self.HelpMenu)	
	
	#Disable buttons	
	Self.fileMenu.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(1, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(4, state=DISABLED)
	Self.CommandMenu_Server.entryconfig(1, state=DISABLED)

    def callList(Self):
    	ChannelListWindow.ChannelName.delete(0, END)
        ChannelListWindow.deiconify()
	ChannelListWindow.lift()
        server.list()

    def askNick(Self):
	Temp = askstring("Nickname", "Enter you nickname:")
	if Temp == None:
	    showwarning("Error","No username was inputed!")
	    #Self.UserName = getpass.getuser()
	else:
	    if server.is_connected() == 0:
	        Self.UserName = Temp
	    elif server.is_connected() == 1:
		server.nick(Temp)
    def askKick(Self):
	kickChannel = askstring("Kick Channel", "Enter the name of channel you want to kick a client from:")
        kickNick = askstring("Kick Name", "Enter the name of client you want to kick:")
	kickReason = askstring("Kick Reason", "Enter the reason for kick:")
	if kickChannel == None or kickNick == None or kickReason == None:
	    showwarning("Error","Input all three elements!")
        server.kick(kickChannel, kickNick, kickReason)	
    def askPartChannel(Self):
	pChannel = askstring("Part Channel", "Enter a name of channel to part(leave):")
	if pChannel == None:
	    return
	server.part(pChannel)
        try:
            ChannelDic[pChannel].destroy()
        except KeyError:
            pass
        else:
            del ChannelDic[pChannel]

    def askJoinChannel(Self):
	jChannel = askstring("Join Channel", "Enter a name of channel to join:")
	if jChannel == None:
	    return
	elif (jChannel.lower() not in ChannelDic) and  (jChannel[0] == '#'):
            ChannelDic[jChannel.lower()] = Channel(jChannel)
            server.join(jChannel)
	elif jChannel.lower() in ChannelDic:
	    ChannelDic[jChannel.lower()].lift()
	
    def askServer(Self):
	Self.Address = askstring("Server", "Enter the server name:")

    def disconnectFrom(Self):
	#Disable buttons	
	Self.fileMenu.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(1, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(4, state=DISABLED)
	Self.CommandMenu_Server.entryconfig(1, state=DISABLED)
	for Key in ChannelDic.keys():
	    server.part(Key)
	    ChannelDic[Key].destroy()
	    del ChannelDic[Key]
	for Key in PrivateDic.keys():
	    PrivateDic[Key].destroy()
	    del PrivateDic[Key]
	server.disconnect()
	
    def connectTo(Self):
	if Self.Address == None:
	    showwarning("Connection Error","No Server name has been provided")
	    return
	try:
	    server.connect(Self.Address, 6667, Self.UserName)
	except irclib.ServerConnectionError:
	    showwarning("Connection Error","Server doesnt exist! Try again")
	    Self.Address = 'ecegrid-lnx.ecn.purdue.edu'
	else:
	    Self.title("%s - %s" % (Self.UserName, Self.Address))
	
	#Enable buttons	
	Self.fileMenu.entryconfig(2, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(1, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(2, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(4, state=NORMAL)
	Self.CommandMenu_Server.entryconfig(1, state=NORMAL)





    def partMe(Self):
        global ChannelDic
        if askokcancel("Quit", "Do you really wish to quit?"):
            Self.destroy()
            server.part(Self.ChannelName)
            del ChannelDic[Self.ChannelName]

    def MsgOrNot(Self, event):
        global ChannelDic
        WinOpen = 1
        String = Self.entryChat.get()
        Temp = String.split()
        if Temp == []:
            pass
        elif String[0] != '/':
            server.privmsg(Self.ChannelName, String)
            Self.text.config(state=NORMAL)
            Self.text.tag_config("chat", foreground="blue")
            Self.text.insert(END, ("<%s> %s\n") % (server.get_nickname(), String), "chat")
            Self.text.yview(END)
            Self.text.config(state=DISABLED)
        elif Temp[0] == '/exit':
            closeMe() 
        elif Temp[0] == '/list':
	    ChannelListWindow.ChannelName.delete(0, END)
            ChannelListWindow.deiconify()
	    ChannelListWindow.lift()
            server.list()
        elif len(Temp) >= 2:
            if Temp[0] == '/join':
                if (Temp[1].lower() not in ChannelDic) and (Temp[1][0] == '#'):
                    ChannelDic[Temp[1].lower()] = Channel(Temp[1])
                    server.join(Temp[1])
            elif Temp[0] == '/kick':
                kickChannel = Temp[1]
                kickNick = Temp[2]
		kickReason = ' '.join(Temp[3:])
                server.kick(kickChannel, kickNick, kickReason)
	    elif Temp[0] == '/mode':
		ChanName = Temp[1]
		String = ' '.join(Temp[2:])
		server.mode(ChanName, String)
	    elif Temp[0] == '/whois':
		usrList = Temp[1:]
		server.whois(usrList)
	    elif Temp[0] == '/nick':
		newNick = Temp[1]
		server.nick(newNick)
	    elif Temp[0] == '/me':
		Text = ' '.join(Temp[1:])
		server.action(Self.ChannelName, Text)
	    	Self.text.config(state=NORMAL)
	    	Self.text.tag_config("action1", foreground="pink", font=("Helvetica", 12, "bold"))
	    	Self.text.insert(END, "*** %s %s\n" % (server.get_nickname(), Text), "action1")
 	   	Self.text.yview(END)
    		Self.text.config(state=DISABLED)
	    elif Temp[0] == '/topic':
		chanName = Temp[1]
		newTopic = ' '.join(Temp[2:])
		server.topic(chanName, newTopic)
            elif Temp[0] == '/msg':
                Nick = Temp[1]
    	        skipChar = len(Temp[0]) + len(Nick) + 2
                Message = String[skipChar:]
	        server.privmsg(Nick,Message)
                privmsgAction(Nick, Message,server.get_nickname())
	    elif Temp[0] == '/notice':
		noticeNick = Temp[1]
		noticeText = ' '.join(Temp[2:])
		server.notice(noticeNick, noticeText)
       		Self.text.config(state=NORMAL)
        	Self.text.tag_config("privnoticeChatChannel", foreground="green", font=("Helvetica", 12,"bold"))
        	Self.text.insert(END, "-> -%s- %s\n" %(noticeNick, noticeText), "privnoticeChatChannel")
        	Self.text.yview(END)
        	Self.text.config(state=DISABLED)
            elif Temp[0] == '/part':
                server.part(Temp[1])
                try:
                    ChannelDic[Temp[1]].destroy()
                except KeyError:
                    Self.entryChat.delete(0, END)
                    pass
                else:
                    del ChannelDic[Temp[1]]
                WinOpen = 0
        if WinOpen == 1:
            Self.entryChat.delete(0, END)

    def DoubleClick1(Self, event):
        global PrivateDic
        KeyList = []

        Sender = Self.name.get(ANCHOR)
	if Sender[0] == '@':
	    Sender = Sender[1:]
        for key in PrivateDic.keys():
	    KeyList.append(key.lower())
        if Sender.lower() not in KeyList:
            PrivateDic[Sender.lower()] = Private(Sender)
        else:
	    PrivateDic[Sender.lower()].lift()

# Channel Window
class Private(Toplevel):
    def __init__(Self, Name):
        Toplevel.__init__(Self)
        Self.config(bg="white", cursor='circle')
        Self.protocol("WM_DELETE_WINDOW", Self.partMe)
        Self.Name = Name
        Self.title(Name)
        Self.scrollText = Scrollbar(Self, bg="light grey")
        Self.text = Text(Self, yscrollcommand=Self.scrollText.set, bg="white", font=("Helvetica", 14))
        Self.scrollText.config(command=Self.text.yview)
        Self.entryChat = Entry(Self, bg="white", fg="blue", font=("Helvetica", 14))
        Self.scrollText.pack(side=RIGHT, fill=Y)
        Self.text.pack(fill=BOTH, side=TOP,expand=TRUE)
        Self.entryChat.pack(fill=X, side=BOTTOM, expand=FALSE)
        Self.entryChat.bind("<Return>", Self.MsgOrNot)
	Self.text.config(state=DISABLED)

	Self.topMenu = Menu(Self, bg='black', foreground='green')
	##Make sure about .config?##
	Self.config(menu=Self.topMenu)

	Self.fileMenu = Menu(Self)
	Self.fileMenu.add_command(label="Connect", command=Self.connectTo)
	Self.fileMenu.add_command(label="Disconnect", command=Self.disconnectFrom)
	Self.fileMenu.add_separator()
	Self.fileMenu.add_command(label="Select Server...", command=Self.askServer)
	Self.fileMenu.add_command(label="Exit", command=closeMe)
	Self.topMenu.add_cascade(label="File", menu=Self.fileMenu)

	Self.CommandMenu_Server = Menu(Self)
	Self.CommandMenu_Server.add_command(label="Get Channel Listing...", command=Self.callList)
	Self.CommandMenu_Server.add_command(label="Change Nick...", command=Self.askNick)
	Self.CommandMenu = Menu(Self)
	Self.CommandMenu.add_cascade(label="Server Related", menu=Self.CommandMenu_Server)

	Self.CommandMenu_Channel = Menu(Self)
	Self.CommandMenu_Channel.add_command(label="Join Channel...", command=Self.askJoinChannel)
	Self.CommandMenu_Channel.add_command(label="Part Channel...", command=Self.askPartChannel)
	Self.CommandMenu_Channel.add_separator()
	Self.CommandMenu_Channel.add_command(label="Kick User...", command=Self.askKick)
	Self.CommandMenu.add_cascade(label="Channel Related", menu=Self.CommandMenu_Channel)
	Self.topMenu.add_cascade(label="Commands", menu=Self.CommandMenu)

	Self.HelpMenu = Menu(Self)
	Self.HelpMenu.add_command(label="About", command=aboutIRC)
	Self.topMenu.add_cascade(label="Help", menu=Self.HelpMenu)	
	
	#Disable buttons	
	Self.fileMenu.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(1, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(4, state=DISABLED)
	Self.CommandMenu_Server.entryconfig(1, state=DISABLED)

    def callList(Self):
    	ChannelListWindow.ChannelName.delete(0, END)
        ChannelListWindow.deiconify()
	ChannelListWindow.lift()
        server.list()

    def askNick(Self):
	Temp = askstring("Nickname", "Enter you nickname:")
	if Temp == None:
	    showwarning("Error","No username was inputed!")
	    #Self.UserName = getpass.getuser()
	else:
	    if server.is_connected() == 0:
	        Self.UserName = Temp
	    elif server.is_connected() == 1:
		server.nick(Temp)
    def askKick(Self):
	kickChannel = askstring("Kick Channel", "Enter the name of channel you want to kick a client from:")
        kickNick = askstring("Kick Name", "Enter the name of client you want to kick:")
	kickReason = askstring("Kick Reason", "Enter the reason for kick:")
	if kickChannel == None or kickNick == None or kickReason == None:
	    showwarning("Error","Input all three elements!")
        server.kick(kickChannel, kickNick, kickReason)	
    def askPartChannel(Self):
	pChannel = askstring("Part Channel", "Enter a name of channel to part(leave):")
	if pChannel == None:
	    return
	server.part(pChannel)
        try:
            ChannelDic[pChannel].destroy()
        except KeyError:
            pass
        else:
            del ChannelDic[pChannel]

    def askJoinChannel(Self):
	jChannel = askstring("Join Channel", "Enter a name of channel to join:")
	if jChannel == None:
	    return
	elif (jChannel.lower() not in ChannelDic) and  (jChannel[0] == '#'):
            ChannelDic[jChannel.lower()] = Channel(jChannel)
            server.join(jChannel)
	elif jChannel.lower() in ChannelDic:
	    ChannelDic[jChannel.lower()].lift()
	
    def askServer(Self):
	Self.Address = askstring("Server", "Enter the server name:")

    def disconnectFrom(Self):
	#Disable buttons	
	Self.fileMenu.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(1, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(2, state=DISABLED)
	Self.CommandMenu_Channel.entryconfig(4, state=DISABLED)
	Self.CommandMenu_Server.entryconfig(1, state=DISABLED)
	for Key in ChannelDic.keys():
	    server.part(Key)
	    ChannelDic[Key].destroy()
	    del ChannelDic[Key]
	for Key in PrivateDic.keys():
	    PrivateDic[Key].destroy()
	    del PrivateDic[Key]
	server.disconnect()	

    def connectTo(Self):
	if Self.Address == None:
	    showwarning("Connection Error","No Server name has been provided")
	    return
	try:
	    server.connect(Self.Address, 6667, Self.UserName)
	except irclib.ServerConnectionError:
	    showwarning("Connection Error","Server doesnt exist! Try again")
	    Self.Address = 'ecegrid-lnx.ecn.purdue.edu'
	else:
	    Self.title("%s - %s" % (Self.UserName, Self.Address))
	
	#Enable buttons	
	Self.fileMenu.entryconfig(2, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(1, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(2, state=NORMAL)
	Self.CommandMenu_Channel.entryconfig(4, state=NORMAL)
	Self.CommandMenu_Server.entryconfig(1, state=NORMAL)







    def partMe(Self):
        global PrivateDic
        if askokcancel("Quit", "Do you really wish to quit?"):
            Self.destroy()
            del PrivateDic[Self.Name.lower()]

    def MsgOrNot(Self, event):
        global PrivateDic
        WinOpen = 1
        String = Self.entryChat.get()
        Temp = String.split()
        if Temp == []:
            pass
        elif String[0] != '/':
            privmsgAction(Self.Name, String)
	    server.privmsg(Self.Name, String)
        elif Temp[0] == '/exit':
            closeMe()
        elif Temp[0] == '/list':
	    ChannelListWindow.ChannelName.delete(0, END)
            ChannelListWindow.deiconify()
	    ChannelListWindow.lift()
            server.list()
        elif len(Temp) >= 2:
            if Temp[0] == '/join':
                if (Temp[1].lower() not in ChannelDic) and (Temp[1][0] == '#'):
                    ChannelDic[Temp[1].lower()] = Channel(Temp[1])
                    server.join(Temp[1])
            elif Temp[0] == '/kick':
                kickChannel = Temp[1]
                kickNick = Temp[2]
		kickReason = ' '.join(Temp[3:])
                server.kick(kickChannel, kickNick, kickReason)
	    elif Temp[0] == '/mode':
		ChanName = Temp[1]
		String = ' '.join(Temp[2:])
		server.mode(ChanName, String)
	    elif Temp[0] == '/whois':
		usrList = Temp[1:]
		server.whois(usrList)
	    elif Temp[0] == '/nick':
		newNick = Temp[1]
		server.nick(newNick)
	    elif Temp[0] == '/topic':
		chanName = Temp[1]
		newTopic = ' '.join(Temp[2:])
		server.topic(chanName, newTopic)
            elif Temp[0] == '/msg':
                Nick = Temp[1]
    	        skipChar = len(Temp[0]) + len(Nick) + 2
                Message = String[skipChar:]
	        server.privmsg(Nick,Message)
                privmsgAction(Nick, Message,server.get_nickname())
	    elif Temp[0] == '/notice':
		noticeNick = Temp[1]
		noticeText = ' '.join(Temp[2:])
		server.notice(noticeNick, noticeText)
       		Self.text.config(state=NORMAL)
        	Self.text.tag_config("privnoticeChatPrivate", foreground="green", font=("Helvetica", 12,"bold"))
        	Self.text.insert(END, "-> -%s- %s\n" %(noticeNick, noticeText), "privnoticeChatPrivate")
        	Self.text.yview(END)
        	Self.text.config(state=DISABLED)
            elif Temp[0] == '/part':
                server.part(Temp[1])
                try:
                    ChannelDic[Temp[1]].destroy()
                except KeyError:
                    Self.entryChat.delete(0, END)
                    pass
                else:
                    del ChannelDic[Temp[1]]
                WinOpen = 0
        if WinOpen == 1:
            Self.entryChat.delete(0, END)

class ShowChannels(Toplevel):
    def __init__(Self):
        Toplevel.__init__(Self)
	Self.mainList = []
        Self.config(bg="white", cursor='circle')
        Self.title("Channel Listing")
        Self.protocol("WM_DELETE_WINDOW", Self.exitWin)
        Self.geometry('550x400+50+44')
        Self.scroll = Scrollbar(Self, bg="light grey")
        Self.TopFrame = Frame(Self, bg="white")
	Self.Var = IntVar()
        #Self.TopFrame = Frame(Self,width=100, height=100, bg="", colormap="new")

        Self.ChannelName = Listbox(Self, yscrollcommand=Self.scroll.set,bg="white", foreground="darkgreen", font=("Helvetica", 12, "bold"))
	Self.ChannelName.bind("<Double-Button-1>", Self.DoubleClick2)
        Self.scroll.config(command=Self.ChannelName.yview)
        Self.filterBox = Entry(Self.TopFrame, bg="white")
	Self.FilterLabel = Label(Self.TopFrame, text="Filter", fg="red", bg="white")
        Self.CheckBox = Checkbutton(Self.TopFrame, text="Default Filter", command=Self.FilterCommand, variable=Self.Var,bg="white", foreground="cyan")
        Self.filterBox.bind("<Key>", Self.keyDookie)
        Self.TopFrame.pack(side=TOP)
        Self.FilterLabel.pack(side=LEFT) 
        Self.filterBox.pack(side=LEFT)
        Self.CheckBox.pack(side=LEFT)
        Self.ChannelName.pack(side=LEFT, fill=BOTH, expand=TRUE)
        Self.scroll.pack(side=LEFT, fill=Y)
	

    def keyDookie(Self, event):
	Self.CheckBox.deselect()
	Self.ChannelName.delete(0,END)
	if event.char != '\b':
	    String = Self.filterBox.get()+event.char
	else:
	    String = Self.filterBox.get()
	Reg_Ex = re.compile(String)
	for cName in Self.mainList:
	    if Reg_Ex.search(cName):
		Self.ChannelName.insert(END, cName)

    def exitWin(Self):
        if askokcancel("Quit", "Do you really wish to quit?"):
	    Self.CheckBox.deselect()
            Self.ChannelName.delete(0,END)
	    Self.mainList = []
	    Self.filterBox.delete(0,END)
            Self.withdraw()

    def FilterCommand(Self):
	Self.filterBox.delete(0,END)
	Self.ChannelName.delete(0,END)
	if Self.Var.get() == 1:
	    #Self.ChannelName.delete(0,END)
	    Reg_Ex = re.compile("#ece((0)?[4-9][0-9]|(0)?3[7-9]|[1-3][0-9][0-9]|4[0-2][0-9]|43[0-7])(\D).*")
	    for cName in Self.mainList:
		if Reg_Ex.match(cName):
		    Self.ChannelName.insert(END, cName)
		    
	elif Self.Var.get() == 0:
	    for cName in Self.mainList:
		Self.ChannelName.insert(END, cName)

    def DoubleClick2(Self, event):
        global ChannelDic

        ChannelName = Self.ChannelName.get(ANCHOR).split()[0]

        KeyList = []
        for key in ChannelDic.keys():
	    KeyList.append(key.lower())
	
	if ChannelName.lower() not in KeyList:
            ChannelDic[ChannelName.lower()] = Channel(ChannelName)
	    server.join(ChannelName)
        else:
	    ChannelDic[ChannelName.lower()].lift()
            #ChannelDic[ChannelName.lower()].withdraw()
            #ChannelDic[ChannelName.lower()].deiconify()


#########################################
############## FUNCTIONS ################
#########################################

def closeMe():
    if askokcancel("Quit", "Do you really wish to quit?"):
        die()

def curtopic(conn, event):
    global ChannelDic
    Target = event.arguments()[0]
    newTitle = Target + ' - ' + event.arguments()[1]
    if Target not in ChannelDic:
        return
    ChannelDic[Target].title(newTitle)

def newtopic(conn, event):
    global ChannelDic
    Target =  event.target()
    newTitle = Target + ' - ' + event.arguments()[0]
    if Target not in ChannelDic:
        return
    ChannelDic[Target].title(newTitle)

def listInsert(conn, event):
    global ChannelListWindow
    Chan = event.arguments()[0]
    Ref = event.arguments()[1]
    Topic = event.arguments()[2]
    WindowTopic = 'Channel listing for ' + event.source()
    #ChannelListWindow.ChannelName.delete(0, END)
    ChannelListWindow.ChannelName.insert(END, Chan+' '+Ref+Topic)
    ChannelListWindow.title(WindowTopic)
    ChannelListWindow.mainList.append(Chan + ' ' + Ref + ' ' + Topic)

def on_join(conn,event):
    global ChannelDic
  
    NameTemp = []
    Nick = event.source().split('!')[0]
    Target = event.target()
    Host = event.source().split('@')[1]
    if Target not in ChannelDic:
        return
    ChannelDic[Target].text.config(state=NORMAL)
    ChannelDic[Target].text.tag_config("joinChat", foreground="green4", font=("Helvetica", 12,"bold"))
    ChannelDic[Target].text.insert(END, "*** %s joined %s\n" %(event.source(), Target), "joinChat")
    ChannelDic[Target].text.yview(END)
    ChannelDic[Target].text.config(state=DISABLED)
    if Nick != server.get_nickname():
    	ChannelDic[Target].name.insert(END, Nick)
    NameList = ChannelDic[Target].name.get(0, END)
    for Name in NameList:
        NameTemp.append(Name)
    NameTemp.sort()
    ChannelDic[Target].name.delete(0, END)
    for Name in NameTemp:
        ChannelDic[Target].name.insert(END, Name)

def on_mode(conn,event):
    global ChannelDic
    
    Nick = event.source().split('!')[0]
    Action = event.arguments()[0]
    onUser = event.arguments()[1:]
    Target = event.target()
    NameList = ChannelDic[Target].name.get(0, END)
    ChannelDic[Target].name.delete(0, END)
    onUserList = ""

    for User in onUser:
        onUserList = onUserList + ' ' + User

    ChannelDic[Target].text.config(state=NORMAL)
    ChannelDic[Target].text.tag_config("modeChat", foreground="pink", font=("Helvetica", 12,"bold"))
    ChannelDic[Target].text.insert(END, "*** %s sets mode: %s %s\n" %(Nick, Action, onUserList), "modeChat")
    ChannelDic[Target].text.yview(END)
    ChannelDic[Target].text.config(state=DISABLED)
    
    for Name in NameList:
        if (Name in onUser) or (Name[1:] in onUser):
            if Action == '+o':
                ChannelDic[Target].name.insert(END, '@'+Name)
            elif Action == '-o':
                if Name[0] == '@':
                    Name = Name[1:]
                ChannelDic[Target].name.insert(END, Name)
            else:
                ChannelDic[Target].name.insert(END, Name)
        else:
            ChannelDic[Target].name.insert(END, Name)

def modeCommand(Channel, modeString):
    Nick = server.get_nickname()
    Action = modeString[0]
    onUserList = ' '.join(modeString[1:])
    ChannelDic[Channel].text.config(state=NORMAL)
    ChannelDic[Channel].text.tag_config("modeChat1", foreground="pink", font=("Helvetica", 12,"bold"))
    ChannelDic[Channel].text.insert(END, "*** %s sets mode: %s %s\n" %(Nick, Action, onUserList), "modeChat1")
    ChannelDic[Channel].text.yview(END)
    ChannelDic[Channel].text.config(state=DISABLED)

def on_kick(conn,event):
    Victim = event.arguments()[0]
    Reason = event.arguments()[1]
    myNick = event.source().split('!')[0]
    Target = event.target()
    myNick = server.get_nickname()
    kickCommand(Target, Victim, myNick, Reason)
    
    NameList = ChannelDic[Target].name.get(0, END)
    ChannelDic[Target].name.delete(0, END)

    for Name in NameList:
	if (Name != Victim) and (Name != ('@'+Victim)):
	    ChannelDic[Target].name.insert(END, Name)

def on_nick(conn,event):
    global ChannelDic
    oldNick = event.source().split('!')[0]
    newNick = event.target()
    
    for Channel in ChannelDic.keys():
	nameList = []
        for name in ChannelDic[Channel].name.get(0, END):
	    if name != oldNick and name[1:] != oldNick:
	        nameList.append(name)
	    else:
		if name[0] == '@':
		    newNick = '@' + newNick
	        nameList.append(newNick)
		nickCommand(oldNick, newNick, Channel)
        nameList.sort()
	ChannelDic[Channel].name.delete(0, END)
        for name2 in nameList:
            ChannelDic[Channel].name.insert(END, name2)

def nickCommand(oldNick, newNick, Channel):
	ChannelDic[Channel].text.config(state=NORMAL)
        ChannelDic[Channel].text.tag_config("nickChat1", foreground="cyan", font=("Helvetica", 12,"bold"))
        ChannelDic[Channel].text.insert(END, "*** %s is now know as %s\n" %(oldNick, newNick), "nickChat1")
        ChannelDic[Channel].text.yview(END)
        ChannelDic[Channel].text.config(state=DISABLED)

def kickCommand(Target, Victim, myNick, Reason):
    if myNick == Victim:
        if Target in ChannelDic:
            ChannelDic[Target].destroy()
            del ChannelDic[Target]
        RootWindow.text.config(state=NORMAL)
        RootWindow.text.tag_config("kickChat", foreground="green", font=("Helvetica", 12,"bold"))
        RootWindow.text.insert(END, "*** %s was kicked by %s (%s)\n" %(Victim, myNick, Reason), "kickChat")
        RootWindow.text.yview(END)
        RootWindow.text.config(state=DISABLED)
    else:
        ChannelDic[Target].text.config(state=NORMAL)
        ChannelDic[Target].text.tag_config("kickChat2", foreground="red", font=("Helvetica", 12,"bold"))
        ChannelDic[Target].text.insert(END, "*** %s was kicked by %s (%s)\n" %(Victim, myNick, Reason), "kickChat2")
        ChannelDic[Target].text.yview(END)
        ChannelDic[Target].text.config(state=DISABLED)

def on_chanoprivsneeded(conn, event):
    channel = event.arguments()[0]
    Message = event.arguments()[1]
    if channel in ChannelDic:
        ChannelDic[channel].text.config(state=NORMAL)
        ChannelDic[channel].text.tag_config("chanoprivs", foreground="red", font=("Helvetica", 12,"bold"))
        ChannelDic[channel].text.insert(END, "*** %s\n" % Message, "chanoprivs")
        ChannelDic[channel].text.yview(END)
        ChannelDic[channel].text.config(state=DISABLED)
    else:
        RootWindow.text.config(state=NORMAL)
        RootWindow.text.tag_config("chanoprivs3", foreground="red", font=("Helvetica", 12,"bold"))
        RootWindow.text.insert(END, "*** %s\n" %(Message), "chanoprivs3")
        RootWindow.text.yview(END)
        RootWindow.text.config(state=DISABLED)

def on_privnotice(conn,event):
    Message = event.arguments()[0]
    Nick = event.source().split('!')[0]
    myNick = event.target()    

    if myNick != 'AUTH':
        RootWindow.text.config(state=NORMAL)
        RootWindow.text.tag_config("privnoticeChat", foreground="white", font=("Helvetica", 12,"bold"))
        RootWindow.text.insert(END, "-%s- %s\n" %(Nick, Message), "privnoticeChat")
        RootWindow.text.yview(END)
        RootWindow.text.config(state=DISABLED)

def on_part(conn,event):
    global ChannelDic

    NameTemp = []
    Nick = event.source().split('!')[0]
    Target = event.target()
    
    if Target not in ChannelDic:
        return
    #Some sort of error when I did /part channel when in channel 
    NameList = ChannelDic[Target].name.get(0, END)
    newName = event.source()
    
    for Name in NameList:
        if Name[0] == '@':
            NameTemp.append(Name)
    
    ChannelDic[Target].text.config(state=NORMAL)
    ChannelDic[Target].text.tag_config("leaveChat", foreground="red4", font=("Helvetica", 12,"bold"))
    if '@' + Nick in NameTemp:
        ChannelDic[Target].text.insert(END, "*** @%s left %s\n" %(event.source(),event.target()), "leaveChat")
    else:
        ChannelDic[Target].text.insert(END, "*** %s left %s\n" %(event.source(),event.target()), "leaveChat")
    ChannelDic[Target].text.yview(END)
    ChannelDic[Target].text.config(state=DISABLED)
   
    NameList = ChannelDic[Target].name.get(0, END)
    ChannelDic[Target].name.delete(0, END)
    for Name in NameList:
        if Name[0] == '@':
            if Name[1:] != Nick:
                ChannelDic[Target].name.insert(END, Name)
        elif Name != Nick:
             ChannelDic[Target].name.insert(END, Name)

def on_whoisuser(conn, event):
    Nick = event.arguments()[0]
    usrName = event.arguments()[1]
    host = event.arguments()[2]
    star = event.arguments()[3]
    server = event.source()
    RootWindow.text.config(state=NORMAL)
    RootWindow.text.tag_config("whoisChat", foreground="cyan", font=("Helvetica", 12,"bold"))
    RootWindow.text.insert(END, "%s is %s@%s %s %s\n" %(Nick, usrName, host, star, usrName), "whoisChat")
    RootWindow.text.insert(END, "%s is using %s\n-----------\n" %(Nick, server), "whoisChat")
    RootWindow.text.yview(END)
    RootWindow.text.config(state=DISABLED)

def on_quit(conn, event):
    global ChannelDic
    NameList = []
    Nick = event.source().split('!')[0]
    
    for Key in ChannelDic.keys():
        for Name in ChannelDic[Key].name.get(0, END):
            if Name == Nick:
                ChannelDic[Key].text.config(state=NORMAL)
                ChannelDic[Key].text.tag_config("leaveIRC", foreground="maroon", font=("Helvetica", 12, "bold"))
                ChannelDic[Key].text.insert(END, "*** %s quit IRC\n" % (event.source()), "leaveIRC")
                ChannelDic[Key].text.yview(END)
                ChannelDic[Key].text.config(state=DISABLED)
                NameList = ChannelDic[Key].name.get(0, END)
                ChannelDic[Key].name.delete(0, END)
                for Name in NameList:
                    if Name != Nick:
                        ChannelDic[Key].name.insert(END, Name)

def on_action(conn, event):
    text = event.arguments()[0]
    Nick = event.source().split('!')[0]
    channel = event.target()

    ChannelDic[channel].text.config(state=NORMAL)
    ChannelDic[channel].text.tag_config("action1", foreground="pink", font=("Helvetica", 12, "bold"))
    ChannelDic[channel].text.insert(END, "*** %s %s\n" % (Nick, text), "action1")
    ChannelDic[channel].text.yview(END)
    ChannelDic[channel].text.config(state=DISABLED)

def userlist(conn, event):
    global ChannelDic
    channel_name = event.arguments()[1]
    NameList = event.arguments()[2].split()
    NameList.sort()
    for Name in NameList:
        ChannelDic[channel_name].name.insert(END, Name) 

def shandler(conn, event):
    global RootWindow
    RootWindow.text.config(state=NORMAL)
    RootWindow.text.insert(END, '*** ' + string.join(event.arguments(), ' ') + '\n')
    RootWindow.text.yview(END)
    RootWindow.text.config(state=DISABLED)

def pubmsg(conn, event):
    #nick!user@host
    global ChannelDic
    Nick = event.source().split('!')[0]
    Host = event.source().split('@')[1]
    Target = event.target()
    Message = event.arguments()[0]
    
    ChannelDic[Target].text.config(state=NORMAL)
    ChannelDic[Target].text.insert(END, "<%s> %s\n" % (Nick, Message))
    ChannelDic[Target].text.yview(END)
    ChannelDic[Target].text.config(state=DISABLED)

def privmsg(conn, event):
    global PrivateDic

    Sender = event.source().split('!')[0]
    Host = event.source().split('@')[1]
    Message = event.arguments()[0]
    KeyList = []
    for key in PrivateDic.keys():
	KeyList.append(key.lower())
    if Sender.lower() not in KeyList:
        PrivateDic[Sender.lower()] = Private(Sender)
    else:
	PrivateDic[Sender.lower()].lift()

    Sender1 = Sender.lower()
    PrivateDic[Sender1].text.config(state=NORMAL)
    PrivateDic[Sender1].text.tag_config("chat4", foreground="red")
    PrivateDic[Sender1].text.insert(END, "<%s> %s\n" % (Sender, Message), "chat4")
    PrivateDic[Sender1].text.yview(END)
    PrivateDic[Sender1].text.config(state=DISABLED)

def privmsgAction(Sender, Message, yourNick=""):
    global PrivateDic
    KeyList = []
    for key in PrivateDic.keys():
	KeyList.append(key.lower())
    if Sender.lower() not in KeyList:
        PrivateDic[Sender.lower()] = Private(Sender)
    else:
	PrivateDic[Sender.lower()].lift()
    yourNick = server.get_nickname()
    Sender1 = Sender.lower() 
    PrivateDic[Sender1].text.config(state=NORMAL)
    PrivateDic[Sender1].text.tag_config("chat", foreground="blue")
    PrivateDic[Sender1].text.insert(END, "<%s> %s\n" % (yourNick, Message), "chat")
    PrivateDic[Sender1].text.yview(END)
    PrivateDic[Sender1].text.config(state=DISABLED)

def spin():
    global done, irc
    while done == 0:
        irc.process_once(0.2)
    sys.exit(0)

def die():
    global done
    done = 1
    sys.exit(0)

#### Menu Functions ####
def aboutIRC():
    Text = "Welcome, This is an IRC client\nYou can connect to any IRC server\n\n\nMany hours has been put into this app\nto function properly\n\n\nThis is a freeware! Don't pay for it!"
    showinfo("IRC Client", Text)

def disconnect(conn, event):
    RootWindow.text.config(state=NORMAL)
    RootWindow.text.tag_config("disconnectNotice", foreground="white", font=("Helvetica", 12,"bold"))
    RootWindow.text.insert(END, "*** Disconnected.\n", "disconnectNotice")
    RootWindow.text.yview(END)
    RootWindow.text.config(state=DISABLED)

###################################
############### MAIN ##############
###################################

irc = irclib.IRC()              #Create IRC object
server = irc.server()           #Create IRC server off the irc object

exitImage = Image.open('exit.jpg')
connImage = Image.open('connect.jpg')

done = 0

thread1 = threading.Thread(target=spin)
thread1.start()

ChannelDic = {}
PrivateDic = {}

server.add_global_handler("yourhost", shandler)
server.add_global_handler("created", shandler)
server.add_global_handler("myinfo", shandler)
server.add_global_handler("featurelist", shandler)
server.add_global_handler("luserclient", shandler)
server.add_global_handler("luserop", shandler)
server.add_global_handler("luserchannels", shandler)
server.add_global_handler("luserme", shandler)
server.add_global_handler("n_local", shandler)
server.add_global_handler("n_global", shandler)
server.add_global_handler("luserconns", shandler)
server.add_global_handler("luserunknown", shandler)
server.add_global_handler("welcome", shandler)
server.add_global_handler("motd", shandler)
server.add_global_handler("topic", newtopic)
server.add_global_handler("currenttopic", curtopic)
server.add_global_handler("namreply", userlist)
server.add_global_handler("join", on_join)
server.add_global_handler("part", on_part)
server.add_global_handler("quit", on_quit)
server.add_global_handler("pubmsg", pubmsg)
#server.add_global_handler("liststart", listStart)
server.add_global_handler("list", listInsert)
#server.add_global_handler("listend", listInsert)
server.add_global_handler("privmsg", privmsg)
server.add_global_handler("mode", on_mode)
server.add_global_handler("kick", on_kick)
server.add_global_handler("privnotice", on_privnotice)
server.add_global_handler("nosuchnick", shandler)
server.add_global_handler("nosuchchannel", shandler)
server.add_global_handler("whoisuser", on_whoisuser)
server.add_global_handler("nick", on_nick)
#server.add_global_handler("endofwhois", on_endofwhois)
server.add_global_handler("action", on_action)
server.add_global_handler("chanoprivsneeded", on_chanoprivsneeded)
server.add_global_handler("disconnect", disconnect)

RootWindow = ServerStatus()
ChannelListWindow = ShowChannels()
ChannelListWindow.withdraw()

RootWindow.mainloop()
