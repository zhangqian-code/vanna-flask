import base64
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class CryptUtil:
    STRING_LENGTH = 6

    @staticmethod
    def bs64_encrypt(plain_str):
        """Base64 编码"""
        return base64.b64encode(plain_str.encode()).decode()

    @staticmethod
    def bs64_encrypt_with_head(plain_str):
        """Base64 编码并加入6位随机混淆字符"""
        if not plain_str:
            print("Empty plain text")
            return None
        head_str = ''.join(random.choices(string.ascii_letters + string.digits, k=CryptUtil.STRING_LENGTH))
        return head_str + base64.b64encode(plain_str.encode()).decode()

    @staticmethod
    def bs64_decrypt(base64_str):
        """Base64 解码"""
        decoded_bytes = base64.b64decode(base64_str)
        return decoded_bytes.decode()

    @staticmethod
    def bs64_decrypt_with_head(base64_str):
        """去除混淆后进行 Base64 解码"""
        if not base64_str or len(base64_str) < CryptUtil.STRING_LENGTH:
            return base64_str
        input_str = base64_str[6:]
        decoded_bytes = base64.b64decode(input_str)
        return decoded_bytes.decode()

    @staticmethod
    def aes_encrypt(plain, key, iv):
        """AES 加密 (CBC 模式)"""
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        encrypted = cipher.encrypt(pad(plain.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted).decode()


    DEFAULT_KEY = 'xzkingdee@123-=.'  # 默认密钥
    DEFAULT_IV = '1m@ri31N-=,.!iog'     # 默认初始化向量

    @staticmethod
    def aes_decrypt_1(encrypted):
        """AES 解密 (CBC 模式) 使用默认密钥和IV"""
        cipher = AES.new(CryptUtil.DEFAULT_KEY.encode('utf-8'), AES.MODE_CBC, CryptUtil.DEFAULT_IV.encode('utf-8'))
        decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted)), AES.block_size)
        return decrypted.decode()
    @staticmethod
    def aes_decrypt(encrypted, key, iv):
        """AES 解密 (CBC 模式)"""
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted)), AES.block_size)
        return decrypted.decode()

    @staticmethod
    def sm4_encrypt(plain_data):
        """SM4 对称加密 (此处可扩展为你具体的 SM4 实现)"""
        # 在此实现具体的 SM4 加密逻辑或使用对应的 Python 库
        # 这里只是简单返回原文来表示加密过程
        return plain_data

    @staticmethod
    def sm4_decrypt(secret_data):
        """SM4 对称解密 (此处可扩展为你具体的 SM4 实现)"""
        # 在此实现具体的 SM4 解密逻辑或使用对应的 Python 库
        # 这里只是简单返回原文来表示解密过程
        return secret_data

    @staticmethod
    def sm4_encrypt64(base64_str):
        """对前端传入的 base64 字符串进行 SM4 加密"""
        plain_txt = CryptUtil.bs64_decrypt_with_head(base64_str)
        return CryptUtil.sm4_encrypt(plain_txt)

    @staticmethod
    def sm4_decrypt64(secret_data):
        """对数据库中的密文进行 SM4 解密并返回 base64 编码的字符串"""
        plain_txt = CryptUtil.sm4_decrypt(secret_data)
        return CryptUtil.bs64_encrypt_with_head(plain_txt)


# 测试示例
if __name__ == "__main__":
    # private static final String KEY = "jimureport@123-=";
    # private static final String IV = "-=,.!iog1m@ri31N";
    key = 'xzkingdee@123-=.'  # 32 字节密钥
    iv = '1m@ri31N-=,.!iog'    # 16 字节初始向量 (IV)
    
    # AES 加解密
    encrypted = CryptUtil.aes_encrypt("明文", key, iv)
    print("AES 加密:", encrypted)
    decrypted = CryptUtil.aes_decrypt(encrypted, key, iv)
    print("AES 解密:", decrypted)
    
    # Base64 编码与解码
    base64_encoded = CryptUtil.bs64_encrypt_with_head("xzkingdeejava")
    print("Base64 编码:", base64_encoded)
    base64_decoded = CryptUtil.bs64_decrypt_with_head(base64_encoded)
    print("Base64 解码:", base64_decoded)
