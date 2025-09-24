"""
网络工具模块
Network Utilities Module

提供网络连接重试、错误处理和API访问优化功能
"""

import time
import asyncio
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    带指数退避的重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # 检查是否是网络相关错误
                    network_errors = [
                        'connection error', 'timeout', 'cloudflare', 
                        'just a moment', 'rate limit', 'too many requests',
                        'internal server error', 'bad gateway', 'service unavailable'
                    ]
                    
                    is_network_error = any(error in error_msg for error in network_errors)
                    
                    if attempt < max_retries and is_network_error:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(f"尝试 {attempt + 1}/{max_retries + 1} 失败: {e}")
                        logger.info(f"等待 {delay:.1f} 秒后重试...")
                        time.sleep(delay)
                        continue
                    else:
                        # 非网络错误或已达到最大重试次数
                        break
            
            # 所有重试都失败了
            logger.error(f"所有重试都失败了，最后的错误: {last_exception}")
            raise last_exception
        
        return wrapper
    return decorator

async def async_retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """
    异步版本的重试装饰器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # 检查是否是网络相关错误
                    network_errors = [
                        'connection error', 'timeout', 'cloudflare', 
                        'just a moment', 'rate limit', 'too many requests',
                        'internal server error', 'bad gateway', 'service unavailable'
                    ]
                    
                    is_network_error = any(error in error_msg for error in network_errors)
                    
                    if attempt < max_retries and is_network_error:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(f"异步尝试 {attempt + 1}/{max_retries + 1} 失败: {e}")
                        logger.info(f"等待 {delay:.1f} 秒后重试...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        break
            
            logger.error(f"所有异步重试都失败了，最后的错误: {last_exception}")
            raise last_exception
        
        return wrapper
    return decorator

def check_api_connectivity(api_base: str, api_key: str) -> bool:
    """
    检查API连通性
    
    Args:
        api_base: API基础URL
        api_key: API密钥
        
    Returns:
        bool: 是否可以连接
    """
    try:
        import requests
        
        # 构建测试URL
        test_url = api_base.rstrip('/') + '/models'
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ API连通性测试成功")
            return True
        else:
            logger.warning(f"⚠️ API返回状态码: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API连通性测试失败: {e}")
        return False

def get_optimal_timeout(operation_type: str = "default") -> int:
    """
    根据操作类型获取最优超时时间
    
    Args:
        operation_type: 操作类型
        
    Returns:
        int: 超时时间（秒）
    """
    timeouts = {
        "search": 30,      # 搜索操作
        "analysis": 120,   # 分析操作
        "generation": 180, # 生成操作
        "validation": 60,  # 验证操作
        "default": 60      # 默认超时
    }
    
    return timeouts.get(operation_type, timeouts["default"])

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """如果需要，等待以避免超过速率限制"""
        now = time.time()
        
        # 清除一分钟前的调用记录
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        # 如果调用次数超过限制，等待
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"速率限制：等待 {sleep_time:.1f} 秒...")
                time.sleep(sleep_time)
        
        # 记录这次调用
        self.calls.append(now)

# 全局速率限制器实例
api_rate_limiter = RateLimiter(calls_per_minute=30)  # 保守的速率限制
