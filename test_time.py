import time
import datetime
# timeStamp = 1597976340582
# timeArray = time.localtime(timeStamp / 1000)
# otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
# print(otherStyleTime)


# for i in range(1, 100):
#     if i*250 + i*20 < 10000:
#         print(i, (i*250 + i*20))


# a = 'audchf'

# print(datetime.now("%Y-%m-%d %H:%M:%S"))
# print(a[3:])
# print(a[:3])

ba = 30000
for i in range(1, 10000):
    if i * 250 + i * 20 < ba:
        print(i)
