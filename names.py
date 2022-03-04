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
import time
from datetime import datetime
import random
import os

def settings():
    with open('settings.json') as f:
        settings = json.loads(f.read())
    return settings

def getNames():
    if os.path.isfile('names.json'):
        with open('names.json', 'r+') as f:
            names = json.loads(f.read())
    else:
        with open('names.json', 'w') as f:
            f.write(json.dumps({'bestBlock': 1740000, 'nameList': []}))
        with open('names.json', 'r+') as f:
            names = json.loads(f.read())
        
    return names


def processBlocks():
    rpcproxy = AuthServiceProxy(f"http://{settings()['rpcConnection']['username']}:{settings()['rpcConnection']['password']}@{settings()['rpcConnection']['ip']}:{settings()['rpcConnection']['port']}")
    
    names = getNames()
    
    currentHeight = rpcproxy.getblockcount() +1
    
    for index in range(names['bestBlock'], currentHeight):
        hash = rpcproxy.getblockhash(index)
        block = rpcproxy.getblock(hash)
        
        
        for txid in block['tx']:
            tx = rpcproxy.getrawtransaction(txid, True)
            
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
                        
                        if "nameRequest" in msgString:
                            if validateSignature(msgString['message'], msgString['addr'], msgString['sig'], msgString['time']) == True:
                                timeElapsed = tx['time'] - msgString['time']
                                
                                if timeElapsed > 1800:
                                    continue
                                
                                if len(msgString['message']) > 30:
                                    continue                                 
                                newName = ''.join(msgString['message'].split())
                                
                                if newName.upper() in names['nameList']:
                                    if msgString['addr'] in names and newName.upper() == names[msgString['addr']]['name'].upper():
                                        names[msgString['addr']]['name'] = newName
                                        names[msgString['addr']]['color'] = msgString['nameRequest']
                                    else:
                                        continue
                                        
                                
                                elif msgString['nameRequest'] not in settings()['colors']:
                                    continue
                                
                                elif msgString['addr'] in names:
                                    if newName != "":
                                        names['nameList'].remove(names[msgString['addr']]['name'].upper())
                                        names['nameList'].append(newName.upper())
                                    names[msgString['addr']]['name'] = newName
                                    names[msgString['addr']]['color'] = msgString['nameRequest']
                                    
                                else:
                                    if newName != "":
                                        names['nameList'].append(newName.upper())
                                    names[msgString['addr']] = {}
                                    names[msgString['addr']]['name'] = newName
                                    names[msgString['addr']]['color'] = msgString['nameRequest']
                            
                    except Exception as e:
                        continue
    updateNames(names)
    updateBlock(currentHeight)
                            
def validateSignature(msg, addr, sig, time):
    rpcproxy = AuthServiceProxy(f"http://{settings()['rpcConnection']['username']}:{settings()['rpcConnection']['password']}@{settings()['rpcConnection']['ip']}:{settings()['rpcConnection']['port']}")
    verify = rpcproxy.verifymessage(addr, sig, msg + str(time))
    if verify == True:
        return True
    else:
        return False
    
def updateNames(names):
    
    with open('names.json', 'r+') as f:
        data = json.load(f)
        if data == names:
            #print('Same')
            pass
    
        else:
            f.seek(0)
            json.dump(names, f, indent = 4)
            f.truncate()

def updateBlock(currentHeight):
    with open('names.json', 'r+') as f:
        data = json.load(f)
        data['bestBlock'] = currentHeight
        f.seek(0)
        json.dump(data, f, indent = 4)
        f.truncate()

def main():
    processBlocks()

if __name__ == "__main__":
    main()
     
    #processBlocks()
    #updateNames()



