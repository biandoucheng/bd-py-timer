import datetime,pytz
from email.generator import Generator
from task import BaseTask
from bdpyconsts import bdpyconsts
from cron import IsTimeHit

class TaskTable(object):
    # 单例实例
    __instance = None
    
    def __new__(cls,*args,**kwargs):
        """
        单例化
        """
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance
    
    def __init__(self,):
        # 初始化任务列表
        self.__tasks = []
        # 调度任务
        self.__schedule_tasks = []
        # 时间循环任务
        self.__loop_tasks = []
        # 单次运行任务
        self.__single_task = []
        # 启动时间
        self.run_at = datetime.datetime.now(tz=pytz.timezone(bdpyconsts.TIME_ZONE))
        # 运行时间表
        self.run_time = {}
    
    def register(self,task:BaseTask):
        """
        注册任务
        
        :param task: BaseTask 任务对象
        """
        self.__tasks.append(task)
        
        # 定时任务
        if task.run_type() == task.TASK_RUN_SCHEDULE:
            self.__schedule_tasks.append(task)
        
        # 循环任务
        if task.run_type() == task.TASK_RUN_MS_SECOND_LOOP:
            self.__loop_tasks.append(task)
            return
        
        # 单次运行任务
        if task.run_type() == task.TASK_RUN_SINGLE:
            self.__single_task.append(task)
    
    def range_schedule_task(self,tm:datetime.datetime) -> Generator:
        """
        获取需要执行的定时任务列表
        
        :param tm: datetime 时间对象
        :return: Generator
        """
        for task in self.__schedule_tasks:
            if IsTimeHit(con=task.shcd_con(),tm=tm):
                yield task
    
    @classmethod
    def register(self,task:BaseTask):
        """
        注册任务
        
        :param task: BaseTask 任务对象
        """
        if not self.__instance:
            ins = TaskTable()
        else:
            ins = self.__instance
        
        ins.register(task=task)