# ##############################################################################################
# # ++导入所需的库和模块
import os
import sys
import cryptography
import hashlib
import json
import base64
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

Script_path = os.path.join(os.path.dirname(__file__))

private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA1/6Xdm/snMpNWzdWxHVaTpz7qzB2tSkDfX195IDn+xMRMkMA
rpxasskvJ/53SqUkrkh+0oHX42HKZ5IE+QMgEKVboiGNEoTtiyQUdCDngqvAvUXK
+Yn1LWKnoAjfwZedAPDw6ctz1pDaXqTn3uM1ZleHANi5wyQ6BEo/2E2PqTMlqidW
8EcYKpyrINeXBPNXTQhKUxRKGNr4uFED/HCIW1yYchf66HvmXIZ89vaC0vvhUWuU
AEE9Jrz7EMKuwcVQrR3fAwwaCo0xgVzpEH1TctSoqGFRg+ZV20lLkVXMsGbhKLl5
VkdCMt+dmurKwQBSV7yCzYDZ/y8ebMRmsFtTlwIDAQABAoIBAES62ItxdgM2RINA
CrYc+Y2GWnbQxxVCZb/qzMKHWkoEeTZbJ75oNlwptH2vdVolTpS+sMxfUMkj9voZ
9scd/XgOhigDMRaxgb0C0Bdb2Q81g/E2Yi4hfgjhGaHM8RZzHhyMjrx2Zvfhw/rV
0oqUFgvo0iasz/+OaX+v+LzlgU8/R35eC8463xdkN9kWHnGE8hEj50ZxZLN5ukKL
x+QK7d9oHc/5fcp8A9rPF8PL5XT7KNz4vtJJu9soFa01xaH9X5IMYnSi3UcB5KSu
HIHMgokY5o0bdOFA7cGsYaSoquMexWhnnBIi7PLmi4mFnTQwx76S0gaZRisVuV3H
L/QeV5ECgYEA8+/d7L9mJy9hLfFC4dME3TjgZXvhMQcSjEWimJfwUzd1pZ3nYwlB
6IRC+nkLPKGpQwes4W+l3UGsIh262enjAT0AyZzxZmkyVhy6uZahgElmbd2kLIrg
DBq2EStBwVeSgNqeVcjism4LL6N5fCExMmmselhwGXrZ9zwLwrtQmc0CgYEA4qz8
RXubBs33thSfo5iQnvqSyWM75d5d0tl6gxACL13R0bUj+gFUxfSC0kYXvxL+bsEk
9Skp/kqDkStCuHChy0JNAJEHZ7fauewTYOZKc1EpfUcXw8OaP5ri+vHMQsmGnVnB
a9wqtGCkCGuOyOTS7lfyapjrYAAAJlZNkvOQrvMCgYAv2+3UlzC5m2gblWwj1jzs
Ek6kWouyDMsszjS6b4TtLsJcPgC5w4U00044yirUOHt29TiL+lW2dT4Ka37PZj3t
bkSLSclq6FTB5F0WMGF7Q+tevs+JFa4jcdIqyCvcfQv3T+0ks4cWrtRvAknBetmm
JGl8j4Fe3mWJRjSgfhOwOQKBgQCknY/PPgbFmEqutqeAfUl5yutSyXg0ZZqphzrL
d5K+p1m6+9uWseTIpdtjrXeNUdPoxud6C1ztyVtmz43yuAknvYyCPtCr5/82SlWA
Z33l5SlGS5zclG6uhmMUbwkx73yNRSOMmyWAPTaizsmw50yvvrrT4x38Z8O0E7Te
ZXfLNQKBgEt5sqpwkaH0AjpAS9tlPOatiu7IWlY6Q+hLqiKFSoCiwpESX+mln8og
hqXEXJu+MU9M0TvdzERfl64+h3XJdY5VPGDGRGNWBg028aEhVxNzskuMVO3gnNlg
GbawbOwb4P760oPmy6yD+jSJqqcF1M++WwC5Mvzu8D5Qoljf9iPT
-----END RSA PRIVATE KEY-----"""

public_key ="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1/6Xdm/snMpNWzdWxHVa
Tpz7qzB2tSkDfX195IDn+xMRMkMArpxasskvJ/53SqUkrkh+0oHX42HKZ5IE+QMg
EKVboiGNEoTtiyQUdCDngqvAvUXK+Yn1LWKnoAjfwZedAPDw6ctz1pDaXqTn3uM1
ZleHANi5wyQ6BEo/2E2PqTMlqidW8EcYKpyrINeXBPNXTQhKUxRKGNr4uFED/HCI
W1yYchf66HvmXIZ89vaC0vvhUWuUAEE9Jrz7EMKuwcVQrR3fAwwaCo0xgVzpEH1T
ctSoqGFRg+ZV20lLkVXMsGbhKLl5VkdCMt+dmurKwQBSV7yCzYDZ/y8ebMRmsFtT
lwIDAQAB
-----END PUBLIC KEY-----"""

