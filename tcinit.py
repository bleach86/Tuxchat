from tkinter import *
from tkinter import font, ttk, messagebox, filedialog
from tooltip import ToolTip
from tkinter.scrolledtext import ScrolledText
from urllib.request import urlopen
import platform, os, sys, threading, json, requests, time
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

system_type = platform.system()

class GUI:
    def __init__(self):
        self.system = system_type
        #self.mkSettingsDir(self.system)
        self.window()
        
    def window(self):
        self.setupinfo = Tk()
        self.setupinfo.wm_title("Message Info")
        self.win = ScrolledText(self.setupinfo, bg="black", fg="white")
        self.win.grid(row=1, column=1, columnspan=10, rowspan=10, pady=10)
        self.win.insert(END, f"Welcome to the Tuxchat setup wizard.\n")
        self.win.insert(END, f"Sit back and relax while I setup tuxchat for you.\n\n")
        self.win.config(state = DISABLED)
        B1 = ttk.Button(self.setupinfo, text="Close", command = self.setupinfo.destroy)
        B1.grid(row=11, column=5)
        setinit = threading.Thread(target=self.setupTc)
        setinit.start()
        self.setupinfo.mainloop()
    
    def insInfo(self, msg):
        self.win.config(state = NORMAL)
        self.win.insert(END, f'{msg}\n')
        self.win.config(state = DISABLED)
    
    def setupTc(self):
        time.sleep(3)
        self.mkSettingsDir(self.system)
        self.getSettings()
        self.mkDataDir(self.system)
    
    def getSettings(self):
        url = 'https://raw.githubusercontent.com/bleach86/Tuxchat/main/settings.json'
        self.insInfo(f"Getting settings from '{url}'...")
        response = urlopen(url)
        data = json.loads(response.read())
        
        with open(f'{self.settingsDir}/settings.json', 'w') as f:
            f.write(json.dumps(data))
            self.insInfo("Success!")
        
        
    def mkDataDir(self, system):
        with open(f"{self.settingsDir}/settings.json") as f:
            settings = json.loads(f.read())
            
        if settings['dataDir'] == "":
            if system == 'Linux':
                self.dataDir = os.path.expanduser('~/.tuxchatdata/')
            elif system == 'Windows':
                self.dataDir = os.path.expanduser('~\\AppData\\Roaming\\Tuxchatdata\\')
            
            confirm = messagebox.askyesno("Confirm Data Directory", f"Tuxchat data dir. Will use ~1.1GB\nPath: '{self.dataDir}'\nPress yes to use this path or no to choose your own.")
            if confirm:
                self.updatePath(self.dataDir)
            
            elif not confirm:
                while True:
                    self.dataDir = filedialog.askdirectory(title='Please select a directory')
                    confirm = messagebox.askyesno("Confirm Data Directory", f"Tuxchat data dir. Will use ~1.1GB\nPath: '{self.dataDir}'\nPress yes to use this path or no to choose a different one.")
                    
                    if confirm:
                        break
                    else:
                        pass
                        
                self.updatePath(self.dataDir)
                
            self.insInfo(f"Creating Data directory at '{self.dataDir}'...")
            os.mkdir(self.dataDir)
            self.insInfo("Success!")
                
                
    def updatePath(self, path):
        with open(f'{self.settingsDir}/settings.json', 'r+') as f:
            data = json.load(f)
            data['dataDir'] = path
            f.seek(0)
            json.dump(data, f, indent = 4)
            f.truncate()
    
        
    def mkSettingsDir(self, system):
        
        if system == 'Linux':
            self.settingsDir = os.path.expanduser('~/.config/tuxchat/')
        elif system == 'Windows':
            self.settingsDir = os.path.expanduser('~\\AppData\\Roaming\\.tuxchat\\')
        
        if os.path.isdir(self.settingsDir) == False:
            self.insInfo(f"Making Tuxchat config directory at '{self.settingsDir}'...")
            os.mkdir(self.settingsDir)
            self.insInfo("Success!")
                
                
    
    def download_url(self, url, path, chunk_size=128):
        r = requests.get(url, stream=True)
        with open(path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        




if __name__ == "__main__":
    GUI()
