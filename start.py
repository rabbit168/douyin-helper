import os
import subprocess
import sys

abs_path = os.path.split(os.path.abspath(__file__))[0]

if len(sys.argv)==0:
    print("参数不够")
print(sys.argv[1])

douyin = os.path.join(abs_path,'douyin.py')
yuyin = os.path.join(abs_path,'yuyin.py')
# frame_server = os.path.join(abs_path,'frame_server.py')
# 149260322188

subprocess.Popen("python %s %s"%(douyin,sys.argv[1]))
subprocess.Popen("python %s %s"%(yuyin,sys.argv[1]))
# subprocess.Popen("python "+frame_server)