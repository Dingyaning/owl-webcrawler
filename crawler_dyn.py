#coding=utf-8
import requests
import json
import base64
import time
import json
import os

from html.parser import HTMLParser
from bs4 import BeautifulSoup
import bs4

def login(username, password):
    username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    session = requests.Session()
    res = session.post(loginURL, data = postData)
    jsonStr = res.content.decode('gbk')
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        print("登录成功")
        # 把cookies添加到headers中，必须写这一步，否则后面调用API失败
        cookies = session.cookies.get_dict()
        cookies = [key + "=" + value for key, value in cookies.items()]
        cookies = "; ".join(cookies)
        session.headers["cookie"] = cookies
    else:
        print("登录失败，原因： %s" % info["reason"])
    return session

def getWeiBoContent(res):
    soup = BeautifulSoup(res,"html.parser")
    print(soup.prettify())

def makeDirs(path):
    print(path)
    paths = path.split(os.sep)
    temppath = ''
    for index,_spilt in enumerate(paths):
        if index == 0:
            temppath = _spilt
            continue
        temppath = temppath + os.sep + _spilt
        if os.path.isdir(temppath):
            pass
        elif index == len(paths)-1:
            if os.path.isfile(temppath):
                pass
            else:
                os.mkdir(temppath)
        else:
            os.mkdir(temppath)
    return temppath


def makeRelativeDirs(time):
    basePath = os.path.abspath(os.path.dirname(__file__)) #获取当前文件夹的绝对路径,根据不同系统会有所不同
    path = basePath+os.sep+time
    path = makeDirs(path)
    return path






if __name__ == '__main__':
    session = login('微博账号', '密码')

    time_today = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    #open file ,clean up file, write into file
    dirs_today = makeRelativeDirs(time_today)
    f = open(dirs_today+"/xinlangweibo.txt",'w')
    # f.truncate()

    for i in range(1,2):
        postData = {
            'keyword':'招商银行信用卡掌上生活',
            'smblog':'搜微博',
            'page':i
        }
        res = session.post('http://weibo.cn/search/?pos=search',data=postData)
        # content = res.content.decode('utf-8')
        # getWeiBoContent(res)
        soup = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        weibo_data = {
            "time":"",
            "content":""
        }

        for tag in soup.find_all('span'):
            if tag['class'][0] == 'ctt':
                temp = ''
                for content in tag.contents:
                    # print(content)
                    if type(content) is not bs4.element.Tag:
                        temp += content
                weibo_data["content"] = temp

                for time_div in tag.parent.next_siblings:
                    if time_div.span['class'][0] == 'ct':
                        content_ct = time_div.span.contents[0]
                        contents_time = content_ct.split('\xa0')
                        weibo_data["time"] = contents_time[0]

                f.write(json.dumps(weibo_data) + '\n')
                print(weibo_data)

            if tag['class'][0] == 'cmt':
                parent = tag.parent
                # print(parent.contents)
                if len(parent.contents) >=2:
                    # print(tag.parent.contents)
                    for pContent in parent.contents:
                        # print(pContent)
                        if type(pContent) is not bs4.element.Tag and len(pContent) > 2:
                            weibo_data["content"] = pContent
                            # print(pContent)
                            pContent_parent = pContent.parent
                            for pParent in pContent_parent.find_all('span'):
                                if pParent['class'][0] == 'ct':
                                    # print(pParent)
                                    content_ct = pParent.contents[0]
                                    contents_time = content_ct.split('\xa0')
                                    # print(contents_time[0])
                                    weibo_data["time"] = contents_time[0]
                            print(weibo_data)
                            f.write(json.dumps(weibo_data)+'\n')

    f.close()



