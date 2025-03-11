# ##############################################################################################
# # ++导入所需的库和模块
import os
import sys
import cryptography
import hashlib
import json
import base64
import secrets
import logging
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
MIIEowIBAAKCAQEAwuxCNMPlIHxyMiKieHemAgsQNMQjXM9n2i1zN8nWftrmiUAp
92QlfJPa17dMZZ64pzTYDMlRGW0fdiXTjkynKPrpW4EDhDcA/6ktdOaGBd7tine5
WlmJKP979dQ1TapPChWvj3oPDsO/SvskiDaN9Dp3SxyrpvJEvlrVAYQHcSJ4vqXg
BEqeGKSBQUkg3WemuAPXAdGXc+Vxoia+mVbEA9LOBamOiDcbnKUI8ymtrs26Ukyg
6Fqu4+RhS5GDoK77wsK5wdb7X/aXz6m3bwFm0edzIcRSHDPgd+qHWO69pqQAxTEk
+aUoSuAkatqCfyNOEDNtBfw0IxSszEYul+dKlwIDAQABAoIBABVioqWJA9I2GmNE
vdWArwO/X1D4CeHXVs9ZjYVb4r66g8YgINqQWrUvFY31gW9kDrc4NXyQTmep5g8/
eX/oX1iVeqpm3lIQT3mSf+G49Dr1qShiwpZWh2qqPlk1+ykhBm3r+32+yE3NjRG2
ubHWERSaoNbqoix9R6x+E6uIZuFIU/f35ko7IKf+E5v9z9bsHEjkXPmw/fMXNnlu
DXmsYHch6XSDYh4qb0ShgVBhciSDNMQ6wwJVnpqYHkn2v0sBUq6A1V1dxjAinQ53
KA10OkMix32Qi4yEn0Lm7tcTXv2dk4ovcPdoPcVSJDk/X4GPNukiqlQZkUyfw/Ct
HgsqdmkCgYEA7WD2KGFYpZrqY/9sq06Gp5WC1jSZoxSYqh3tzNZ89Chs20O+83pl
EfJMGlzVXJHUqhyBU2mQHQyz89B0gJ0qQpWqNl/DZ968PO0Jwhl7Qbk1C++gecaB
Z1X33GDXQumtdi52/L0v/B3cqFA7pdJcWbfCcpsQxRbKLdekkRP3oykCgYEA0jay
1dqXbumLxZXiR9P9Bwz51innQjS8OuF+GNWpOZ/2H9E21F55U4w16UrNu3JQybvj
7qwHGtyRwX93tdCcucyqzz+eWPT6cE3mCeEze2rw6eL2AzMvR5Uk7q0T+2BjyYoe
N6JqLSien1sn1w7LJqE+RGrdMJRfsigPO5T4978CgYEA2EqIIKUKg+LS/YioOLMV
aK+Hhqxo7TqAHEmm+wTY2BPZlDR3UhzM6PxQsZiy5GUQVGwivqEqKf4AHgFrliEe
d4sti9vYDdXayNznDk/viiQ6nIScQTlJgaHIdapbmeGYJ14RFxs/FMcU3tw0bVRu
x2TzrT9zmVG5qOmbToHWG3kCgYAwpVPRRVqR4h3kRYEt2hLN1OTj+KJ5obaFcbU6
jgcxPKE6T7H+hzZQbTv0lsjxPc0QQhjHHKwwPSbFvne3bWU3YfONLk24jEiAQKah
VqoRP3gsx8biiq/AQvVe/lKHc5DkDMBdY4pqlOHQQsn/bH76m4nLT2eMXGmg0sBj
q1/KBQKBgAt9QnIVdpEd6evqZGwQfQX2l9caWNSVnzG/9F1v8fVa7dZcsQF78AGL
tYaKlvlfB+zqKZwrN3nitfHVheh0ZjhJruV2O7Ou+/rURwINqa9rfmx7IGhUPcRz
r6F8Wc6LfJn8JkqVjz+M7PkXikbgLoP31Q9Nxs/fSGqsa42VLt/w
-----END RSA PRIVATE KEY-----"""

public_key ="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwuxCNMPlIHxyMiKieHem
AgsQNMQjXM9n2i1zN8nWftrmiUAp92QlfJPa17dMZZ64pzTYDMlRGW0fdiXTjkyn
KPrpW4EDhDcA/6ktdOaGBd7tine5WlmJKP979dQ1TapPChWvj3oPDsO/SvskiDaN
9Dp3SxyrpvJEvlrVAYQHcSJ4vqXgBEqeGKSBQUkg3WemuAPXAdGXc+Vxoia+mVbE
A9LOBamOiDcbnKUI8ymtrs26Ukyg6Fqu4+RhS5GDoK77wsK5wdb7X/aXz6m3bwFm
0edzIcRSHDPgd+qHWO69pqQAxTEk+aUoSuAkatqCfyNOEDNtBfw0IxSszEYul+dK
lwIDAQAB
-----END PUBLIC KEY-----"""

public_password = "ea54b522ed180be0691d084cde28c930".encode()
##############################################################################################






# 生成公钥和私钥
#------------------------------------------------------------------------
# 生成密钥对
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

# 保存模块
def save_key_to_file(key_data, file_name):
    """
    将密钥保存到文件中。

    Args:
        key_data (bytes): 要保存的密钥数据（PEM格式）。
        file_name (str): 要保存的文件名。
    """
    with open(file_name, "wb") as key_file:
        key_file.write(key_data)

# 生成并保存到指定地方
def create_and_save_keys(private_key_path = None, public_key_path = None):
    """
    生成一对RSA密钥对，并将它们保存到指定的路径中。

    Args:
        private_key_path (str): 私钥保存的路径和文件名，默认为 'private_key.pem'。
        public_key_path (str): 公钥保存的路径和文件名，默认为 'public_key.pem'。
    """
    private_key_pem, public_key_pem = generate_key_pair()
    save_key_to_file(private_key_pem, private_key_path)
    save_key_to_file(public_key_pem, public_key_path)
    logging.info(f"密钥已生成并保存到文件：{private_key_path} 和 {public_key_path}")

# 生成对称密钥
def generate_passworld(length = 32):
    return secrets.token_hex(length)
#------------------------------------------------------------------------


# 生成加密密钥
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

    signature = private_key.sign(
        encrypted_license,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    license_package = {
        "license": base64.b64encode(encrypted_license).decode(),
        "iv": base64.b64encode(iv).decode(),
        "signature": base64.b64encode(signature).decode(),
        "salt": base64.b64encode(salt).decode() if salt else None  # 将盐值编码为Base64
    }

    return base64.b64encode(json.dumps(license_package).encode()).decode()


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


    # print(generate_passworld())
    # create_and_save_keys(os.path.join(Script_path, 'private_key.pem'), os.path.join(Script_path, 'public_key.pem'))
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

