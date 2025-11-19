import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from django.conf import settings

class DataEncryptor:
    """
    数据加密工具类 (AES-CBC模式)
    """
    # 默认密钥（实际生产环境应从环境变量获取）
    # 前端使用了 padEnd(32, '\0')，这里必须保持一致
    DEFAULT_KEY = b'Educational_Counselor_Secret_K'.ljust(32, b'\0')[:32]  # 32 bytes for AES-256
    BLOCK_SIZE = 16

    @classmethod
    def get_key(cls):
        secret = getattr(settings, 'API_ENCRYPTION_KEY', None)
        if secret:
            # 确保密钥长度正确
            if isinstance(secret, str):
                secret = secret.encode()
            return secret.ljust(32, b'\0')[:32]
        return cls.DEFAULT_KEY

    @classmethod
    def encrypt_data(cls, data):
        """
        加密数据
        :param data: 字典或列表等可JSON序列化的数据
        :return: { "iv": "base64...", "payload": "base64..." }
        """
        try:
            # 1. 序列化数据
            json_data = json.dumps(data).encode('utf-8')
            
            # 2. 生成IV
            iv = get_random_bytes(cls.BLOCK_SIZE)
            
            # 3. 加密
            cipher = AES.new(cls.get_key(), AES.MODE_CBC, iv)
            encrypted_bytes = cipher.encrypt(pad(json_data, cls.BLOCK_SIZE))
            
            # 4. Base64编码
            return {
                "encrypted": True,
                "iv": base64.b64encode(iv).decode('utf-8'),
                "payload": base64.b64encode(encrypted_bytes).decode('utf-8')
            }
        except Exception as e:
            # 生产环境应记录日志
            print(f"Encryption error: {e}")
            return data

    @classmethod
    def decrypt_data(cls, encrypted_payload, iv_str):
        """
        解密数据
        """
        try:
            iv = base64.b64decode(iv_str)
            encrypted_bytes = base64.b64decode(encrypted_payload)
            
            cipher = AES.new(cls.get_key(), AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), cls.BLOCK_SIZE)
            
            return json.loads(decrypted_bytes.decode('utf-8'))
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

