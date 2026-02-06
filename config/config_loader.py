# config/config_loader.py
import json
import os
from typing import Any, Dict, Optional

class ConfigLoader:
    _settings: Dict[str, Any] = {}
    
    def __init__(self, config_file: str = "settings.json"):
        self.config_file = config_file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._path = os.path.join(base_dir, self.config_file)        
        self._load_settings()

    def _load_settings(self):
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
        except FileNotFoundError:
            self._settings = {}
        except json.JSONDecodeError as e:
            self._settings = {}

    def save_settings(self):
        try:
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            pass
            
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        current = self._settings
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        current = self._settings
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    @property
    def EMPLOYEE_ID(self) -> int | None:
        return self.get("employee.id")

    @property
    def EMPLOYEE_NAME(self) -> str | None:
        return self.get("employee.name")

    def __repr__(self):
        return f"ConfigLoader(loaded_settings={self._settings})"

settings = ConfigLoader()