from ast import Try
from asyncio import Task
import datetime,pytz
from TaskFactory import BaseTask
from bdpyconsts import bdpyconsts

class StatManager:
    # 全局状态统计
    task_stats = {}
    # 开始时间
    start_at = ""
    # 总任务数
    task_count = 0
    # 总执行次数
    run_times = 0
    # 成功次数
    success_times = 0
    # 最近一次执行的任务
    last_run_task = ""
    # 最后一次执行时间
    last_run_at = ""
    # 最后一次执行状态
    last_run_success = ""
    # 最后一次执行错误信息
    last_run_msg = ""
    
    def __new__(cls,task:BaseTask):
        # 启动时间
        if not cls.start_at:
            cls.start_at = datetime.datetime.now(tz=pytz.timezone(bdpyconsts.TIME_ZONE))
        
        # 实例化主状态管理器
        if not Task:
            return object.__new__(cls)

        # 实例化状态管理器
        name = task.name()
        if name not in cls.task_stats:
            cls.task_stats[name] = object.__new__(cls)
            cls.task_count += 1
        return cls.task_stats[name]
    
    def __init__(self,task:BaseTask):
        """
        初始化状态统计
        
        :param task: BaseTask 任务类
        """
        # 是否是主状态管理器
        if task == None:
            self.__master = True
            return
        else:
            self.__master = False
        # 任务名称
        self.name = task.name()
        # 任务别名
        self.alias = task.alias()
        # 执行类型
        self.run_type = task.run_type()
        # 执行次数
        self.count = 0
        # 重试次数
        self.rety = 0
        # 平均执行耗时
        self.tm_avg = 0
        # 最大耗时
        self.tm_max = 0
        # 平均内存消耗 M
        self.mem_avg = 0
        # 最大内存消耗
        self.mem_max = 0
        # 平均cpu 消耗
        self.cpu_avg = 0.0
        # 最大cpu消耗
        self.cpu_max = 0.0
        # 成功次数
        self.success = 0
        # 成功率
        self.success_rate = 1.0
        # 最后一次执行时间
        self.last_at = None
        # 运行记录
        self.run_list = []
    
    def stat(self,success:bool,st:datetime.datetime,ed:datetime.datetime,mem:int,cpu:float,rety:bool,msg:str):
        """
        执行结果统计
        
        :param success: bool 是否成功
        :param st: datetime 开始执行时间
        :param ed: datetime 结束执行时间
        :param mem: int 消耗内存 M
        :param cpu: 暂用cpu float
        :param rety: bool 是否属于重试
        :param msg: str 错误信息
        """
        if self.__master == True:
            return
        
        # 类统计
        StatManager.run_times += 1
        StatManager.last_run_at = ed
        StatManager.last_run_task = self.name
        
        # 对象统计
        self.count += 1
        self.last_at = ed
        
        # 成功记录
        if success:
            self.success += 1
            StatManager.success_times += 1
            StatManager.last_run_success = True
        else:
            StatManager.last_run_success = False
        
        # 成功率计算
        self.success_rate = round(self.success / self.count,2)
        
        # 平均耗时计算
        stmp = st.timestamp()
        edtmp = ed.timestamp()
        tmcost = int(edtmp - stmp)
        self.tm_avg = int((self.tm_avg * (self.count - 1) + tmcost) / self.count)
        
        if tmcost > self.tm_max:
            self.tm_max = tmcost
        
        # 内存消耗率计算
        self.mem_avg = int((self.mem_avg * (self.count - 1) + mem) / self.count)
        if mem > self.mem_max:
            self.mem_max = mem
        
        # cpu 消耗率计算
        self.cpu_avg = round((self.cpu_avg * (self.count - 1) + cpu) / self.count,2)
        if cpu > self.cpu_max:
            self.cpu_max = cpu
        
        # 重试统计
        if rety:
            self.rety += 1
        
        # 添加运行记录
        if len(self.run_list) > 10:
            self.run_list = self.run_list[0:9]
        self.run_list.append({
            "name":self.name,
            "alias":self.alias,
            "retry":rety,
            "st":st,
            "ed":ed,
            "tmcost":tmcost,
            "mem":mem,
            "cpu":cpu,
            "success":success,
            "msg":msg
        })
    
    def summary(self,) -> str:
        """
        输出执行状态的摘要
        
        :return: str
        """
        if self.__master == True:
            return ""
            
        return """"
    head   %s   |  %s  |  %s
    tab    count | rety | success | success_rate  | tm_avg | tm_max | mem_avg | mem_max | cpu_avg | cpu_max | last_at
        
           %s  --  %s  --  %s  --  %d  --  %d  --  %d  --  %f --  %d  --  %d  --  %d --  %d  --  %f  --  %f  --  %s    
        
        """ % (
            self.name,self.alias,self.run_type,
            self.count,self.rety,self.success,
            self.success_rate,self.tm_avg,
            self.tm_max,self.mem_avg,
            self.mem_max,self.cpu_avg,
            self.cpu_max,str(self.last_at)
            )
    
    def detail(self,after:int=0) -> str:
        """
        输出详细的任务执行描述
        
        :return: str
        """
        if self.__master == True:
            return ""
            
        head = """
    head   %s  |  %s  |  %s
    tab    retry | st | ed | tmcost | mem | cpu | success | msg
        
        """ % (self.name,self.alias,self.run_type)
        det = """
          %s  --  %s  --  %s  --  %d  --  %d  --  %f  --  %d  --  %s
        """
        desbs = []
        for recd in self.run_list[after:len(self.run_list - 1)]:
            desbs.append(det % (str(recd["retry"]),str(recd["st"]),str(recd["ed"]),recd["tmcost"],recd["mem"],recd["cpu"],recd["success"],recd["msg"]))
        
        return head + "\r\n".join(desbs)
    
    @classmethod
    def describe(cls,) -> str:
        """
        类统计记录
        
        :return: str
        """
        tn = datetime.datetime.now(tz=pytz.timezone(bdpyconsts.TIME_ZONE))
        
        return """
head   %s  |  %s | %d 
tab    run_times | success_times | last_run_task | last_run_at | success | msg
       %d  --  %d  -- %s  --  %s  --  %d  --  %s
    
    """ % (str(cls.start_at),str(tn),cls.task_count,cls.run_times,cls.success_times,cls.last_run_task,str(cls.last_run_at),cls.last_run_success,cls.last_run_msg)