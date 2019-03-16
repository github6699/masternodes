# Masternodescripts
Masternode Install script for various coins on Ubuntu VPS. 
This script configures a new vps, installs dependencies, and installs Coin Daemon in path, and creates proper systemd scripts for ease of use.
Ip:port and private key show at the end for easy copy/paste to control wallet.

###Currently supported Coins
Coin | Supported | Collateral Required
:--- | :---: | ---:
HTH | Yes | 2,500,000
REDN | Yes | 5,000
XMN | Yes | 1,000
SOV | Yes | 15,000
GeekCash | Yes | 10,000
ResQ  | Yes | 300,000
Wiki | Yes | 15,000

Tested on Ubuntu 16.04, 64bit OS. 


If the VPS is newly deployed, run these 3 lines first:
```
apt-get update
apt-get upgrade
reboot
```

After the reboot, log in again.

Now when all is ready, install the Coin Daemon:
```
apt-get -y install python
git clone https://bitbucket.org/minerscore/masternodes.git
cd masternodes
python <masternode_script.py> (Use the MN script you want to install)
```

While waiting for the script to finish, you can set up the local wallet:

* Make a receive address called masternode1 (or whatever you want to call it)
* Send required collateral to the newly made address. Wait for confirmations.
* Go to Settings > Options >Wallet, and activate "Show Masternodes Tab"
* Go to Tools > Debug Console, and enter following: `masternode outputs` 
  This returns `collateral_output_txid` and `collateral_output_index`
* Go to Tools > Open Masternode Configuration File
  The script prints a config line for this file.
  Add the config line like the example in the file, and add the returns from "masternode outputs"
    ```Masternode1 ip:port GENKEY collateral_output_txid collateral_output_index```

Where the ip:port and GENKEY is retrieved from the finished VPS install. `collateral_output_txid` AND `collateral_output_index` is from the Debug console.

Save the file and restart your wallet. Wait until fully synchronized, then go to Masternode tab and start your Masternode.

You can check on the VPS with commands like (for reden):
```
check: reden-cli masternode status
stop:  reden-cli stop or systemctl stop redend
start: redend or systemctl start redend
```

## To Update
```
cd masternodes
git pull
python <masternode_script.py> (Use the MN script you want to update)
```

### Other items
In the masternodes directory, there is a monitors directory.  Running the monitor of the coin you installed, after it's started, will give you some basic stats about your node.  Future updates may include the ability to receive sms, emails, slack, or discord messages if your node changes state.

Example: `monitors/sov-monitor`

```css
=================== Masternode Stats ===================

Node Status:	 ENABLED
Payee Address:	 Sccc9anj7cGSZec1CqafUp9Xj9hp2sQtwb
Masternode IP:	 104.237.11.156:11888
Pay Rank:	 91 out of 119
Last Paid:	 2019-01-08 01:28:43
Last Seen:	 2019-01-08 03:15:09
Online For:	 1 day, 4:30:34

========================================================
```