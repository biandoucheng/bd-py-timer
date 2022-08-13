# 基本任务抽象类
import abc

class BaseTask(metaclass=abc.ABCMeta):
    # 任务运行模式 毫秒循环
    TASK_RUN_MS_SECOND_LOOP = "MS_SECOND_LOOP"
    # 任务运行模式 时间表
    TASK_RUN_SCHEDULE = "SCHEDULE"
    # 单次运行任务
    TASK_RUN_SINGLE = "SINGLE"
    
    @abc.abstractmethod
    @staticmethod
    def run_type(self,) -> str:
        """
        返回任务定时类型
        
        :return: str
        """
    
    @staticmethod
    def loop_msd(self,) -> int:
        """
        返回毫秒循环的毫秒
        
        :return: int
        """
        return None
    
    @staticmethod
    def shcd_con(self,) -> str:
        """
        返回遍历输出时间表达式
        
        :return: str 定时表达式列表
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
    
    @staticmethod
    def logsuccess(self,) -> bool:
        """
        成功是否通知
        
        :return: bool
        """
        return False
    
    @staticmethod
    def logfield(self,) -> bool:
        """
        失败是否通知
        
        :return: bool
        """
        return False
    
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