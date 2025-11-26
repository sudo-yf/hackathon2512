import subprocess
import queue
import time
import threading
import platform
import os
from ..base_language import BaseLanguage

class BaseShellLanguage(BaseLanguage):
    """
    Shell语言执行器基类
    提供通用的shell命令执行功能，支持跨平台和中断机制
    """
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.output_queue = None
        self.platform = platform.system().lower()
    
    def get_shell_command(self, code: str) -> list:
        """
        获取特定shell的执行命令
        子类需要重写此方法
        """
        raise NotImplementedError("子类必须实现get_shell_command方法")
    
    def is_available(self) -> bool:
        """
        检查当前shell是否在平台上可用
        子类可以重写此方法
        """
        return True
    
    def run(self, code: str):
        """
        [llm] 执行shell命令（异步执行，返回队列）
        """
        # 重置状态
        self.should_stop = False
        self.is_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # 创建输出队列
        self.output_queue = queue.Queue()
        
        # 启动执行线程
        execution_thread = threading.Thread(
            target=self._execute_shell,
            args=(code,)
        )
        execution_thread.daemon = True
        execution_thread.start()
        
        return self.output_queue
    
    def _execute_shell(self, code: str):
        """
        在单独线程中执行shell命令
        """
        if not self.is_available():
            self.output_queue.put({"type": "text", "text": f"Shell '{self.__class__.__name__}' 在当前平台 {self.platform} 上不可用"})
            return
        
        try:
            # 构建命令
            cmd = self.get_shell_command(code)
            
            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=False,
                cwd=os.getcwd()
            )
            
            # 启动输出读取线程
            stdout_thread = threading.Thread(target=self._read_stdout)
            stderr_thread = threading.Thread(target=self._read_stderr)
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程完成或被中断
            while self.process.poll() is None:
                if self.should_stop:
                    self._terminate_process()
                    break
                time.sleep(0.1)
            
            # 等待输出线程完成
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            
            # 添加退出状态信息
            if self.process.returncode is not None:
                if self.process.returncode == 0:
                    self.output_queue.put({
                        "type": "text", 
                        "text": f"\n命令执行完成，退出码: {self.process.returncode}"
                    })
                else:
                    self.output_queue.put({
                        "type": "text", 
                        "text": f"\n命令执行失败，退出码: {self.process.returncode}"
                    })
            
        except Exception as e:
            self.output_queue.put({
                "type": "text", 
                "text": f"执行错误: {str(e)}"
            })
        
        finally:
            self.elapsed_time = time.time() - self.start_time
            self.is_running = False
            self.process = None
    
    def interrupt(self):
        """
        中断shell命令执行
        """
        super().interrupt()
        if self.process and self.process.poll() is None:
            self._terminate_process()
    
    def _terminate_process(self):
        """
        终止进程，尝试优雅终止后强制终止
        """
        if not self.process:
            return
            
        try:
            # 首先尝试优雅终止
            self.process.terminate()
            
            # 等待一段时间
            time.sleep(0.5)
            
            # 如果还在运行，强制终止
            if self.process.poll() is None:
                self.process.kill()
                
                if self.platform == 'windows':
                    # Windows上可能需要更强制的方法
                    os.system(f'taskkill /F /PID {self.process.pid}')
                    
        except Exception as e:
            # 忽略终止过程中的错误
            pass
    
    def _read_stdout(self):
        """
        读取标准输出
        """
        if not self.process:
            return
            
        try:
            while True:
                line = self.process.stdout.readline()
                if line == '' and self.process.poll() is not None:
                    break
                if line:
                    self.output_queue.put({
                        "type": "text", 
                        "text": line.rstrip()
                    })
        except Exception as e:
            self.output_queue.put({
                "type": "text", 
                "text": f"读取输出错误: {str(e)}"
            })
    
    def _read_stderr(self):
        """
        读取标准错误
        """
        if not self.process:
            return
            
        try:
            while True:
                line = self.process.stderr.readline()
                if line == '' and self.process.poll() is not None:
                    break
                if line:
                    self.output_queue.put({
                        "type": "text", 
                        "text": f"ERROR: {line.rstrip()}"
                    })
        except Exception as e:
            self.output_queue.put({
                "type": "text", 
                "text": f"读取错误输出错误: {str(e)}"
            })
