# MIT License

# Copyright (c) 2022 bleach86, tuxprint#5176

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from tkinter import *
from tkinter import font, ttk, messagebox
from tooltip import ToolTip
import threading
import time
import re
from pygame import mixer
import pyperclip
import os
from datetime import datetime
import emoji
import names, tcinit
from tkinter.scrolledtext import ScrolledText
import platform

def settings():
    with open('settings.json') as f:
        settings = json.loads(f.read())
    return settings
    
with open("emote.json", 'r', encoding='utf-8') as e:
    emote = json.loads(e.read())
emoteList = emote

rpcproxy2 = AuthServiceProxy(f"http://{settings()['rpcConnection']['username']}:{settings()['rpcConnection']['password']}@{settings()['rpcConnection']['ip']}:{settings()['rpcConnection']['port']}")

version = 'v0.18-alpha'



def rpcproxy():
    rpcproxy = AuthServiceProxy(f"http://{settings()['rpcConnection']['username']}:{settings()['rpcConnection']['password']}@{settings()['rpcConnection']['ip']}:{settings()['rpcConnection']['port']}")
    
    return rpcproxy

focus = True

def getNames():
    with open('names.json') as f:
        screenNames = json.loads(f.read())
    return screenNames

def getBlocked():
    with open('blocklist.json') as f:
        blocked = json.loads(f.read())
    return blocked

def getMessages():
    global seenTX
    global bestBlock
    message = []
    currentHeight = rpcproxy2.getblockcount() +1
    for i in range(bestBlock, currentHeight):
        hash = rpcproxy2.getblockhash(i)
        block = rpcproxy2.getblock(hash)
        
        for txid in block['tx']:
            if txid in seenTX:
                seenTX.remove(txid)
                continue
            tx = rpcproxy2.getrawtransaction(txid, True)
            
            if 'coinbase' in tx['vin'][0]:
                #print('coinbase bitches')
                continue
                
            for i in tx['vout']:
                
                if 'OP_RETURN' in i['scriptPubKey']['asm']:
                    #print('message bitches')
                    
                    msg = i['scriptPubKey']['hex']
                    msgBytes = bytes.fromhex(msg[8:])
                    try:
                        try:
                            msgString = msgBytes.decode("UTF-8")
                        except:
                            try:
                                msgBytes = bytes.fromhex(msg[10:])
                                msgString = msgBytes.decode("UTF-8")
                            except:
                                msgBytes = bytes.fromhex(msg[12:])
                                msgString = msgBytes.decode("UTF-8")
                        msgString = json.loads(msgString)
                        if msgString['addr'] in getBlocked()['blackList']:
                            continue

                        verify = rpcproxy2.verifymessage(msgString['addr'], msgString['sig'], msgString['message'] + str(msgString['time']) + str(msgString['rm']))
                        
                        if msgString['rm'] == settings()['room'].strip() and verify == True:
                            msgString['txid'] = txid
                            message.append(msgString)

                        print(msgString)
                        if verify == True:
                            print("Signature Verified")
                        else:
                            print("Signature not verified")
                    
                    except:
                        continue
                        #print(msgBytes)
                        
                        
    mempool = rpcproxy2.getrawmempool()
    
    for txid in mempool:
        if txid in seenTX:
            continue
        
        tx = rpcproxy2.getrawtransaction(txid, True)
            
        for i in tx['vout']:
                
            if 'OP_RETURN' in i['scriptPubKey']['asm']:
                #print('message bitches')
                
                msg = i['scriptPubKey']['hex']
                msgBytes = bytes.fromhex(msg[8:])
                try:
                    
                    try:
                        msgString = msgBytes.decode("UTF-8")
                    except:
                        try:
                            msgBytes = bytes.fromhex(msg[10:])
                            msgString = msgBytes.decode("UTF-8")
                        except:
                            msgBytes = bytes.fromhex(msg[12:])
                            msgString = msgBytes.decode("UTF-8")
                    msgString = msgBytes.decode("UTF-8")
                    msgString = json.loads(msgString)
                    if msgString['addr'] in getBlocked()['blackList']:
                            continue
                            
                    verify = rpcproxy2.verifymessage(msgString['addr'], msgString['sig'], msgString['message'] + str(msgString['time']) + str(msgString['rm']))
                        
                    if msgString['rm'] == settings()['room'].strip() and verify == True:
                        msgString['txid'] = txid
                        message.append(msgString)
                    
                    print(msgString)
                    if verify == True:
                        print("Signature Verified")
                    else:
                        print("Signature not verified")
                
                except:
                    continue
                    #print(msgBytes)
        seenTX.append(txid)
    
    bestBlock = currentHeight
    return(sorted(message, key=lambda d: d['time']))
                    

