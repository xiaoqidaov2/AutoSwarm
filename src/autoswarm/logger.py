import logging
import logging.handlers
from typing import Optional
from pathlib import Path


def setup_logger(config, name: str = "autoswarm") -> logging.Logger:
    """
    设置 AutoSwarm 的日志系统
    
    Args:
        config: AutoSwarmConfig 对象
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.level.upper()))
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(config.logging.log_format)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if config.logging.log_file:
        log_path = Path(config.logging.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            str(log_path),
            maxBytes=config.logging.max_file_size,
            backupCount=config.logging.backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "autoswarm") -> logging.Logger:
    """
    获取已配置的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器对象
    """
    return logging.getLogger(name)
