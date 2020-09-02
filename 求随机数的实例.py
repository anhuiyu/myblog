"""
求一个0~255的随机数
"""
import random
ret=random.randint(0,255)
print(ret)

#如何生成五位数的字母和数字随机组合的验证码，“A3bv7”
tmp_list=[]
for i in range(5):
    #生成大写字母
    u=chr(random.randint(65,90))
    #生成小写字母
    l=chr(random.randint(97,122))
    #生成数字
    n=str(random.randint(0,9))
    tmp=random.choice([u,l,n])
    tmp_list.append(tmp)
print("".join(tmp_list))