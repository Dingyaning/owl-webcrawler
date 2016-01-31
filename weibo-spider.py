import requests
import json
import base64
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import bs4

# class MyHTMLParser(HTMLParser):
#     def __init__(self):
#         HTMLParser.__init__(self)
#         self.recording = 0;
#     def handle_starttag(self, tag, attrs):
#         if tag == 'span':
#             if self.recording:
#                 self.recording += 1
#                 return
#             for k, v in attrs:
#                 if k == 'class' and v == 'ctt':
#                     self.recording = 1
#                     break
#     def handle_endtag(self, tag):
#         if self.recording == 1 and tag == 'span':
#             self.recording -= 1;
#     def handle_data(self, data):
#         if self.recording:
#             print(data)


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
        print("login success")
        cookies = session.cookies.get_dict()
        cookies = [key + "=" + value for key, value in cookies.items()]
        cookies = "; ".join(cookies)
        session.headers["cookie"] = cookies
    else:
        print("login fail, cause: %s" % info["reason"])
    return session

if __name__ == '__main__':
    session = login('your account', 'your password')
    postData = {
        'keyword':'掌上生活',
        'smblog':'搜微博'
    }
    res =  session.post('http://weibo.cn/search/?pos=search', data=postData).content.decode('utf-8')
    # parser = MyHTMLParser()
    # parser.feed(res.content.decode('utf-8'))
    soup = BeautifulSoup(res, "html.parser")
    for tag in soup.find_all('span'):
        # print(tag['class'])
        if tag['class'][0] == 'ctt':
            temp = ''
            for content in tag.contents:
                # print(type(content))
                if type(content) is bs4.element.Tag:
                    temp += content.contents[0]
                else:
                    temp += content
            print(temp)
        if tag['class'][0] == 'cmt':
            parent = tag.parent
            # print(tag.parent.contents)
            if len(tag.parent.contents) >= 2:
                for pContent in parent.contents:
                    if type(pContent) is not bs4.element.Tag and len(pContent) > 2:
                        print(pContent)
