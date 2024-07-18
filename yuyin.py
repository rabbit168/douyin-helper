import pyttsx3
import redis
import sys
import math
import json
import time

hashKey_prefix = 'dy:message:hash'

def getRedis():
    return redis.Redis(connection_pool=pool)

# pyttsx3.speak("欢迎张三加入直播间")

# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# # 遍历可用的语音，选择您觉得合适的
# for voice in voices:
#     print(voice.id)
#     engine.setProperty('voice', voice.id)
#     engine.setProperty('rate', 200)  # 调整语速，数值越大速度越快
#     engine.setProperty('volume', 1)  # 调整音量，范围在 0 到 1 之间
#     engine.say("欢迎张三加入直播间")
#     # pyttsx3.speak("欢迎张三加入直播间")
#     engine.runAndWait()



if __name__ == '__main__':
    # r = redis.Redis(host='localhost', port=6379, db=0)
    # dy:message:hash:694742422766
    pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
    liveId = '694742422766'
    # liveId = sys[0]

    redisClient = getRedis()
    pushKey = '%s:latest:%s'%(hashKey_prefix,liveId)

    while True:
        try:
            start = time.time()
            if redisClient.llen(pushKey)>0:
                res = redisClient.rpop(pushKey)
                print('时间1::::::::',time.time()-start)
                res = json.loads(res)
                print('时间2::::::::',time.time()-start)
                print(res)
                if '来了' in res['message']:
                    msg = "欢迎%s,点点关注"%res['voice']
                if '点赞' in res['message']:
                    msg = "谢谢%s点赞"%res['voice']
                print(msg)
                pyttsx3.speak(msg)
                print('时间3::::::::',time.time()-start)
        except BaseException as e:
            print(e)
