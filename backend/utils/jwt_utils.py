"""
JWT Token工具类
用于生成和验证访问Token
"""

import jwt
import os
import time
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional


# JWT配置
JWT_SECRET = os.environ.get('JWT_SECRET', '6vz1c3AhSq3SvGm-rIBrKYCGNcvbhTf6UlAGTZLs8Pk')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24  # Token有效期24小时


def generate_token(client_id: str, metadata: Dict = None) -> str:
    """
    生成JWT Token
    
    Args:
        client_id: 客户端唯一标识（设备ID或IP）
        metadata: 额外的元数据
    
    Returns:
        JWT token字符串
    """
    now = datetime.utcnow()
    payload = {
        'client_id': client_id,
        'iat': now,  # 签发时间
        'exp': now + timedelta(hours=TOKEN_EXPIRE_HOURS),  # 过期时间
        'metadata': metadata or {}
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # 确保token是字符串类型（某些PyJWT版本返回bytes）
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token


def verify_token(token: str) -> Tuple[bool, any]:
    """
    验证JWT Token
    
    Args:
        token: JWT token字符串
    
    Returns:
        (is_valid, payload_or_error_message)
        - 成功: (True, payload字典)
        - 失败: (False, 错误消息字符串)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, 'Token已过期'
    except jwt.InvalidTokenError as e:
        return False, f'Token无效: {str(e)}'
    except Exception as e:
        return False, f'Token验证失败: {str(e)}'


def decode_token_without_verify(token: str) -> Optional[Dict]:
    """
    解码Token（不验证签名）
    用于调试或获取过期Token的信息
    
    Args:
        token: JWT token字符串
    
    Returns:
        payload字典或None
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception:
        return None


class TokenManager:
    """
    Token管理器
    提供Token黑名单、撤销等高级功能
    """
    
    def __init__(self):
        self.blacklist = set()  # Token黑名单（生产环境建议使用Redis）
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 每小时清理一次
    
    def revoke_token(self, token: str):
        """
        撤销Token
        
        Args:
            token: 要撤销的Token
        """
        self.blacklist.add(token)
    
    def is_revoked(self, token: str) -> bool:
        """
        检查Token是否被撤销
        
        Args:
            token: 要检查的Token
        
        Returns:
            bool: True表示已被撤销
        """
        return token in self.blacklist
    
    def cleanup_expired(self):
        """
        清理过期的黑名单Token
        """
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            # 遍历黑名单，移除已过期的Token
            expired_tokens = set()
            for token in self.blacklist:
                payload = decode_token_without_verify(token)
                if payload and 'exp' in payload:
                    # 如果Token已过期，标记为删除
                    if payload['exp'] < current_time:
                        expired_tokens.add(token)
            
            # 从黑名单中移除过期Token
            self.blacklist -= expired_tokens
            self.last_cleanup = current_time
    
    def get_blacklist_size(self) -> int:
        """获取黑名单大小"""
        return len(self.blacklist)


# 全局Token管理器实例
token_manager = TokenManager()

