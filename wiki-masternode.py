#!/usr/bin/env python

import urllib2
import zipfile
import tarfile
import platform
import string
import random
import time
import subprocess
import os
import sys
from shutil import copy

walletVer="1.1.0"
rpcport = "13889"
port = "13888"
rpcuser = "wikiuser"
datadir = "/root/.wikicore"
config_file = "wiki.conf"
cli = "wiki-cli"
coind = "wikid"
walletUrl = "https://github.com/Altcoinwiki/source/releases/download/v%s" % (walletVer)
walletFile = "WikiCoin-%s-x86_64-pc-linux-gnu.zip" % (walletVer)
ticker = "WIK"

def upgrade():
    if os.path.isfile("%s/%s" % (datadir,config_file)):
        upgrade = raw_input("Do you want to upgrade %s? (y/n): " % (coind)).lower() 
        if "y" in upgrade:
            subprocess.call("systemctl stop %s" % (coind), shell=True)
            downloadWallet()
            time.sleep(2)           
            print("Wallet has been upgraded.")
            exit(0)
        elif "n" in upgrade:
            reinstall = raw_input("Do you want to reinstall %s? (y/n): " % (coind)).lower()
            if "y" in reinstall:
                installUbuntuPackages()
            else:
                exit(1)
        else:
            exit(1)           
    else:
        installUbuntuPackages()

def installUbuntuPackages():
    print("Installing packages...")
    subprocess.call("add-apt-repository -y ppa:bitcoin/bitcoin", shell=True)
    subprocess.call("add-apt-repository -y ppa:ubuntu-toolchain-r/test", shell=True)
    subprocess.call("apt-get update -y", shell=True)
    subprocess.call("apt-get -y upgrade", shell=True)
    subprocess.call("apt-get -y install wget libssl-dev dnsutils psmisc libzmq3-dev libevent-dev bsdmainutils software-properties-common libboost-all-dev libminiupnpc-dev libdb4.8-dev libdb4.8++-dev gcc-4.9 libstdc++6", shell=True)
    print("Install of required packages is done")
    addMonitoring()


def addMonitoring():
    install = raw_input("Do you want to setup monitoring so you can manually verify status? (y/n): ").lower()
    if "y" in install:
        fpath = os.path.abspath(sys.argv[0]).rsplit('/', 1)[0]
        os.symlink("%s/monitors/%s-monitor" % (fpath,ticker.lower()), "/usr/local/bin/%s-monitor" % (ticker.lower()))
    elif "n" in install:
        print("No monitoring scripts will be added")
    else:
        print("Please try and again and select y or n ")
        exit(1)


def removeOldFiles():
    print("Removing old files...")
    subprocess.call("killall %s" % (coind), shell=True)
    subprocess.call("rm -rf %s /usr/local/bin/wiki*" % (datadir), shell=True)
    print("Old files removed")


def downloadWallet():
    print("Downloading Wallet...")
    if not os.path.isdir(datadir): 
        subprocess.call("mkdir %s" % (datadir), shell=True)
    ## Download wallet
    url = "%s/%s" % (walletUrl, walletFile)
    file_name = "wallet"
    dloc = "/tmp/%s" % file_name
    u = urllib2.urlopen(url)
    f = open(dloc, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: %s Bytes: %s") % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (
            file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,

    f.close()
    procFile(dloc)


def procFile(data):
    """
    Process zip previously downloaded
    """
    print("Extracting %s to /tmp/") % (data)
    if zipfile.is_zipfile(data):
        zip = zipfile.ZipFile(data)
        zip.extractall('/tmp/')
    elif tarfile.is_tarfile(data):
      tar = tarfile.open(data)
      tar.extractall(path='/tmp/')
      tar.close()
    else:
      print("You didn't dowload a tar file or a zip file, you need to investigate")
      exit(1)
    subprocess.call("rm -rf %s" % (data), shell=True)
    subprocess.call("mv /tmp/WikiCoin*/* /usr/local/bin/", shell=True)    
    subprocess.call("chmod +x /usr/local/bin/wiki*", shell=True)
    conffile = "%s/%s" % (datadir, config_file)
    f = open(conffile, "w")
    f.write("rpcuser=%s\ndaemon=1\nrpcpassword=temp\nrpcport=%s" % (rpcuser,rpcport))
    f.close()
    subprocess.call("%s" % (coind), shell=True)
    time.sleep(10)
    print("Wallet has now been downloaded")


def configureMasterNode():
    print("Masternode configuration")
    pwd = pwd_generator()
    wan = getWan()
    conffile = "%s/%s" % (datadir, config_file)
    key = subprocess.check_output("%s masternode genkey" % (cli), shell=True).rstrip()
    subprocess.call("%s stop" % (cli), shell=True)
    f = open(conffile, "w")
    f.write("rpcuser=%s\nrpcpassword=%s\nrpcport=%s\nrpcallowip=127.0.0.1\nport=%s\nexternalip=%s\nlisten=1\nmaxconnections=256\ndaemon=1\nmasternode=1\nmasternodeprivkey=%s\n" % (rpcuser, pwd, rpcport, port, wan, key))
    f.close()
    systemdScript()
    subprocess.call("systemctl start %s" % (coind), shell=True)
    showResults(pwd, wan, key)


def pwd_generator(size=32, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def showResults(pwd, wan, key):
    print("\n============================= Node Information ============================================\n")
    print("rpcuser: %s" % (rpcuser))
    print("rpcpassword: %s" % (pwd))
    print("Masternode IP: %s:%s" % (wan, port))
    print("Masternode private key: %s" % (key))
    print("Config file: %s/%s" % (datadir, config_file))
    print("\nCopy the following for your local masternode.conf: %s:%s %s" % (wan, port, key))
    print("\n\n=========================================================================================\n")
    print("Check your node status with: %s masternode status" % (cli))
    print("Stop your node with: systemctl stop %s" % (coind))
    print("Start your node with: systemctl start %s" % (coind))
    print("\n=========================================================================================\n")


def getWan():
    return subprocess.check_output("dig +short myip.opendns.com @resolver1.opendns.com", shell=True).rstrip()


def systemdScript():
    f = open("/etc/systemd/system/%s.service" % (coind), "w")
    f.write("[Unit]\nDescription=%s service\nAfter=network.target\n[Service]\nUser=root\nGroup=root\nType=forking\nExecStart=/usr/local/bin/%s\nExecStop=-/usr/local/bin/%s stop\nRestart=always\nPrivateTmp=true\nTimeoutStopSec=60s\nTimeoutStartSec=10s\nStartLimitInterval=120s\nStartLimitBurst=5\n[Install]\nWantedBy=multi-user.target" % (ticker, coind, cli))
    f.close()
    subprocess.call("systemctl daemon-reload", shell=True)
    subprocess.call("systemctl enable %s" %(coind), shell=True)


if __name__ == '__main__':
    oper = str(platform.dist()[0])
    if oper == 'Ubuntu':
        upgrade()
    else:
        print("Sorry, %s operating system is not currently supported" % (oper))
        exit(1)
    removeOldFiles()
    downloadWallet()
    configureMasterNode()