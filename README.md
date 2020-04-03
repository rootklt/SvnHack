### SvnHack ###

SVN信息泄漏利用脚本，可用于1.7版本及以下的SVN信息泄漏。

---

### Usage ###

```bash
usage: SvnHack.py [-h] -u TARGETURL [--wcdb] [--chkver] [--download]

optional arguments:
  -h, --help            show this help message and exit
  -u TARGETURL, --url TARGETURL
                        Special svn target url
  --wcdb                Download wc.db database file
  --chkver              Check svn Version
  --download            Download .svn data
```

![image](https://github.com/rootklt/SvnHack/blob/master/help.gif)

```bash
python -u http://127.0.0.1:8080/.svn --download

#下载.svn目录下的源代码
```
![image](https://github.com/rootklt/SvnHack/blob/master/download.gif)

### Update Log ###

+ 1.增加了1.7版本以下支持

### TODO ###

+ 1. 对新增部分进行调试（因为时间关系，没来得及调试）
