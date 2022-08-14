import queue,datetime,pytz
from time import sleep
from retry import retry
from hashlib import md5
from TaskFactory import BaseTask
from TaskTable import TaskTable
from TaskStat import StatManager
from TaskCron import IsTimeHit
from concurrent.futures import ThreadPoolExecutor
from bdpyconsts import bdpyconsts

class TaskTimer:
    # 定时器实例
    __timer = None
    
    def __new__(cls,*args,**kwargs):
        if not cls.__timer:
            cls.__timer = object.__new__(cls)
        return cls.__timer
    
    
    def __init__(self,console:bool) -> None:
        # 是否打印执行记录
        self.console = console
        
        # 任务表格
        self.__task_table = TaskTable()
        # 任务执行统计
        self.__task_stat = StatManager(task=None)
        # 初始化队列
        self.__task_sched_queue = queue.Queue(maxsize=1)
        self.__task_single_queue = queue.Queue(maxsize=1)
        # 任务ID记录
        self.__task_ids = {}
        
        # 启动线程池管理
        mxw = bdpyconsts.MAX_TASK_THREAD
        if not mxw:
            mxw = 20
        self.__pool = ThreadPoolExecutor(max_workers=mxw)
        
    
    def run(self,):
        """
        开启时间循环
        
        :return:
        """
        # 启动日志打印
        self.__pool.submit(self.console_log)
        # 启动定时任务监听
        self.__pool.submit(self.run_sched_tasks)
        # 启动循环任务
        self.run_sed_loop_tasks()
        
        # 启动时间心跳
        while True:
            try:
                sleep(1)
                self.__task_sched_queue.put_nowait(1)
                self.__task_single_queue.put_nowait(1)
            except queue.Full:
                pass
    
    
    def console_log(self,):
        """
        打印执行日志
        
        :return:
        """
        if not self.console:
            return
        
        last_count = self.__task_stat.run_times
        while True:
            sleep(1)
            current_count = self.__task_stat.run_times
            if current_count > last_count:
                print(self.__task_stat.summary())
                print(self.__task_stat.detail(after=last_count - 1))
                last_count = current_count
    
    
    def run_sched_tasks(self,):
        """
        运行定时任务
        
        :return:
        """
        while True:
            self.__task_sched_queue.get()
            tm = datetime.datetime.now(tz=pytz.timezone(bdpyconsts.TIME_ZONE))
            for task in self.__task_table.range_schedule_task():
                self.__pool.submit(self.run_task_with_retry,task=task,tm=tm)
    
    
    def run_task_with_retry(self,task:BaseTask,tm=datetime.datetime):
        """
        运行一个定时任务执行函数
        
        :param task: BaseTask 任务类
        :param tm: 当前时间
        """
        # 时间表达式定时
        if task.run_type() == BaseTask.TASK_RUN_SCHEDULE:
            if not IsTimeHit(con=task.shcd_con(),tm=tm):
                return None
        
        # 单次运行定时
        elif task.run_type() == BaseTask.TASK_RUN_SINGLE:
            # 已执行过
            if task.name() in self.__task_stat.task_stats:
                return None
            
            # 判断是否到了执行时间
            run_at = task.single_tm()
            if run_at.startswith(BaseTask.SINGLE_TASK_RUN_TIME):
                run_tm = datetime.datetime.strptime(run_at.replace(BaseTask.SINGLE_TASK_RUN_TIME, ""),"%Y-%m-%d %H:%M:%S")
                if run_tm.__gt__(self.__task_stat.start_at):
                    return None
            # 判断是否到了执行秒数
            elif run_at.startswith(BaseTask.SINGLE_TASK_RUN_AFTER):
                run_af = int(run_at.replace(BaseTask.SINGLE_TASK_RUN_AFTER, ""))
                tn = int(datetime.datetime.now().timestamp())
                ts = int(self.__task_stat.start_at.timestamp())
                if (tn - ts) < run_af:
                    return None
        # 秒循环定时,在这里不处理
        else:
            return None
        
        if not task.timeout():
            tmout = None
        else:
            tmout = task.timeout()
        
        # 使用重试方法执行任务
        task_id = retry(tries=task.trytimes(),delay=task.try_after(),max_delay=tmout)(self.__task_call_back,task=task,tm=tm)
        del self.__task_ids[task_id]
    
    
    def run_sed_loop_tasks(self,):
        """
        运行时间循环任务
        
        :return:
        """
        for task in self.__task_table.__loop_tasks:
            self.__pool.submit(self.__run_loop_task_with_retry,task=task)
    
    
    def __run_loop_task_with_retry(self,task:BaseTask):
        """
        运行一个循环任务执行函数
        
        :param task: BaseTask 任务类
        :param tm: 当前时间
        """
        if not task.timeout():
                tmout = None
        else:
            tmout = task.timeout()
        
        while True:
            sleep(task.loop_sed())
            
            # 使用重试方法执行任务
            tm = datetime.datetime.now(tz=pytz.timezone(bdpyconsts.TIME_ZONE))
            task_id = retry(tries=task.trytimes(),delay=task.try_after(),max_delay=tmout)(self.__task_call_back,task=task,tm=tm)
            del self.__task_ids[task_id]
        
    
    # TODO 内存,cpu 消耗计算,异常日志记录
    def __task_call_back(self,task:BaseTask,tm=datetime.datetime):
        """
        运行一个任务执行函数
        
        :param task: BaseTask 任务类
        :param tm: 当前时间
        """
        # 任务ID标记
        task_id = "%s_%s" % (str(tm),task.name())
        task_id = md5(task_id.encode(encoding="utf-8")).hexdigest()
        
        # 任务重试判断
        if task_id in self.__task_ids:
            rety = True
        else:
            rety = False
            self.__task_ids[rety] = True
        
        # 任务执行
        ok = False
        msg = ""
        try:
            ins = object.__new__(task)
            ok = ins.run(tm=tm)
            if ok :
                ins.after()
        except Exception as e:
            msg = str(e)
            raise e
        finally:
            # 执行记录
            self.__task_stat.stat(
                success=ok,
                st=tm,
                ed=datetime.datetime.now(tz=pytz.timezone(bdpyconsts.TIME_ZONE)),
                mem=0,
                cpu=0,
                rety=rety,
                msg=msg
            )
        
        return task_id