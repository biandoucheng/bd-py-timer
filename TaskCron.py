# 定时规则
'''
时间范围表示
*       每个时间点
*,*     指定某些时间点
*-*     指定时间范围的每个时间点
*/*     在时间范围内要求执行*次
*/*-*   在指定时间范围内要求执行*次
*,*/*-* 在指定时间范围内要求执行*次

时间单元
*   年
*   月 1-12/12
*   日 1-31/31 按月份不同
*   周 1-7/7
*   时 0-23/24
*   分 0-59/60
*   秒 0-59/60
'''
import abc,datetime,re,pytz
from bdpyconsts import bdpyconsts

# 时区
_TIME_ZONE = bdpyconsts.TIME_ZONE
if not _TIME_ZONE:
    _TIME_ZONE = "Asia/Shanghai"

#指定时间点正则
_TIME_HIT_POINT_PREG = re.compile(r'^\d+(\,\d+)+$')
#指定范围任意正则
_TIME_HIT_RANGE_ANYWAY_PREG = re.compile(r'^\d+\-\d+$')
#指定次数正则
_TIME_HIT_TIMES_PREG = re.compile(r'^\d+\/\*$')
#指定范围指定次数正则
_TIME_HIT_RANGE_TIMES_PREG = re.compile(r'^\d+\/\d+\-\d+$')
#指定范围指定时间点正则
_TIME_HIT_RANGE_POINT_PREG = re.compile(r'^\d+(\,\d+)+\/\d+\-\d+$')

def IsTimeHit(con:str,tm:datetime.datetime=None) -> bool:
    """
    判断时间是否命中
    
    :param con: str 定时表达式
    :param tm: datetime 时间对象
    """
    cons = con.strip().split(" ")
    if len(cons) != 7:
        return False
    
    if not tm:
        tm = datetime.datetime.now(tz=pytz.timezone(_TIME_ZONE))
    
    # 年判断
    year = Year(tm=tm)
    year.parse(con=cons[0])
    if not year.hit():
        return False
    
    # 月判断
    month = Month(tm=tm)
    month.parse(con=cons[1])
    if not month.hit():
        return False
    
    # 日判断
    day = Day(tm=tm)
    day.parse(con=cons[2])
    if not day.hit():
        return False
    
    # 周判断
    week = Week(tm=tm)
    week.parse(con=cons[3])
    if not week.hit():
        return False
    
    # 时判断
    hour = Hour(tm=tm)
    hour.parse(con=cons[4])
    if not hour.hit():
        return False
    
    # 分判断
    minute = Minute(tm=tm)
    minute.parse(con=cons[5])
    if not minute.hit():
        return False
    
    # 秒判断
    second = Second(tm=tm)
    second.parse(con=cons[6])
    if not second.hit():
        return False
    
    return True


class Cron:
    """
    时间检测器
    """
    
    # 时间命中标志 永不
    TIME_HIT_NEVER = "!"
    # 时间命中标志 任意
    TIME_HIT_ANYWAY = "*"
    # 时间命中标志 指定时间点
    TIME_HIT_POINT  = "*,*"
    # 时间命中标志 指定范围任意
    TIME_HIT_RANGE_ANYWAY = "*-*"
    # 时间命中标志 指定次数
    TIME_HIT_TIMES = "*/*"
    # 时间命中标志 指定范围指定次数
    TIME_HIT_RANGE_TIMES = "*/*-*"
    # 时间命中标志 指定范围指定时间点
    TIME_HIT_RANGE_POINT = "*,*/*-*"
    
    def __init__(self):
        # 时间表达式
        self.__con = None
        # 时间命中标志
        self.__hit_flg = None
        # 命中时间点
        self.__hit_point = set()
    
    def load(self,con:str):
        """
        加载时间表达式
        
        :param con: str 时间表达式
        """
        self.__con = con.strip()
    
    def parse(self,min:int,max:int):
        """
        解析时间表达式
        
        :param min: int 最小时间值
        :param max: int 最大时间值
        :return:
        """
        if self.__con == self.TIME_HIT_ANYWAY:
            self.__hit_flg = self.TIME_HIT_ANYWAY
            return
        
        if _TIME_HIT_POINT_PREG.match(self.__con):
            self.__hit_flg = self.TIME_HIT_POINT
            vs = self.__con.split(",")
            for v in vs:
                self.__hit_point.add(int(v))
            return
        
        if _TIME_HIT_RANGE_ANYWAY_PREG.match(self.__con):
            self.__hit_flg = self.TIME_HIT_RANGE_ANYWAY
            vs = self.__con.split("-")
            vmin = int(vs[0])
            vmax = int(vs[-1])
            while vmin <= vmax:
                self.__hit_point.add(vmin)
                vmin += 1
            return
        
        if _TIME_HIT_TIMES_PREG.match(self.__con):
            tms = int(self.__con.strip("*/"))
            if tms == 0 or (not min or not max):
                self.__hit_flg = self.TIME_HIT_NEVER
                return
            self.__hit_flg = self.TIME_HIT_TIMES
            long = max - min + 1
            block = long / tms
            start = min
            while start <= max:
                self.__hit_point.add(start)
                start += block
            return
        
        if _TIME_HIT_RANGE_TIMES_PREG.match(self.__con):
            con = self.__con.replace("/", ",").replace("-", ",")
            vls = con.split(",")
            tms = int(vls[0])
            vmi = int(vls[1])
            vmx = int(vls[-1])
            long = vmx - vmi + 1
            if tms == 0 or vmx == 0 or vmx < vmi:
                self.__hit_flg = self.TIME_HIT_NEVER
                return
            self.__hit_flg = self.TIME_HIT_RANGE_TIMES
            block = long / tms
            while vmi <= vmax:
                self.__hit_point.add(vmi)
                vmi += block
            return
        
        if _TIME_HIT_RANGE_POINT_PREG.match(self.__con):
            vls = self.__con.split("/")
            pts = vls[0].split(",")
            rgs = vls[-1].split("-")
            rmi = int(rgs[0])
            rmx = int(rgs[-1])
            if rmx < rmi:
                self.__hit_flg = self.TIME_HIT_NEVER
                return
            self.__hit_flg = self.TIME_HIT_RANGE_POINT
            for p in pts:
                pv = int(p)
                if p >= rmi and p <= rmx:
                    self.__hit_point.add(pv)
            return
        
        self.__hit_flg = self.TIME_HIT_NEVER
        
    
    def hit(self,point:int) -> bool:
        """
        判断是否命中
        
        :paream point: int 当前时间点
        :return: bool
        """
        if self.__hit_flg == None or self.__hit_flg == self.TIME_HIT_NEVER:
            return False
        if self.__hit_flg == self.TIME_HIT_ANYWAY:
            return True
        
        return point in self.__hit_point
        