def subEmotes(msg):
    msg = emoji.emojize(msg, use_aliases=True)
    emote = emoteList
    if settings()['subEmotes'] == True:
        for i in emote:
            if i in msg:
                msg = msg.replace(i, emote[i])
    
    return msg

def subName(addr, info=False):
    
    if addr in getNames():
        if getNames()[addr]['name'] == "":
            return addr
        elif addr in getBlocked()['hideName'] and info == False:
            return addr 
        else:
            return getNames()[addr]['name']
    else:
        return addr

def subColor(addr):
    
    if addr in getNames():
        return getNames()[addr]['color']
    else:
        return 'white'

class GUI:
    # constructor method
    def __init__(self):
        self.focus = focus
        self.lastMsg = 0
        with open('settings.json') as f:
            settings = json.loads(f.read())
        
        self.settings = settings
        
        if self.settings['mute'] == False:
            mixer.init()
            ps = mixer.Sound('pop-alert.ogg')
            self.ps = ps
        
        self.json = json
        self.rpcproxy = rpcproxy
        self.masterMsg = []
       
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
         
        
        if self.settings['enterToSend'] == True:
            self.Window.bind("<Return>", self.enterbtn)
            self.Window.bind("<Shift-Return>", self.shiftenterbtn)
        self.Window.bind("<FocusIn>", self.focusIn)
        self.Window.bind("<FocusOut>", self.focusOut)
        self.Window.bind("<Button-3>", self.rightClick)
        self.Window.bind("<Button-1>", self.leftClick)
        self.Window.protocol("WM_DELETE_WINDOW", self.onClose)
        self.goAhead(subName(self.settings['signingAddress']))
        if os.name == 'nt':
            self.Window.iconbitmap('tuxchat-logo.ico')
        else:
            self.Window.call('wm', 'iconphoto', self.Window._w, PhotoImage(file='tuxchat-logo.png'))
        
        self.Window.mainloop()
        
 
    def goAhead(self, name):
        self.layout(name)
         
        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()
 
    # The main layout of the chat
    def layout(self,name):
       
        self.name = name
        if len(name) > 24:
            dots = '...'
        else:
            dots = ''
        # to show chat window
        self.Window.deiconify()
        self.Window.title(f"Tuxcoin blockchain messaging interface | {version}")
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(
                              bg = "#17202A")
        self.labelHead = Label(self.Window,
                             bg = "#17202A",
                              fg = "#EAECEE",
                              text = f"{self.name[0:24]}{dots} | {self.settings['room'].strip()}",
                              font = ("Noto", 13, "bold"),
                              pady = 5)
         
        self.labelHead.pack(side=TOP)
         
        self.textCons = ScrolledText(self.Window,
                             bg = "#17202A",
                             fg = "#EAECEE",
                             font = ("Noto", 14),
                             width=50,
                             padx = 5,
                             pady = 5,
                             wrap=WORD)
         
        self.textCons.pack(fill=BOTH, side=TOP, padx=5, pady=5, anchor="w")
         
        self.entryMsg = ScrolledText(self.Window,
                              width=50,
                              height=4,
                              padx=5,
                              pady=5,
                              bg = "#2C3E50",
                              fg = "#EAECEE",
                              font = ("Noto", 13),
                              wrap=WORD)
         
        # place the given widget
        # into the gui window
        self.entryMsg.pack(side=LEFT, anchor="w", padx=5, pady=5)
         
        self.entryMsg.focus()
         
        # create a Send Button
        self.buttonMsg = Button(self.Window,
                                text = "Send",
                                font = ("Noto", 10, "bold"),
                                bg = "#17202A",
                                fg = "#EAECEE",
                                width=11,
                                height=1,
                                bd=0,
                                command = lambda : self.sendButton(re.sub(r'[\r\n][\r\n]{2,}', '\n\n', self.entryMsg.get(1.0, "end-1c"))))
        
        self.buttonMsg.pack(side=BOTTOM, anchor="w", pady=5)
                             
        self.buttonSetting = Button(self.Window,
                                text = "Settings",
                                font = ("Noto", 10, "bold"),
                                width = 10,
                                height=1,
                                bg = "#17202A",
                                fg = "#EAECEE",
                                bd=0,
                                command = self.settingsBtn)
        
        self.buttonSetting.pack(side=BOTTOM, anchor="w", pady=5, ipadx=3)
        ToolTip(widget = self.buttonSetting, text = "Change tuxchat settings, including screen name, here.")
        
        self.labelFoot = Label(self.Window,
                            bg = "#17202A",
                             fg = "#EAECEE",
                              text = f"Balance: {rpcproxy().getbalance():,}")
         
        self.labelFoot.pack(side=BOTTOM, anchor="w", padx=5)

        self.textCons.config(cursor = "arrow")
        
         
        self.textCons.config(state = DISABLED)
        
        self.rcMenu = Menu(self.Window, tearoff=0)
        
        self.rcMenu.add_command(label ="Cut", command=self.cut)
        self.rcMenu.add_command(label ="Copy", command=self.copy)
        self.rcMenu.add_command(label ="Paste", command=self.paste)
        
    def updateName(self):
        if self.name != subName(settings()['signingAddress']):
            self.name = subName(settings()['signingAddress'])
            if len(self.name) > 24:
                dots = '...'
            else:
                dots = ''
            self.labelHead['text'] = f"{self.name[0:24]}{dots} | {settings()['room'].strip()}"
    
    def updateBalance(self):
        tnow = datetime.now()
        
        if tnow.second % 10 == 0:
            self.labelFoot['text'] = f"Balance: {rpcproxy().getbalance():,}"
     
    def rightClick(self, event):
        try:
            self.rcMenu.tk_popup(event.x_root, event.y_root)
        finally:
            self.rcMenu.grab_release()
            
    def leftClick(self, event):
        try:
            self.rcMenu.unpost()
        except:
            pass
    
    def settingsBtn(self):
        self.buttonSetting.config(state='disabled')
        self.popup = Tk()
        self.popup.wm_title("Tuxchat Settings")
        self.addrLabel = Label(self.popup, text="Signing Address: ", font=("Noto", 10, "bold"))
        self.addrLabel.grid(row=1, column=1, pady=10)
        
        self.addrEntry = Entry(self.popup, width=36)
        self.addrEntry.grid(row=1, column=2)
        self.addrEntry.insert(END, settings()['signingAddress'])
        
        self.addrBtn = Button(self.popup, text='Submit', command = lambda : self.setAddr(self.addrEntry.get()))
        self.addrBtn.grid(row=1, column=5)
        
        self.nameLabel = Label(self.popup, text="Screen Name: ", font=("Noto", 10, "bold"))
        self.nameLabel.grid(row=2, column=1, pady=10)
        
        self.nameEntry = Entry(self.popup, width=36)
        self.nameEntry.grid(row=2, column=2)
        self.nameEntry.insert(END, self.name)
        
        colorChoice = settings()['colors']
        selectedChoice = StringVar()
        self.colorCombo = ttk.Combobox(self.popup, textvariable=selectedChoice, width=10)
        
        self.colorCombo['values'] = colorChoice
        self.colorCombo.current(colorChoice.index(subColor(settings()['signingAddress'])))
        self.colorCombo.grid(row=2, column=4, sticky="W")
        
        self.colorLabel = Label(self.popup, text="Color:", font=("Noto", 10, "bold"))
        self.colorLabel.grid(row=2, column=3, sticky='W')
        
        self.nameBtn = Button(self.popup, text='Submit', command = lambda : self.setName(self.nameEntry.get(), self.colorCombo.get()))
        self.nameBtn.grid(row=2, column=5)
        
        self.roomLabel = Label(self.popup, text="Room: ", font=("Noto", 10, "bold"))
        self.roomLabel.grid(row=3, column=1, pady=10)
        
        roomChoice = settings()['roomHistory']
        selectedRoomChoice = StringVar()
        self.roomCombo = ttk.Combobox(self.popup, textvariable=selectedRoomChoice)
        
        self.roomCombo['values'] = roomChoice[::-1]
        self.roomCombo.current(0)
        self.roomCombo.grid(row=3, column=2, sticky="W")
        
        self.roomBtn = Button(self.popup, text='Refresh/Submit', command = lambda : self.newRoom(self.roomCombo.get()))
        self.roomBtn.grid(row=3, column=5)
        
        self.blLabel = Label(self.popup, text="Blacklist: ", font=("Noto", 10, "bold"))
        self.blLabel.grid(row=4, column=1, pady=10)
        
        blChoice = getBlocked()['blackList']
        selectedRoomChoice = StringVar()
        self.blCombo = ttk.Combobox(self.popup, textvariable=selectedRoomChoice, width=36)
        
        self.blCombo['values'] = blChoice
        self.blCombo.grid(row=4, column=2, sticky="W")
        
        self.blBtn = Button(self.popup, text='Submit', command = lambda : self.rmBlackList(self.blCombo.get()))
        self.blBtn.grid(row=4, column=5)
        
        self.settingsDisable()
    
        self.B1 = ttk.Button(self.popup, text="Close", command = self.killPopup)
        self.B1.grid(row=5, column=2)
        self.B2 = ttk.Button(self.popup, text="Edit", command = self.settingsEdit)
        self.B2.grid(row=5, column=3)
        ToolTip(widget = self.addrLabel, text = "Address used to sign messages with.\nLeave blank to generate new random address.")
        ToolTip(widget = self.nameLabel, text = "Your screen name.")
        ToolTip(widget = self.colorLabel, text = "The color of your screen name.")
        ToolTip(widget = self.roomLabel, text = "The current room that you are in. To change either make a selectin from the dropdown, or type the name of a room in.")
        ToolTip(widget = self.blLabel, text = "The current blacklist. Addresses can be removed from the list through this.")
        self.popup.protocol("WM_DELETE_WINDOW", self.killPopup)
        
        self.popup.mainloop()
    
    def newRoom(self, room):
        room = room.strip()
        
        if room in settings()['roomHistory']:
            with open('settings.json', 'r+') as f:
                data = json.load(f)
                data['room'] = room
                data['roomHistory'].remove(room)
                data['roomHistory'].append(room)
                f.seek(0)
                json.dump(data, f, indent = 4)
                f.truncate()
            self.textCons.config(state = NORMAL)
            self.textCons.delete(1.0, END)
            self.textCons.config(state = DISABLED)
            setBlock()
            self.masterMsg = []
            
            if len(self.name) > 24:
                dots = '...'
            else:
                dots = ''
            self.labelHead['text'] = f"{self.name[0:24]}{dots} | {settings()['room'].strip()}"
            self.killPopup()
            
        else:
            with open('settings.json', 'r+') as f:
                data = json.load(f)
                data['room'] = room
                data['roomHistory'].append(room)
                f.seek(0)
                json.dump(data, f, indent = 4)
                f.truncate()
            self.textCons.config(state = NORMAL)    
            self.textCons.delete(1.0, END)
            self.textCons.config(state = DISABLED)
            setBlock()
            self.masterMsg = []
            
            if len(self.name) > 24:
                dots = '...'
            else:
                dots = ''
            self.labelHead['text'] = f"{self.name[0:24]}{dots} | {settings()['room'].strip()}"
            self.killPopup()
                
    
    def settingsDisable(self):
        self.addrEntry.config(state='readonly')
        self.addrBtn.config(state='disabled')
        self.nameEntry.config(state='readonly')
        self.colorCombo.config(state='disabled')
        self.nameBtn.config(state='disabled')
        self.blCombo.config(state='disabled')
        self.blBtn.config(state='disabled')
    
    def settingsEdit(self):
        confirm = messagebox.askyesno("Confirmation", "Are you sure you want to edit settings?")
        
        if confirm:
            self.B2.config(state='disabled')
            self.addrEntry.config(state='normal')
            self.addrBtn.config(state='normal')
            self.nameEntry.config(state='normal')
            self.colorCombo.config(state='readonly')
            self.nameBtn.config(state='normal')
            self.blCombo.config(state='readonly')
            self.blBtn.config(state='normal')
            self.popup.lift()
        else:
            self.popup.lift()
    
    def killPopup(self):
        self.buttonSetting.config(state='normal')
        self.popup.destroy()
    
    def setName(self, name, color):
        if color == "":
            messagebox.showwarning("Warning", f"Please select a color")
            return
        name = ''.join(name.split())
        if len(name) > 30:
            messagebox.showwarning("Warning -Name too long", f"Name too long.\nPlease choose a name that is 30 characters or less.")
            return
        elif name == subName(settings()['signingAddress']) and color == subColor(settings()['signingAddress']):
            return
            
        elif name.upper() in getNames()['nameList'] and name.upper() != subName(settings()['signingAddress']).upper():
            messagebox.showwarning("Warning -Name already in use", f"Name already in use, please choose a different name.")
            return
            
        else:
            verify = messagebox.askyesno("Confirmation", f"Are you sure you want to use the name: {name} with the color: {color}?")
            if verify:
                signature = {}
                timestamp = int(time.time())
                addr = settings()['signingAddress']
                
                sig = rpcproxy().signmessage(addr, name + str(timestamp))
                
                signature['addr'] = addr
                signature['sig'] = sig
                
                message = {'message': name, 'sig': signature['sig'], 'addr': signature['addr'], "nameRequest": color, "time": timestamp}
        
                try:
                    req = rpcproxy().sendmessage(json.dumps(message))
                    messagebox.showinfo("Information", f"Name request successfully submitted.\nName request must be included in a block to take affect.\nTXID: {req}")
                    self.killPopup()
                    
                except Exception as e:
                    print(e)
                
                print("Name request successfully submitted. Please allow a few minutes for name change to take affect.")
                
    def setAddr(self, addr):
        if addr == '':
                addr = rpcproxy().getnewaddress("", "legacy")
        
        if validateAddress(addr)[0] == False:
            messagebox.showwarning("Warning", f"{validateAddress(addr)[1]}")

            
        elif addr == settings()['signingAddress']:
            return
        
        else:
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to use the address: {addr}")
            
            if confirm:
                
                with open('settings.json', 'r+') as f:
                    data = json.load(f)
                    data['signingAddress'] = addr
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                self.addrEntry.delete(0, END)
                self.addrEntry.insert(END, settings()['signingAddress'])
                messagebox.showinfo("INFO", f"Address successfully updated.")
            self.killPopup()
 
    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.msg = msg
        if validateAddress(settings()['signingAddress']) == False or settings()['signingAddress'] == '':
            messagebox.showerror("ERROR", f"Valid signing address not found!\nPlease add a valid signing address in settings!")
            return
        
        if self.checkBytes(self.msg) == False:
            return
        
        if rpcproxy().getbalance() < 1:
            messagebox.showerror("ERROR", f"Low Balance!")
            return
        
        self.textCons.config(state = DISABLED)
        self.entryMsg.delete(1.0, END)
        snd= threading.Thread(target = self.sendMessage)
        snd.start()
        
        self.buttonMsg.config(state='disabled')
        self.buttonMsg.after(1000, lambda: self.buttonMsg.config(state='normal'))
        
    def checkBytes(self, msg):
        msgLen = len(msg.strip().encode('raw_unicode_escape'))
        roomLen = len(settings()['room'].strip().encode('raw_unicode_escape'))
        metaLen = roomLen + 190
        maxLen = 1010 - metaLen
        totalLen = msgLen + metaLen
        
        #print(msgLen)
        #print(totalLen)
        
        if totalLen > 1010:
            messagebox.showwarning("Warning", f"Message exceeds maximum possible Bytes.\nMax Possible: {maxLen}\nYour message: {msgLen}")
            return False
        else:
            return True
    
    def getInfo(self, event):
        thing = self.textCons.index(f"@{event.x},{event.y}"), self.textCons.index("current")
        #print(thing)
        thing = thing[0]
        
        for i in reversed(self.masterMsg):
            if i['index'] == int(float(thing)):
                self.popinfo = Tk()
                self.popinfo.wm_title("Message Info")
                label = Text(self.popinfo)
                label.grid(row=1, column=1, columnspan=10, rowspan=10, pady=10)
                label.insert(END, f"Sender: {i['addr']}\nScreen name: {subName(i['addr'], True)}\nRoom: {i['rm']}\nSignature: {i['sig']}\nTXID: {i['txid']}\nTimestamp: {i['time']}\nMessage Time: {datetime.fromtimestamp(i['time'])}\nMessage:\n{i['message']}")
                label.config(state = DISABLED)
                if i['addr'] in getBlocked()['blockList']:
                    B2text = "Unblock"
                else:
                    B2text = "Block"
                    
                if i['addr'] in getBlocked()['hideName']:
                    B4text = "Unhide Name"
                else:
                    B4text = "Hide Name"
                
                B1 = ttk.Button(self.popinfo, text="Close", command = self.popinfo.destroy)
                B1.grid(row=11, column=3)
                B2 = ttk.Button(self.popinfo, text=B2text, command = lambda : self.addBlock(i['addr']))
                B2.grid(row=11, column=4)
                B3 = ttk.Button(self.popinfo, text="Blacklist", command = lambda : self.addBlackList(i['addr']))
                B3.grid(row=11, column=5)
                B4 = ttk.Button(self.popinfo, text=B4text, command = lambda : self.addHideName(i['addr']))
                B4.grid(row=11, column=6)
                
                self.popinfo.mainloop()
                
                break
        return "break"
    
    def addHideName(self, addr):
        if addr == settings()['signingAddress']:
            return
        elif addr in getBlocked()['hideName']:
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want unhide the following name From user\n{addr}")
        
            if confirm:
                with open('blocklist.json', 'r+') as f:
                    data = json.load(f)
                    data['hideName'].remove(addr)
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                    f.truncate()
                messagebox.showinfo("Information", f"Successfully unhidden name.")
                self.popinfo.destroy()
            
        else:    
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want hide the following name\n{subName(addr)}\nFrom user\n{addr}")
            
            if confirm:
                with open('blocklist.json', 'r+') as f:
                    data = json.load(f)
                    data['hideName'].append(addr)
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                    f.truncate()
                messagebox.showinfo("Information", f"Successfully hidden name.")
                self.popinfo.destroy()
    
    def rmBlackList(self, addr):

        if addr in getBlocked()['blackList']:
            
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to remove\nADDR: {addr}\nScreen Name: {subName(addr)}\n from the black list?")
            
            if confirm:
                with open('blocklist.json', 'r+') as f:
                    data = json.load(f)
                    data['blackList'].remove(addr)
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                    f.truncate()
                messagebox.showinfo("Information", f"Successfully removed\n{addr}\nfrom black list.")
                self.killPopup()
    
    def addBlackList(self, addr):
        if addr == settings()['signingAddress']:
            return
        elif addr in getBlocked()['blackList']:
            return
        confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to add\nADDR: {addr}\nScreen Name: {subName(addr)}\n to the black list?")
        
        if confirm:
            with open('blocklist.json', 'r+') as f:
                data = json.load(f)
                data['blackList'].append(addr)
                f.seek(0)
                json.dump(data, f, indent = 4)
                f.truncate()
            messagebox.showinfo("Information", f"Successfully added\n{addr}\nto black list.")
            self.popinfo.destroy()
        
    def addBlock(self, addr):
        if addr == settings()['signingAddress']:
            return
        elif addr in getBlocked()['blockList']:
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to unblock\nADDR: {addr}\nScreen Name: {subName(addr)}")
        
            if confirm:
                with open('blocklist.json', 'r+') as f:
                    data = json.load(f)
                    data['blockList'].remove(addr)
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                    f.truncate()
                messagebox.showinfo("Information", f"Successfully removed\n{addr}\nfrom the block list.")
                self.popinfo.destroy()
        else:        
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to block\nADDR: {addr}\nScreen Name: {subName(addr)}")
            
            if confirm:
                with open('blocklist.json', 'r+') as f:
                    data = json.load(f)
                    data['blockList'].append(addr)
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                    f.truncate()
                messagebox.showinfo("Information", f"Successfully added\n{addr}\nto block list.")
                self.popinfo.destroy()
    
    # function to receive messages
    def receive(self):
        self.textCons.tag_add("gray", END)
        self.textCons.tag_config("gray", foreground="gray", font=("Noto", 9))
        
        self.textCons.tag_add("red", END)
        self.textCons.tag_bind("red", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("red", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("red", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("red", foreground="red")
        
        self.textCons.tag_add("green", END)
        self.textCons.tag_bind("green", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("green", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("green", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("green", foreground="green")
        
        self.textCons.tag_add("blue", END)
        self.textCons.tag_bind("blue", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("blue", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("blue", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("blue", foreground="blue")
        
        self.textCons.tag_add("yellow", END)
        self.textCons.tag_bind("yellow", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("yellow", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("yellow", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("yellow", foreground="yellow")
        
        self.textCons.tag_add("cyan", END)
        self.textCons.tag_bind("cyan", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("cyan", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("cyan", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("cyan", foreground="cyan")
        
        self.textCons.tag_add("pink", END)
        self.textCons.tag_bind("pink", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("pink", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("pink", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("pink", foreground="pink")
        
        self.textCons.tag_add("purple", END)
        self.textCons.tag_bind("purple", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("purple", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("purple", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("purple", foreground="purple")
        
        self.textCons.tag_add("magenta", END)
        self.textCons.tag_bind("magenta", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("magenta", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("magenta", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("magenta", foreground="magenta")
        
        self.textCons.tag_add("black", END)
        self.textCons.tag_bind("black", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("black", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("black", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("black", foreground="black")
        
        self.textCons.tag_add("white", END)
        self.textCons.tag_bind("white", "<Button-1>", self.getInfo)
        self.textCons.tag_bind("white", "<Enter>", lambda e: self.textCons.config(cursor="hand2"))
        self.textCons.tag_bind("white", "<Leave>", lambda e: self.textCons.config(cursor=""))
        self.textCons.tag_config("white", foreground="white")
        
                
        while True:
            try:
                message = getMessages()
                self.updateName()
                self.updateBalance()
                
                for i in message: 
                
                    # insert messages to text box
                    uname = subName(i['addr']) #i.split(':')[0]
                    
                    i['index'] = self.getRow()
                    
                    if i['addr'] in getBlocked()['blockList']:
                        message = "<BLOCKED>"
                    else:
                        message = subEmotes(i['message'])
                    
                    self.textCons.config(state = NORMAL)
                    
                        
                    self.textCons.insert(END, f"{uname}: ", subColor(i['addr']))
                    
                    self.textCons.insert(END, f"{datetime.fromtimestamp(i['time'])}\n", "gray")
                    
                    self.textCons.insert(END,
                                         f"{message}\n\n")
                     
                    self.textCons.config(state = DISABLED)
                    self.textCons.see(END)
                    if settings()['mute'] == False and self.focus == False:
                        self.ps.play()
                    self.masterMsg.append(i)
                        
            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                print("An error occured!")
                print(e)

                break
            time.sleep(0.1)
    
    def getRow(self):
        index = self.textCons.index("end-1c")
        row = int(float(index)) #index.split(".")[0]
        return row
            
    def onClose(self):
        self.Window.destroy()
        os._exit(0)
    
    def enterbtn(self, msg):
        self.entryMsg.delete("insert-1c")
        self.buttonMsg.invoke()
    
    def shiftenterbtn(self, msg):
        self.entryMsg.insert(END, "")
        
    def focusIn(self, focus):
        self.focus = True
        
    def focusOut(self, focus):
        self.focus = False
    
    def paste(self):
        self.entryMsg.insert(END, pyperclip.paste())
        
    def copy(self):
        pyperclip.copy(self.entryMsg.selection_get())
        self.textCons.tag_remove(SEL, "1.0", END)
        
    def cut(self):
        pyperclip.copy(self.entryMsg.selection_get())
        try:
            self.entryMsg.delete("sel.first", "sel.last")
        except:
            self.textCons.tag_remove(SEL, "1.0", END)
         
    def signMessage(self, msg, time, room):
        
        signature = {}
        self.signature = signature
        self.msg = msg
        
        addr = settings()['signingAddress']
        sig = rpcproxy().signmessage(addr, self.msg + str(time) + str(room))
        
        self.signature['addr'] = addr
        self.signature['sig'] = sig
        
        return self.signature
      
    # function to send messages
    def sendMessage(self):
        
        self.textCons.config(state=DISABLED)
        timestamp = int(time.time())
        sig = self.signMessage(self.msg.strip(), timestamp, settings()['room'].strip())
        while True:
            if self.msg.strip() == '':
                print("Blank message not allowed.")
                break
                
            message = {'message': self.msg.strip(), 'sig': sig['sig'], 'addr': sig['addr'], "rm": settings()['room'].strip(), "time": timestamp}
            self.message = message

            try:
                rpcproxy().sendmessage(self.json.dumps(message))
            except Exception as e:
                print(e)
            self.lastMsg = timestamp
            break


def setBlock():
    global bestBlock
    global seenTX
    seenTX = []
    currentHeight = rpcproxy().getblockcount()
    bestBlock = currentHeight - settings()['history']

def checkSetup():
    system_type = platform.system()
    if system_type == 'Linux':
        settingsFile = os.path.expanduser('~/.config/tuxchat/settings.json')
        
        if os.path.isfile(settingsFile) == False:
            pass
            #print('lol')
         
    elif system_type == 'Windows':
        settingsFile = os.path.expanduser('~\\AppData\\Roaming\\tuxchat\\tuxchat\\settings.json')

def checkConnection():
    print('Checking connection to Tuxcoin wallet...')
    try:
        ver = rpcproxy().getnetworkinfo()['subversion']
        print('Connection sucessful!')
    except:
        print('No connection to Tuxcoin wallet')
        input("Press Enter to close")
        sys.exit()
        
    print('Checking for compatable wallet version...')
    if int(''.join(filter(str.isdigit, ver))) < 182:
        print(f'Tuxcoin wallet version too low.\nHas: {ver}\nRequired: TuxcoinCore:0.18.2 or higher.')
        input("Press Enter to close")
        sys.exit()
    else:
        print(f'Wallet version is: {ver}\nCompatible wallet detected!')
        
def checkPeers():
    print('Checking for compatable peers on the Tuxcoin network...')
    
    peers = rpcproxy().getpeerinfo()
    
    for i in peers:
        ver = int(''.join(filter(str.isdigit, i['subver'])))
        if ver < 182:
            continue
        else:
            print("Compatable peer found!")
            break
            
        print('No compatable peers found')
        input("Press Enter to close")
        sys.exit()

def validateAddress(addr):
    
    val = rpcproxy().validateaddress(addr)
    
    if val['isvalid'] == True and val['ismine'] == True and val['isscript'] == False and val['iswitness'] == False:
        print('Address validated!')
        msg = 'Address validated!'
        return (True, msg)
    else:
        if val['isvalid'] == False:
            print('Not a valid Tuxcoin address!')
            msg = 'Not a valid Tuxcoin address!'
            return (False, msg)
        
        elif val['ismine'] == False:
            print("Address not owned by wallet!")
            msg = "Address not owned by wallet!"
            return (False, msg)
        
        elif val['isscript'] == True or val['iswitness'] == True:
            print("Invalid address type!\nAddress must be Legacy, not segwit/bech32")
            msg = "Invalid address type!\nAddress must be Legacy, not segwit/bech32"
            return (False, msg)

def startNames():
    while True:
        
        names.main()
        time.sleep(10)            
        
def main():
    
    print(f"Welcome to tuxchat version: {version}")
    checkSetup()
    checkConnection()
    checkPeers()
    setBlock()

    print('Refreshing screen name database. This may take several minutes.')
    print('Building database...')
    names.main()

                
    gnm = threading.Thread(target=startNames)
    gnm.start()

   
            
main()
 
# create a GUI class object
g = GUI()