public_password = "ea54b522ed180be0691d084cde28c930".encode()
##############################################################################################






#   生成公钥和私钥
#------------------------------------------------------------------------
#   生成密钥
def generate_key_pair(key_size=2048):
    """
    生成一对RSA公私钥，并将其保存为PEM格式文件。

    Args:
        key_size (int): RSA密钥的大小，默认为2048位。

    Returns:
        private_key_pem (bytes): 生成的私钥内容（PEM格式）。
        public_key_pem (bytes): 生成的公钥内容（PEM格式）。
    """
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # 从私钥中提取公钥
    public_key = private_key.public_key()

    # 将私钥保存为PEM格式
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()  # 如果想加密私钥，可以修改这里
    )

    # 将公钥保存为PEM格式
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem, public_key_pem

#   保存模块
def save_key_to_file(key_data, file_name):
    """
    将密钥保存到文件中。

    Args:
        key_data (bytes): 要保存的密钥数据（PEM格式）。
        file_name (str): 要保存的文件名。
    """
    with open(file_name, "wb") as key_file:
        key_file.write(key_data)

#   生成并保存到指定地方
def create_and_save_keys(private_key_path = None, public_key_path = None):
    """
    生成一对RSA密钥对，并将它们保存到指定的路径中。

    Args:
        private_key_path (str): 私钥保存的路径和文件名，默认为 'private_key.pem'。
        public_key_path (str): 公钥保存的路径和文件名，默认为 'public_key.pem'。
    """
    private_key_pem, public_key_pem = generate_key_pair()

    # 保存私钥和公钥到指定路径
    save_key_to_file(private_key_pem, private_key_path)
    save_key_to_file(public_key_pem, public_key_path)

    feedback.CP(f"密钥已生成并保存到文件：{private_key_path} 和 {public_key_path}")

#------------------------------------------------------------------------


#   生成对称密钥
def generate_passworld(length = 32):
    return secrets.token_hex(length)













#   生成加密密钥
def generate_encryption_key(length=32, password=None, salt=None):
    """
    生成加密密钥。

    Args:
        length (int): 密钥长度，默认为32字节（即256位AES密钥）。
        password (bytes): 可选的密码，如果提供，将使用PBKDF2从密码派生密钥。
        salt (bytes): 可选的盐值，如果提供，将使用此盐值进行派生，否则生成新盐值。

    Returns:
        tuple: (encryption_key, salt)
    """
    if password is None:
        # 完全随机生成密钥
        encryption_key = os.urandom(16)
        return encryption_key, None
    else:
        if salt is None:
            salt = os.urandom(16)  # 生成一个随机的盐值
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        encryption_key = kdf.derive(password)
        return encryption_key, salt

