# Tuxchat
Blockchain messaging interface for Tuxcoin.

Quick Start:

In order to use tuxchat, you will need to have the latest version of tuxcoin running and synced. 

So start by downloading the latest release for your OS [here](https://github.com/bleach86/tuxcoin-V2/releases).

Make sure to download tuxcoin.conf and tuxcoin-blocks zip file.

The blocks and chainstate folder from the zip file go into your tuxcoin data directory as does the tuxcoin.conf file. 
Usually found in `%appdata%\roaming\Tuxcoin` for Windows or in `~/.tuxcoin` on Linux. You may have to make this directory.

Once your wallet is running and synced with the tuxcoin network, you will need to add funds to pay the transaction fees for the messages.

You can contact `tuxprint#5176` on the [official tuxcoin Discord server](https://discord.gg/35NdZhq) to get funds.

Once your wallet is running and funded you are ready to use tuxchat. 

Now just run tuxchat.exe. Once tuxchat is running you will need to click the settings button and add a signing address.
You can either add your own, or leave the spcae blank and hit submit for a new one to be generated for you. If you use a custom address, the private keys must be held in the wallet that tuxchat is connected to.

Once you have a signing address, you can go back to settings and choose a username and display color. Note, this process may take a few minutes to complete due to the nature of blockchain. If for some reason, it has been more than 30 minutes since making name request, then resubmit.

You are now ready to use tuxchat!

Note: tuxchat communicates with the tuxcoin network over rpc. If you wish to change the rpc username and password in the tuxcoin.conf file,
then you need to make sure to make the same changes in settings.json file.

This is early access/alph level software. Use at own risk. There may be breaking changes made at anytime without notice.
