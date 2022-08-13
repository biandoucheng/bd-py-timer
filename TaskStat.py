import datetime
from TaskFactory import BaseTask

class StatManager:
    # 全局状态统计
    task_stats = {}
    
    def __new__(cls,task:BaseTask):
        # 实例化状态管理器
        name = task.name()
        if task.name() not in cls.task_stats:
            cls.task_stats[name] = object.__new__(cls)
        return cls.task_stats[name]
    
    def __init__(self,task:BaseTask):
        """
        初始化状态统计
        
        :param task: BaseTask 任务类
        """
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
    
    def stat(self,success:bool,st:datetime.datetime,ed:datetime.datetime,mem:int,cpu:float,rety:bool):
        """
        执行结果统计
        
        :param success: bool 是否成功
        :param st: datetime 开始执行时间
        :param ed: datetime 结束执行时间
        :param mem: int 消耗内存 M
        :param cpu: 暂用cpu float
        :param rety: bool 是否属于重试
        """
        self.count += 1
        self.last_at = ed
        
        # 成功记录
        if success:
            self.success += 1
        
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
        if len(self.run_list) > 30:
            self.run_list = self.run_list[0:29]
        self.run_list.append({
            "name":self.name,
            "alias":self.alias,
            "retry":rety,
            "st":st,
            "ed":ed,
            "tmcost":tmcost,
            "mem":mem,
            "cpu":cpu,
            "success":success
        })
    
    def summary(self,) -> str:
        """
        输出执行状态的摘要
        
        :return: str
        """
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
    
    def detail(self,) -> str:
        """
        输出详细的任务执行描述
         "name":self.name,
            "alias":self.alias,
            "retry":rety,
            "st":st,
            "ed":ed,
            "tmcost":tmcost,
            "mem":mem,
            "cpu":cpu,
            "success":success
        
        :return: str
        """
        head = """
    head   %s  |  %s  |  %s
    tab    retry | st | ed | tmcost | mem | cpu | success 
        
        """ % (self.name,self.alias,self.run_type)
        det = """
          %s  --  %s  --  %s  --  %d  --  %d  --  %f  --  %d
        """
        desbs = []
        for recd in self.run_list:
            desbs.append(det % (str(recd["retry"]),str(recd["st"]),str(recd["ed"]),recd["tmcost"],recd["mem"],recd["cpu"],recd["success"]))
        
        return head + "\r\n".join(desbs)