def generate_license(private_key_pem, device_fingerprint, days_valid = None, password=None, license_type='standard_license'):
    """
    使用私钥生成序列号（许可证），并加密许可证信息。

    Args:
        private_key_pem (str): 私钥（PEM格式）。
        device_fingerprint (str): 设备标识符（例如主板ID的哈希）。
        days_valid (int): 许可证的有效期（天数）。
        password (bytes): 用户提供的密码，如果提供，将使用PBKDF2从密码派生密钥。
        license_type (str): 许可证类型，可以是 "standard", "developer", "permanent"。

    Returns:
        str: 生成的序列号（Base64编码）。
    """


    # free_license（免费版）
    # standard_license（标准版）
    # premium_license（高级版）
    # developer_license（开发者许可证）
    # educational_license（教育许可证）
    # permanent_standard_license（标准版）
    # permanent_premium_license（高级版）
    # 加载私钥
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
    )

    # 当前时间（UTC）
    current_time = datetime.utcnow()

    # 如果license_type是 'developer_license', 'permanent_standard_license', 或 'permanent_premium_license'
    # 则这些类型的许可证为永久有效，因此将expiry_date设为None表示没有到期日
    if license_type in ['free_license', 'developer_license', 'permanent_standard_license', 'permanent_premium_license']:
        expiry_date = None # 永久许可证没有过期日期
    else:
        # 对于其他类型的许可证，expiry_date为当前时间加上有效期天数(days_valid)
        expiry_date = current_time + timedelta(days=days_valid)

    # 定义许可证信息
    license_data = {
        "device_fingerprint": device_fingerprint,
        "issue_date": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "expiry_date": expiry_date.strftime('%Y-%m-%d %H:%M:%S') if expiry_date else None,
        "license_type" : license_type
    }

    # 将许可证信息转换为JSON字符串
    license_json = json.dumps(license_data).encode()

    # 根据是否有密码来生成加密密钥
    encryption_key, salt = generate_encryption_key(password=password)

    # 使用对称密钥（AES）加密许可证信息
    iv = os.urandom(16)  # 生成一个随机的初始化向量
    cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_license = encryptor.update(license_json) + encryptor.finalize()

    # 使用私钥对加密后的许可证信息进行签名
    signature = private_key.sign(
        encrypted_license,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 将加密的许可证信息、签名、初始化向量和盐组合起来
    license_package = {
        "license": base64.b64encode(encrypted_license).decode(),
        "iv": base64.b64encode(iv).decode(),
        "signature": base64.b64encode(signature).decode(),
        "salt": base64.b64encode(salt).decode() if salt else None  # 将盐值编码为Base64
    }

    # 序列号为最终的许可证包，编码为Base64格式
    return base64.b64encode(json.dumps(license_package).encode()).decode()

from datetime import datetime

def get_license_remaining_time(license_package_b64, password=None):
    """
    查询许可证的剩余时间。

    Args:
        license_package_b64 (str): Base64编码的许可证包。
        password (bytes): 用户提供的密码，如果提供，将使用PBKDF2从密码派生密钥。

    Returns:
        int: 许可证剩余的天数，如果许可证已经过期则返回0。
    """
    # 解码Base64编码的许可证包
    license_package_json = base64.b64decode(license_package_b64).decode()
    license_package = json.loads(license_package_json)

    # 获取加密的许可证信息、初始化向量、签名和盐值
    encrypted_license = base64.b64decode(license_package["license"])
    iv = base64.b64decode(license_package["iv"])
    signature = base64.b64decode(license_package["signature"])
    salt = base64.b64decode(license_package["salt"]) if license_package.get("salt") else None

    # 根据密码和盐值生成解密密钥
    encryption_key, _ = generate_encryption_key(password=password, salt=salt)

    # 使用对称密钥（AES）解密许可证信息
    cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    license_json = decryptor.update(encrypted_license) + decryptor.finalize()

    # 解析许可证信息
    license_data = json.loads(license_json.decode())

    # 获取当前日期和许可证到期日期
    current_date = datetime.utcnow()
    expiry_date = datetime.strptime(license_data["expiry_date"], '%Y-%m-%d %H:%M:%S')

    # 计算剩余天数
    remaining_time = (expiry_date - current_date).days

    # 如果剩余时间为负值，说明许可证已经过期，返回0
    return max(remaining_time, 0) , expiry_date



if __name__ == '__main__':
    device_fingerprint = str(input("输入device_fingerprint设别标识符"))

    license_types = {
        1: 'free_license',  # 免费版
        2: 'standard_license',  # 标准版
        3: 'premium_license',  # 高级版
        4: 'developer_license',  # 开发者许可证
        5: 'educational_license',  # 教育许可证
        6: 'permanent_standard_license',  # 永久标准版
        7: 'permanent_premium_license'  # 永久高级版
    }

    for key, value in license_types.items():
        print(f"{key}: {value}")

    license_type = int(input('请输入许可证类型'))

    if license_type not in license_types:
        quit()

    if license_type in [1,4,6,7]:
        print(generate_license(private_key, device_fingerprint, password=public_password, license_type=license_types[license_type]))
    else:
        day = int(input("输入许可天数设别标识符"))
        print(generate_license(private_key, device_fingerprint, day, password = public_password, license_type=license_types[license_type]))

