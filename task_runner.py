#!/usr/bin/env python3
"""
带超时检测和进度输出的任务执行器

功能：
1. 执行长时间任务
2. 超时后检测任务是否仍在运行
3. 如果任务正常运行，输出进展并继续
4. 如果任务真正失败，则放弃并报错
"""

import subprocess
import sys
import time
import threading
import signal

class TaskRunner:
    """带超时检测的任务执行器"""
    
    def __init__(self, timeout=60, check_interval=5):
        self.timeout = timeout
        self.check_interval = check_interval
        self.process = None
        self.start_time = None
        self.last_output_time = None
        self.is_running = True
        
    def run(self, command, cwd=None):
        """
        执行命令，支持超时检测
        
        Args:
            command: 命令列表或字符串
            cwd: 工作目录
        
        Returns:
            tuple: (returncode, stdout, stderr)
        """
        self.start_time = time.time()
        self.last_output_time = time.time()
        
        # 启动进程
        if isinstance(command, str):
            command = command.split()
        
        print(f"🚀 开始执行: {' '.join(command)}")
        
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            text=True
        )
        
        # 启动超时检测线程
        monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        monitor_thread.start()
        
        # 等待进程完成
        try:
            stdout, stderr = self.process.communicate()
            self.is_running = False
            return self.process.returncode, stdout, stderr
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            return -1, "", str(e)
    
    def _monitor(self):
        """监控进程状态"""
        while self.is_running and self.process:
            elapsed = time.time() - self.start_time
            
            # 检查进程是否还在运行
            if self.process.poll() is not None:
                # 进程已结束
                break
            
            # 检查是否超时
            if elapsed > self.timeout:
                print(f"\n⚠️ 已超时 ({self.timeout}秒)，检测任务状态...")
                
                # 检测进程是否仍在运行
                if self.process.poll() is None:
                    # 进程仍在运行，可能是正常执行中
                    print(f"✅ 任务仍在运行 (已运行 {int(elapsed)}秒)")
                    print(f"📊 继续等待...")
                    
                    # 延长超时时间
                    self.timeout = int(elapsed * 1.5)
                    print(f"⏰ 新超时时间: {self.timeout}秒")
                else:
                    # 进程已结束
                    print(f"❌ 任务已终止")
                    break
            
            time.sleep(self.check_interval)
    
    def run_with_progress(self, command, cwd=None, progress_callback=None):
        """
        执行命令并定期输出进度
        
        Args:
            command: 命令列表或字符串
            cwd: 工作目录
            progress_callback: 进度回调函数
        
        Returns:
            tuple: (returncode, stdout, stderr)
        """
        self.start_time = time.time()
        
        if isinstance(command, str):
            command = command.split()
        
        print(f"🚀 开始执行: {' '.join(command)}")
        
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True
        )
        
        output_lines = []
        
        # 逐行读取输出
        while True:
            line = self.process.stdout.readline()
            if not line and self.process.poll() is not None:
                break
            
            if line:
                output_lines.append(line)
                print(f"  {line.rstrip()}")
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(line)
                
                self.last_output_time = time.time()
            
            # 检查超时
            elapsed = time.time() - self.start_time
            if elapsed > self.timeout:
                # 检查进程是否还在运行
                if self.process.poll() is None:
                    print(f"\n⚠️ 超时但任务仍在运行，继续等待...")
                    self.timeout = int(elapsed * 2)
                else:
                    break
        
        stdout = ''.join(output_lines)
        return self.process.returncode, stdout, ""


# ============== 使用示例 ==============
if __name__ == "__main__":
    import asyncio
    
    # 示例：执行一个长时间任务
    def progress_handler(line):
        """进度处理"""
        if "error" in line.lower():
            print(f"⚠️ 检测到错误: {line}")
    
    # 创建任务执行器（超时60秒）
    runner = TaskRunner(timeout=60, check_interval=5)
    
    # 示例命令
    command = ["sleep", "30"]  # 模拟长时间任务
    
    # 执行
    returncode, stdout, stderr = runner.run_with_progress(
        command,
        progress_callback=progress_handler
    )
    
    print(f"\n结果: returncode={returncode}")
