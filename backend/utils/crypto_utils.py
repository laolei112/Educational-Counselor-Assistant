"""
加密和签名验证工具
用于防爬取和请求验证
"""

import hashlib
import time
from typing import Dict, Optional, Tuple
import os


class SignatureValidator:
    """
    签名验证器
    """
    
    def __init__(self, secret_key: str = None, valid_api_keys: list = None):
        """
        初始化签名验证器
        
        Args:
            secret_key: API密钥，用于签名验证
            valid_api_keys: 有效的API Key列表
        """
        self.secret_key = secret_key or os.environ.get('API_SECRET', '6vz1c3AhSq3SvGm-rIBrKYCGNcvbhTf6UlAGTZLs8Pk')
        self.valid_api_keys = valid_api_keys or ['betterschool-client-v1']
        self.nonce_cache = {}  # 用于防重放攻击的nonce缓存
        self.cache_cleanup_interval = 3600  # 每小时清理一次缓存
        self.last_cleanup = time.time()
    
    def _cleanup_nonce_cache(self):
        """清理过期的nonce缓存"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cache_cleanup_interval:
            # 清理5分钟前的nonce
            expired_time = current_time - 300
            self.nonce_cache = {
                k: v for k, v in self.nonce_cache.items() 
                if v > expired_time
            }
            self.last_cleanup = current_time
    
    def _generate_signature(
        self, 
        timestamp: int, 
        nonce: str, 
        api_key: str,
        params: Dict = None,
        body: str = None
    ) -> str:
        """
        生成签名
        
        签名算法：SHA256(timestamp + nonce + apiKey + sortedParams + body + apiSecret)
        """
        # 构建签名字符串
        sign_string = f"{timestamp}{nonce}{api_key}"
        
        # 添加查询参数（排序后）
        if params:
            sorted_params = sorted(params.items())
            param_str = '&'.join([f"{k}={v}" for k, v in sorted_params if v is not None])
            sign_string += param_str
        
        # 添加请求体
        if body:
            sign_string += body
        
        # 添加密钥
        sign_string += self.secret_key
        
        # 生成SHA256签名
        signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()
        return signature
    
    def validate_signature(
        self,
        timestamp: str,
        nonce: str,
        api_key: str,
        signature: str,
        params: Dict = None,
        body: str = None,
        time_window: int = 300  # 时间窗口（秒），默认5分钟
    ) -> Tuple[bool, Optional[str]]:
        """
        验证签名
        
        Returns:
            (is_valid, error_message)
        """
        # 清理过期的nonce缓存
        self._cleanup_nonce_cache()
        
        # 验证必要参数
        if not all([timestamp, nonce, api_key, signature]):
            return False, "缺少必要的签名参数"
        
        # 验证API Key
        if api_key not in self.valid_api_keys:
            return False, "无效的API Key"
        
        # 验证时间戳
        try:
            request_time = int(timestamp)
        except ValueError:
            return False, "无效的时间戳格式"
        
        current_time = int(time.time())
        time_diff = abs(current_time - request_time)
        
        if time_diff > time_window:
            return False, f"请求已过期（时间差: {time_diff}秒）"
        
        # 验证nonce（防重放攻击）
        nonce_key = f"{api_key}:{nonce}:{timestamp}"
        if nonce_key in self.nonce_cache:
            return False, "检测到重放攻击"
        
        # 生成期望的签名
        expected_signature = self._generate_signature(
            request_time, nonce, api_key, params, body
        )
        
        # 对比签名
        if signature != expected_signature:
            return False, "签名验证失败"
        
        # 记录nonce（防重放）
        self.nonce_cache[nonce_key] = current_time
        
        return True, None
    
    def validate_request(
        self,
        headers: Dict[str, str],
        params: Dict = None,
        body: str = None
    ) -> Tuple[bool, Optional[str]]:
        """
        验证HTTP请求
        
        Args:
            headers: HTTP请求头
            params: 查询参数
            body: 请求体
        
        Returns:
            (is_valid, error_message)
        """
        # 从请求头中提取签名信息
        timestamp = headers.get('X-Timestamp') or headers.get('x-timestamp')
        nonce = headers.get('X-Nonce') or headers.get('x-nonce')
        api_key = headers.get('X-Api-Key') or headers.get('x-api-key')
        signature = headers.get('X-Signature') or headers.get('x-signature')
        
        return self.validate_signature(
            timestamp, nonce, api_key, signature, params, body
        )


class RateLimiter:
    """
    频率限制器（简单实现，生产环境建议使用Redis）
    """
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        初始化频率限制器
        
        Args:
            max_requests: 时间窗口内的最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}  # {client_id: [timestamps]}
        self.blocked_clients = {}  # {client_id: block_until_time}
        self.last_cleanup = time.time()
    
    def _cleanup(self):
        """清理过期数据"""
        current_time = time.time()
        if current_time - self.last_cleanup > 300:  # 每5分钟清理一次
            # 清理过期的请求记录
            cutoff_time = current_time - self.time_window
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    ts for ts in self.requests[client_id] 
                    if ts > cutoff_time
                ]
                if not self.requests[client_id]:
                    del self.requests[client_id]
            
            # 清理解封的客户端
            self.blocked_clients = {
                k: v for k, v in self.blocked_clients.items()
                if v > current_time
            }
            
            self.last_cleanup = current_time
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """
        检查是否允许请求
        
        Args:
            client_id: 客户端标识（IP、设备ID等）
        
        Returns:
            (is_allowed, error_message)
        """
        self._cleanup()
        
        current_time = time.time()
        
        # 检查是否被封禁
        if client_id in self.blocked_clients:
            block_until = self.blocked_clients[client_id]
            if current_time < block_until:
                remaining = int(block_until - current_time)
                return False, f"请求过于频繁，请在{remaining}秒后重试"
            else:
                del self.blocked_clients[client_id]
        
        # 获取客户端的请求记录
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # 清理时间窗口外的记录
        cutoff_time = current_time - self.time_window
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] 
            if ts > cutoff_time
        ]
        
        # 检查请求频率
        request_count = len(self.requests[client_id])
        if request_count >= self.max_requests:
            # 封禁客户端（封禁时间为时间窗口的2倍）
            self.blocked_clients[client_id] = current_time + (self.time_window * 2)
            return False, "请求过于频繁，已被暂时限制访问"
        
        # 记录请求
        self.requests[client_id].append(current_time)
        
        return True, None
    
    def get_remaining_requests(self, client_id: str) -> int:
        """获取剩余请求次数"""
        if client_id not in self.requests:
            return self.max_requests
        
        current_time = time.time()
        cutoff_time = current_time - self.time_window
        valid_requests = [
            ts for ts in self.requests[client_id] 
            if ts > cutoff_time
        ]
        
        return max(0, self.max_requests - len(valid_requests))


# 全局实例
signature_validator = SignatureValidator()
rate_limiter = RateLimiter(max_requests=100, time_window=60)