class CronUnit(metaclass=abc.ABCMeta):
    """
    时间单位抽象定义
    """
    
    def load(self,tm:datetime.datetime):
        """
        时间初始化
        
        :return:
        """
        self.__time = tm
    
    @abc.abstractmethod
    def parse(self,con:str):
        """
        初始化时间表达式
        
        :param con: str 时间表达式
        :return:
        """
    
    @abc.abstractmethod
    def long(self,) -> int:
        """
        返回时间长度
        
        :return: int 时间长度
        """
    
    def min(self,) -> int:
        """
        返回时间最小值
        
        :return: int 时间最小值
        """
    
    @abc.abstractmethod
    def max(self,) -> int:
        """
        返回时间最大值
        
        :return: int 时间最大值
        """
    
    @abc.abstractmethod
    def current(self,) -> int:
        """
        获取当前值
        
        :return: int 当前时间值
        """
    
    @abc.abstractmethod
    def desc(self,) -> str:
        """
        时间描述
        
        :return: str 获取时间描述
        """
    
    @abc.abstractmethod
    def hit(self,con:str) -> bool:
        """
        判断时间是否命中
        
        :param con: str 时间命中判断
        """


class Year(CronUnit):
    """
    时间单元 年
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = None
        # 最小值
        self.__min = None
        # 最大值
        self.__max = None
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.year
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "%s 年" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())


class Month(CronUnit):
    """
    时间单元 月
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = 12
        # 最小值
        self.__min = 1
        # 最大值
        self.__max = 12
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.month
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "%s 月" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())


class Day(CronUnit):
    """
    时间单元 日
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = None
        # 最小值
        self.__min = 1
        # 最大值
        self.__max = None
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.day
        if self.__current in [1,3,5,7,8,10,12]:
            self.__long = 31
            self.__max = 31
        elif self.__current in [4,6,9,11]:
            self.__long = 30
            self.__max = 30
        else:
            year = tm.year
            if year % 4 == 0 or year % 100 == 0 or year % 400 == 0:
                self.__long = 29
                self.__max = 29
            else:
                self.__long = 28
                self.__max = 28
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "%s 日" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())


class Week(CronUnit):
    """
    时间单元 周
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = 7
        # 最小值
        self.__min = 1
        # 最大值
        self.__max = 7
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.weekday() + 1
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "周 %s" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())


class Hour(CronUnit):
    """
    时间单元 小时
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = 24
        # 最小值
        self.__min = 0
        # 最大值
        self.__max = 23
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.hour
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "%s 时" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())


class Minute(CronUnit):
    """
    时间单元 分钟
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = 60
        # 最小值
        self.__min = 0
        # 最大值
        self.__max = 59
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.hour
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "%s 分" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())


class Second(CronUnit):
    """
    时间单元 秒
    """
    
    def __init__(self,tm:datetime.datetime=None):
        """
        初始化时间
        
        :param tm: datetime.datetime 时间对象
        """
        # 时间对象
        self.__time = None
        
        # 初始化时间对象
        if tm:
            self.load(tm)
        
        # 时间长度
        self.__long = 60
        # 最小值
        self.__min = 0
        # 最大值
        self.__max = 59
        # 当前值
        self.__current = None
    
    def load(self, tm: datetime.datetime):
        self.__time = tm
        self.__current = tm.second
    
    def parse(self, con: str):
        self.__croner = Cron(con)
        self.__croner.parse(self.__min,self.__max)
    
    def long(self) -> int:
        return self.__long
    
    def min(self) -> int:
        return self.__min
    
    def max(self) -> int:
        return self.__max
    
    def current(self) -> int:
        return self.__current
    
    def desc(self) -> str:
        return "%s 秒" % str(self.current())
    
    def hit(self,) -> bool:
        return self.__croner.hit(self.current())