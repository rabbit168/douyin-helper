# coding=utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
import time
import redis
import os
import pickle
import re
import datetime
import json

def extract_chars(text):
    pattern = re.compile(r'[a-zA-Z0-9\u4e00-\u9fff]+')
    return ''.join(pattern.findall(text))

abs_path = os.path.split(os.path.abspath(__file__))[0]
os.chdir(abs_path)



html = ''
liveId = ''
hashKey_prefix = 'dy:message:hash'

def parse_latest(html):
    redisConn = getRedis()
    doc = pq(html)
    data_id = doc.attr('data-id')
    # print(data_id)
    spans = doc('span')
    content = ''
    item = {}
    # 解析用户
    content_list = []
    for span in spans.items():
        text = span.text()
        if text != '':
            # print(text)
            content_list.append(text)
    item['dataid']=data_id
    item['username']=content_list[0]
    item['voice']=extract_chars(content_list[0])
    item['message']=content_list[1]
    # 解析用户等级
    img_list = []
    imgs = doc('img')
    for img in imgs.items():
        img_list.append(img.attr('src'))
    if len(img_list)>0:
        numbers = re.findall(r"\d+", img_list[0])
        # print(numbers)
        item['user_level'] = numbers[2]
    #当没有的时候就放入
    pushKey = '%s:latest:%s'%(hashKey_prefix,str(liveId))
    setKey = '%s:latest:%s:%s'%(hashKey_prefix,str(liveId),str(item['dataid']))
    item['setKey'] = setKey
    item['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print('latest--------------',item)
    if not redisConn.exists(setKey):
        print("latest写入--------",item)
        redisConn.set(setKey,json.dumps(item))
        redisConn.lpush(pushKey,json.dumps(item))


def parse_content(html):
    redisConn = getRedis()
    html = html.replace('&nbsp;','')
    doc = pq(html)
    # data_id = doc.attr('data-id')
    # print(data_id)
    divs = doc('.webcast-chatroom___item')
    num = 0
    for div in divs.items():
        item = {}
        img_list = []
        item['dataid'] =div.attr('data-id')
        content = div.text()
        if '：' in content:
            contents = content.split('：')
            item['username'] =contents[0]
            item['voice']=extract_chars(contents[0])
            if '送出' in content:
                numbers = re.findall(r"\d+", contents[1])
                # print(numbers)
                item['gift_count'] =numbers[0]

        imgs = div('img')
        for img in imgs.items():
            # print(img.attr('src'))
            img_list.append(img.attr('src'))
        # 提取等级
        if len(imgs)==2:
            numbers = re.findall(r"\d+", img_list[0])
            # print(numbers)
            item['user_level'] = numbers[2]
            item['gift_pic'] = img_list[1]
        #当没有的时候就放入
        pushKey = '%s:gift:%s'%(hashKey_prefix,str(liveId))
        setKey = '%s:gift:%s:%s'%(hashKey_prefix,str(liveId),str(item['dataid']))
        item['setKey'] = setKey
        item['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print('gift-------------',item)
        if not redisConn.exists(item['setKey']):
            print("gift写入--------------",item)
            redisConn.set(setKey,json.dumps(item))
            redisConn.lpush(pushKey,json.dumps(item))
        num +=1
    # print(num)
    # return content

def start(url):
    global html
    # 1. 初始化配置对象
    options = Options()
    # options.add_argument("--headless")
    #创建Chrome浏览器驱动，注意一定要大写浏览器名称
    driver=webdriver.Chrome(options=options)
    # driver=webdriver.Chrome()
    driver.get(url)
    # exit(0)
    WebDriverWait(driver, 10).until(lambda driver: driver.title)
    title = driver.title
    print(title)
    # 礼物消息
    xpath = '//*[@id="chatroom"]/div/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]'
    # 底部消息
    xpath_bottom = '//*[@id="chatroom"]/div/div[2]/div/div/div[1]/div/div[1]/div/div[2]'
    while True:
        try:
            html = driver.find_element(By.XPATH, xpath).get_attribute("innerHTML")
            # print(html)
            parse_content(html)
            html = driver.find_element(By.XPATH, xpath_bottom).get_attribute("innerHTML")
            # print(html)
            parse_latest(html)
            # break
        except BaseException as e:
            print(e)
        time.sleep(0.5)

    # driver.quit()

# 调试字符串
string = '<div class="webcast-chatroom___item fade fade-enter-done" data-id="7390945420964502079" style="background-color: transparent;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p11-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_1.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">哇�🌿藤藤藤菜菜 </span><span class="WsJsvMP9">来了</span></div></div>'

string1 = '<div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390948275930043418" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_26.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">花*****：</span><span class="WsJsvMP9"><span class="webcast-chatroom___content-with-emoji-text">永远打的是外围一圈</span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390948310365148187" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p11-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_26.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">花*****：</span><span class="WsJsvMP9"><span class="webcast-chatroom___content-with-emoji-text">没什么意思呀</span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390948555392226331" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"></span></span><span class="u2QdU6ht">用*****：</span><span class="WsJsvMP9"><span class="webcast-chatroom___content-with-emoji-text">互粉</span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390949669407659035" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"></span></span><span class="u2QdU6ht">用*****：</span><span class="WsJsvMP9"><div class="webcast-chatroom___content-with-emoji-emoji " style="width: 20px; height: 20px;"><img draggable="false" src="https://p3-pc-sign.douyinpic.com/obj/tos-cn-i-tsj2vxp0zn/7e81dc405625453a9b550f28c76c3021?x-expires=2036196000&amp;x-signature=IZrSaiez7%2BQ1%2B%2BVI2NebslhkgFA%3D&amp;from=876277922" alt="[啤酒]"></div></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390950154986132530" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_17.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">風*****：</span><span class="WsJsvMP9"><span class="webcast-chatroom___content-with-emoji-text">苗不准</span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390950288410612745" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p11-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_17.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">風*****：</span><span class="WsJsvMP9"><span class="webcast-chatroom___content-with-emoji-text">可以打主播那两个吗</span><div class="webcast-chatroom___content-with-emoji-emoji " style="width: 20px; height: 20px;"><img draggable="false" src="https://p3-pc-sign.douyinpic.com/obj/tos-cn-i-tsj2vxp0zn/03f3147990b14955a28902cb1b80d160?x-expires=2036196000&amp;x-signature=pRoT5D16K2Rzznrsn8iHROoqu7g%3D&amp;from=876277922" alt="[捂脸]"></div><div class="webcast-chatroom___content-with-emoji-emoji " style="width: 20px; height: 20px;"><img draggable="false" src="https://p3-pc-sign.douyinpic.com/obj/tos-cn-i-tsj2vxp0zn/03f3147990b14955a28902cb1b80d160?x-expires=2036196000&amp;x-signature=pRoT5D16K2Rzznrsn8iHROoqu7g%3D&amp;from=876277922" alt="[捂脸]"></div></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390951957260280844" style="transition: all 300ms ease 0s;"><div class="webcast-chatroom__room-message">欢迎来到直播间！抖音严禁未成年人直播或打赏。直播间内严禁出现违法违规、低俗色情、吸烟酗酒、人身伤害等内容。如主播在直播过程中以不当方式诱导打赏、私下交易，请谨慎判断，以防 人身财产损失。请大家注意财产安全，理性消费，谨防网络诈骗。</div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390951942920508451" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_13.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">琦*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p3-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952052744115200" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p11-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_1.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">🌺*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p11-webcast.douyinpic.com/img/webcast/802a21ae29f9fae5abe3693de9f874bd~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952134094230528" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_27.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">笨*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p3-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952453979509795" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p11-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_20.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">远*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p11-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952552474792994" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_4.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">用*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p11-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952569898587145" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_18.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">五*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p3-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952600746857512" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_4.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">用*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p3-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;1</span></span></span></span></div></div><div class="webcast-chatroom___item webcast-chatroom___enter-done" data-id="7390952608850514944" style="transition: all 300ms ease 0s;"><div class="TNg5meqw"><span style="cursor: pointer; display: inline-block; height: 20px; vertical-align: middle;"><span class="k3s5qMFF"><span class="e7Bc18Wu"><img alt="" src="https://p3-webcast.douyinpic.com/img/webcast/new_user_grade_level_v1_6.png~tplv-obj.image" height="18"></span></span></span><span class="u2QdU6ht">贝*****：</span><span class="WsJsvMP9"><span class="lEfJhurR"><span class="hH0pxiDh">送出了<img class="DyNQfBip" src="https://p3-webcast.douyinpic.com/img/webcast/7ef47758a435313180e6b78b056dda4e.png~tplv-obj.png" alt=""><span class="tbZ6dkVE">&nbsp;×&nbsp;2</span></span></span></span></div></div>'

def getRedis():
    return redis.Redis(connection_pool=pool)

if __name__ == '__main__':
    # r = redis.Redis(host='localhost', port=6379, db=0)
    # dy:message:hash:694742422766
    pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
    url = 'https://live.douyin.com/694742422766'
    numbers = re.findall(r"\d+", url)
    liveId = numbers[0]
    print("房间号:",liveId)
    start(url)
    # 提取房间号
    # parse_latest(string)
    # parse_content(string1)





