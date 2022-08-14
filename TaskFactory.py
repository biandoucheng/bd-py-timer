# 基本任务抽象类
import abc

class BaseTask(metaclass=abc.ABCMeta):
    # 任务运行模式 秒循环
    TASK_RUN_SECOND_LOOP = "SECOND_LOOP"
    # 任务运行模式 时间表
    TASK_RUN_SCHEDULE = "SCHEDULE"
    # 单次运行任务
    TASK_RUN_SINGLE = "SINGLE"
    
    # 单次任务启动之后执行时间点前缀 AFTER_30
    SINGLE_TASK_RUN_AFTER = "AFTER_"
    # 单次任务执行时间点前缀 TIME_2022-08-13 22:36:21
    SINGLE_TASK_RUN_TIME = "TIME_"
    
    @abc.abstractmethod
    @staticmethod
    def run_type(self,) -> str:
        """
        返回任务定时类型
        
        :return: str
        """
    
    @abc.abstractmethod
    @staticmethod
    def shcd_con(self,) -> str:
        """
        返回遍历输出时间表达式
        
        :return: str 定时表达式列表
        """
        return None
    
    @abc.abstractmethod
    @staticmethod
    def loop_sed(self,) -> float:
        """
        返回秒循环的秒
        
        :return: float
        """
        return None
    
    @abc.abstractmethod
    @staticmethod
    def single_tm(self,) -> str:
        """
        返回单次任务执行时间点
        """
        return None
    
    @abc.abstractmethod
    @staticmethod
    def name(self,) -> str:
        """
        任务名称或脚本名称
        
        :return: str
        """
    
    @abc.abstractmethod
    @staticmethod
    def alias(self,) -> str:
        """
        任务别名
        
        :return: str
        """
    
    @abc.abstractmethod
    @staticmethod
    def timeout(self,) -> float:
        """
        执行超时时间
        
        :return: float 超时时间|0表示无上限
        """
    
    @abc.abstractmethod
    @staticmethod
    def trytimes(self,) -> int:
        """
        失败重试次数
        
        :return: int 重试次数|0代表不重试
        """
    
    @abc.abstractmethod
    @staticmethod
    def try_after(self,) -> float:
        """
        返回重试时间间隔 
        
        :return: float
        """

    @abc.abstractmethod
    @staticmethod
    def logsend(self,msg:str):
        """
        发送日志,内部自己实现的方式
        
        :return:
        """
    
    @abc.abstractmethod
    @staticmethod
    def emails(self,)->list:
        """
        获取通知邮件列表
        
        :return: list 通知邮件列表
        """
    
    @abc.abstractmethod
    @staticmethod
    def logfile(self,)->str:
        """
        获取日志记录文件路径
        
        :return: str 日志文件路径
        """
    
    @abc.abstractmethod
    @staticmethod
    def logsuccess(self,) -> bool:
        """
        成功是否通知
        
        :return: bool
        """
        return False
    
    @abc.abstractmethod
    @staticmethod
    def logfield(self,) -> bool:
        """
        失败是否通知
        
        :return: bool
        """
        return False
    
    @abc.abstractmethod
    @staticmethod
    def logabnormal(self,) -> bool:
        """
        异常是否通知
        
        :return: bool
        """
        return False
    
    def run(self,**kwargs) -> bool:
        """
        运行入口
        
        :param kwargs: dict 字典参数
        :return: bool 是否执行成功
        """
        return True
    
    def after(self,**kwargs) -> bool:
        """
        后置钩子
        
        :param kwargs: dict 字典参数
        :return: bool 是否执行成功
        """
        return True