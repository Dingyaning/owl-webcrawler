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
        print("login successd !")
        # 把cookies添加到headers中，必须写这一步，否则后面调用API失败
        cookies = session.cookies.get_dict()
        cookies = [key + "=" + value for key, value in cookies.items()]
        cookies = "; ".join(cookies)
        session.headers["cookie"] = cookies
    else:
        print("login fail： %s" % info["reason"])
    return session

def getWeiBoContent(res):
    soup = BeautifulSoup(res,"html.parser")
    # print(soup.prettify())

def makeDirs(path):
    # print(path)
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
    print(temppath)
    return temppath

def analysisHtml(soup,f):
    weibo_data = {
        "time":"",
        "content":""
    }
    dayOfMonths = time.strftime('%m月%d日',time.localtime(time.time()))

    for tag in soup.find_all('span'):
        if tag['class'][0] == 'ctt':
            temp = ''
            for content in tag.contents:
                # print(content)
                if type(content) is not bs4.element.Tag:
                    temp += content
            weibo_data["content"] = temp
            if tag.parent.next_siblings is bs4.element.Tag:
                print(tag.parent.next_siblings.name)
                for time_div in tag.parent.next_siblings:
                    if time_div.span['class'][0] == 'ct':
                        content_ct = time_div.span.contents[0]
                        contents_time = content_ct.split('\xa0')
                        weibo_data["time"] = contents_time[0].replace('今天',dayOfMonths)
            else:
                for time_span in tag.next_siblings:
                    if type(time_span) is bs4.element.Tag and time_span.name == 'span' and time_span['class'][0] == 'ct':
                        content_ct = time_span.contents[0]
                        contents_time = content_ct.split('\xa0')
                        weibo_data["time"] = contents_time[0].replace('今天',dayOfMonths)
            f.write(json.dumps(weibo_data) + '\n')
            # print(weibo_data)

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
                                content_ct = pParent.contents[0]
                                contents_time = content_ct.split('\xa0')
                                # print(contents_time[0])
                                weibo_data["time"] = contents_time[0]
                        # print(weibo_data)
                        f.write(json.dumps(weibo_data)+'\n')




if __name__ == '__main__':
    import sys
    basePath = sys.argv[1]

    session = login('你的微博账户', '账户密码')

    time_today = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    #open file ,clean up file, write into file,close file
    dirs_today = makeDirs(basePath+os.sep+time_today)
    f = open(dirs_today+"/xinlangweibo.txt",'w')
    f.truncate()

    keyword_serch = '招商银行信用卡掌上生活'

    # 全量
    # for i in range(1,100):
    #     postData = {
    #         'keyword':keyword_serch,
    #         'smblog':'搜微博',
    #         'page':i,
    #         'sort':'time'
    #     }
    #     res = session.post('http://weibo.cn/search/?pos=search',data=postData)
    #     # content = res.content.decode('utf-8')
    #     # getWeiBoContent(res)
    #     soup = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
    #
    #     analysisHtml(soup,f)
    # f.close()

    #当天
    for i in range(1,100):
        time_today = time.strftime('%Y%m%d',time.localtime(time.time()))
        # print(time_today)

        postData = {
            'keyword':keyword_serch,
            'smblog':'搜微博',
            'page':i,
            'starttime':str(time_today),
            'endtime':str(time_today),
            'sort':'time'
        }
        res = session.post('http://weibo.cn/search/?pos=search',data=postData)
        soup = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        if len(soup.find_all('span')) <= 4:
            break
        analysisHtml(soup,f)
    f.close()



