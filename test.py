from concurrent.futures import ThreadPoolExecutor
import time

pool = ThreadPoolExecutor(max_workers=10)

def fun1(s:str):
    print("fun1 %s start" % s)
    time.sleep(5)
    print("fun1 %s end" % s)


def f1():
    for i in range(5):
        pool.submit(fun1,str(i))


def f2():
    for i in [5,6,7,8]:
        pool.submit(fun1,str(i))


for i in range(2):
    if i == 0:
        f1()
    else:
        f2()

pool.submit(fun1,"111")

