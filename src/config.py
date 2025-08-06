import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Configuration manager for the Wonder Discord Bot"""
    
    def __init__(self, config_path: str = "../config.json"):
        self.config_path = Path(__file__).parent / config_path
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Save configuration to JSON file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    @property
    def prefix(self) -> str:
        return self.get('prefix', 'w.')
    
    @property
    def currency(self) -> Dict[str, Any]:
        return self.get('currency', {})
    
    @property
    def branding(self) -> Dict[str, Any]:
        return self.get('branding', {})
    
    @property
    def colors(self) -> Dict[str, str]:
        return self.get('colors', {})
    
    @property
    def theme(self) -> Dict[str, Any]:
        return self.get('theme', {})
    
    @property
    def cooldowns(self) -> Dict[str, int]:
        return self.get('cooldowns', {})
    
    @property
    def games(self) -> Dict[str, Any]:
        return self.get('games', {})
    
    @property
    def shop(self) -> Dict[str, Any]:
        return self.get('shop', {})
    
    @property
    def giveaways(self) -> Dict[str, Any]:
        return self.get('giveaways', {})
    
    @property
    def leveling(self) -> Dict[str, Any]:
        return self.get('leveling', {})

# Global config instance
config = Config()