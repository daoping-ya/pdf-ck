import json
import os
from config import Config

class SettingsManager:
    _instance = None
    _settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
    
    # 默认设置
    _default_settings = {
        "enable_ocr": False,
        "enable_layout_preservation": False,  # 排版复刻(增强提取)
        "max_workers": 1
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    def _load_settings(self):
        """加载设置,如果文件不存在则使用默认值"""
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # 合并默认设置,确保新字段存在
                    self.settings = {**self._default_settings, **saved_settings}
            except Exception:
                self.settings = self._default_settings.copy()
        else:
            self.settings = self._default_settings.copy()
            self._save_settings()

    def _save_settings(self):
        """保存设置到文件"""
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        if key in self._default_settings:
            self.settings[key] = value
            self._save_settings()
            return True
        return False

    def get_all(self):
        return self.settings

# 全局实例
settings = SettingsManager()
