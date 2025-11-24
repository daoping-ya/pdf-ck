import sqlite3
import threading
import uuid
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from config import Config

class TaskManager:
    """轻量级任务管理器 - 使用ThreadPool替代Celery"""
    
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or Config.MAX_WORKERS
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.db_path = Config.DB_PATH
        self.lock = threading.Lock()
        self.active_tasks = 0
        self._init_db()
    
    def _init_db(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def submit_task(self, func, *args, **kwargs):
        """提交异步任务"""
        # 检查是否超过并发限制
        with self.lock:
            if self.active_tasks >= self.max_workers:
                raise Exception("服务繁忙,请稍后再试")
            self.active_tasks += 1
        
        task_id = str(uuid.uuid4())
        self._create_task(task_id)
        
        def wrapper():
            try:
                self._update_task(task_id, 'PROCESSING', 0)
                result = func(task_id, *args, **kwargs)
                self._update_task(task_id, 'COMPLETED', 100, result=json.dumps(result))
                return result
            except Exception as e:
                self._update_task(task_id, 'FAILED', 0, error=str(e))
                raise
            finally:
                with self.lock:
                    self.active_tasks -= 1
        
        self.executor.submit(wrapper)
        return task_id
    
    def _create_task(self, task_id):
        """创建任务记录"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO tasks (task_id, status, progress) VALUES (?, ?, ?)',
                    (task_id, 'PENDING', 0)
                )
                conn.commit()
    
    def _update_task(self, task_id, status, progress, result=None, error=None):
        """更新任务状态"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE tasks 
                    SET status=?, progress=?, result=?, error=?, updated_at=CURRENT_TIMESTAMP 
                    WHERE task_id=?
                ''', (status, progress, result, error, task_id))
                conn.commit()
    
    def update_progress(self, task_id, progress):
        """更新任务进度"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'UPDATE tasks SET progress=?, updated_at=CURRENT_TIMESTAMP WHERE task_id=?',
                    (progress, task_id)
                )
                conn.commit()
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT task_id, status, progress, result, error FROM tasks WHERE task_id=?',
                (task_id,)
            )
            row = cursor.fetchone()
            
            if row:
                result_data = None
                if row[3]:
                    try:
                        result_data = json.loads(row[3])
                    except:
                        result_data = row[3]
                
                return {
                    'task_id': row[0],
                    'status': row[1],
                    'progress': row[2],
                    'result': result_data,
                    'error': row[4]
                }
            return None
    
    def cleanup_old_tasks(self, max_age_hours=3):
        """清理旧任务记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                DELETE FROM tasks 
                WHERE updated_at < datetime('now', '-{} hours')
            '''.format(max_age_hours))
            deleted = conn.total_changes
            conn.commit()
        return deleted

# 全局实例
task_manager = TaskManager()
