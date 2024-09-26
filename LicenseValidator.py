# ##############################################################################################
# # ++导入所需的库和模块
import os
import sys
import cryptography
import hashlib
import json
import base64
import importlib
import ntplib
import requests
import time
import maya.OpenMayaUI as omui
import maya.cmds as cmds
#   自己的库
import Arnold_Magic_Node_lib


#   重新加载模块
importlib.reload(Arnold_Magic_Node_lib)

from time import ctime
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature

# 导入PySide
try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Signal, Slot
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Signal, Slot
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance




Script_path = os.path.join(os.path.dirname(__file__))

dataM = Arnold_Magic_Node_lib.DataManager() # 导入储存模块
feedback = Arnold_Magic_Node_lib.FeedbackPrompt() # 导入报错模块

cached_device_fingerprint = None  # 全局变量，用于缓存主板ID

public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1/6Xdm/snMpNWzdWxHVa
Tpz7qzB2tSkDfX195IDn+xMRMkMArpxasskvJ/53SqUkrkh+0oHX42HKZ5IE+QMg
EKVboiGNEoTtiyQUdCDngqvAvUXK+Yn1LWKnoAjfwZedAPDw6ctz1pDaXqTn3uM1
ZleHANi5wyQ6BEo/2E2PqTMlqidW8EcYKpyrINeXBPNXTQhKUxRKGNr4uFED/HCI
W1yYchf66HvmXIZ89vaC0vvhUWuUAEE9Jrz7EMKuwcVQrR3fAwwaCo0xgVzpEH1T
ctSoqGFRg+ZV20lLkVXMsGbhKLl5VkdCMt+dmurKwQBSV7yCzYDZ/y8ebMRmsFtT
lwIDAQAB
-----END PUBLIC KEY-----"""

public_password = "ea54b522ed180be0691d084cde28c930".encode()


# 获取语言
# 获取语言设置
language_config = dataM.ascii_load_data(os.path.join(Script_path, 'Datas', 'settings', 'language_config.json' ))['language_config']
# 加载语言文件
language = dataM.ascii_load_data(os.path.join(Script_path, 'Datas', 'languages', f'{language_config}.json' ))["LicenseV"]

##############################################################################################


#   获取主板的ID
def get_motherboard_id():
    command = "wmic baseboard get serialnumber"
    output = os.popen(command).read().strip()

    # 过滤掉空行
    lines = [line.strip() for line in output.split("\n") if line.strip()]
    if len(lines) > 1:
        serial_number = lines[1]
        return serial_number
    else:
        feedback.CP(language["GMI"]["01"])
        return None

#   Hardware Identifier 设别标识符
def generate_device_fingerprint(motherboard_id):
    """
    根据主板ID生成设备指纹。

    Args:
        motherboard_id (str): 设备的主板ID。

    Returns:
        str: 设备指纹（SHA-256哈希值）。
    """
    # 使用SHA256对主板ID进行哈希处理，生成设备指纹

    sha256_hash = hashlib.sha256()
    sha256_hash.update(motherboard_id.encode('utf-8'))
    device_fingerprint = sha256_hash.hexdigest()
    return device_fingerprint





#------------------------------------------获取时间戳
# 获取淘宝时间戳
def get_web_timestamp(link = "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"):
    # "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"
    # "http://worldtimeapi.org/api/ip"
    # "https://timeapi.io/api/Time/current/zone?timeZone=UTC"
    try:
        response = requests.get(link)
        if response.status_code == 200:
            data = response.json()
            timestamp = data['data']['t']  # 获取时间戳字符串
            timestamp_float = float(timestamp) / 1000  # 转换为浮点类型 并把毫秒转为秒
            return timestamp_float
        else:
            print("无法获取淘宝时间戳")
            return False
    except Exception as e:
        print("获取link时间失败:" + e)
        return False

# 从阿里云 NTP 服务器获取时间戳
def get_ntp_timestamp(ntp_servers = None):

    inside_ntp_servers = [
        "ntp.tencent.com",  # 腾讯云
        "ntp.aliyun.com",  # 阿里云
        "ntp.cnnic.cn",  # 中国国家互联网应急中心（CNCERT/CC）
    ]
    if ntp_servers == None:
        ntp_servers = inside_ntp_servers
    try:
        for server in ntp_servers:
            try:
                client = ntplib.NTPClient()
                response = client.request(server)
                return response.tx_time
            except:
                pass
    except Exception as e:
        print("获取 NTP 时间失败:" + str(e))
        return False

# 获取本地的时间戳
def get_local_timestamp():
    """
    获取当前本地时间的 Unix 时间戳
    """
    current_timestamp = datetime.now()
    return current_timestamp.timestamp()

#------------------------------------------获取时间戳





#   生成加密密钥
def generate_encryption_key(password, salt = None, iterations=100000, length=32):
    """
    生成加密密钥。

    Args:
        password (bytes): 用户提供的密码。
        salt (bytes): 随机生成的盐值，如果为None，将自动生成一个。
        iterations (int): PBKDF2 的迭代次数。
        length (int): 密钥的长度，默认为32字节（256位）。

    Returns:
        tuple: (bytes, bytes) 派生的加密密钥和使用的盐。
    """
    if salt is None:
        salt = os.urandom(16)  # 生成一个随机的盐值
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,  # 调整此值来优化性能
        backend=default_backend()
    )
    encryption_key = kdf.derive(password)
    return encryption_key, salt



#   检查给定的字符串是否是有效的 JSON 格式
def is_valid_json(data):
    """
    检查给定的字符串是否是有效的 JSON 格式。

    Args:
        data (str): 待检查的字符串。

    Returns:
        bool: 如果是有效的 JSON 格式，返回 True，否则返回 False。
    """
    try:
        json.loads(data)
        return True
    except ValueError:
        return False

#   验证许可证并解密
def verify_license(public_key_pem, license_b64, current_device_fingerprint, current_timestamp, password=None):
    """
    验证许可证并解密。

    Args:
        public_key_pem (str): 公钥（PEM格式），用于验证许可证签名。
        license_b64 (str): Base64编码的许可证包。
        password (bytes): 用户提供的密码，用于派生对称加密密钥（如果使用了密码派生）。
        current_device_fingerprint (str): 当前设备的标识符，用于与许可证中的设备指纹进行匹配。

    Returns:
        bool: 如果许可证有效，返回True；否则返回False。
    """

    # 加载语言文件
    LT = language['VL']


    try:

        # 加载公钥：将传入的PEM格式公钥解码为公钥对象
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        # 解码Base64序列号：将Base64编码的许可证包解码为JSON格式的字典
        decoded_license = base64.b64decode(license_b64).decode()
        if not is_valid_json(decoded_license):
            raise ValueError(LT['01'])

        license_package = json.loads(decoded_license)

        # 提取加密的许可证信息、IV（初始化向量）、签名和盐值
        encrypted_license = base64.b64decode(license_package["license"])
        iv = base64.b64decode(license_package["iv"])
        signature = base64.b64decode(license_package["signature"])
        salt = base64.b64decode(license_package["salt"]) if license_package.get("salt") else None

        # 根据是否有密码来生成对称加密密钥（encryption_key）
        # 使用密码和盐通过PBKDF2派生密钥，或者直接生成随机密钥（如果没有密码）
        encryption_key, _ = generate_encryption_key(password=password, salt=salt, iterations=100000)

        # 使用公钥验证签名：确保加密的许可证信息没有被篡改
        public_key.verify(
            signature,  # 许可证包中的签名
            encrypted_license,  # 签名的内容是加密的许可证信息
            padding.PSS(  # 使用PSS填充方案和SHA256哈希函数
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # 解密许可证信息：使用生成的对称加密密钥和初始化向量解密许可证信息
        cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_license = decryptor.update(encrypted_license) + decryptor.finalize()

        # 将解密后的许可证信息转换为字典
        license_data = json.loads(decrypted_license.decode())

        # 检查设备标识符是否匹配：如果提供了当前设备的标识符，确保它与许可证中的设备指纹匹配
        if current_device_fingerprint and license_data["device_fingerprint"] != current_device_fingerprint:
            feedback.CP(LT['02'])
            return False

        # 检查许可证是否过期：如果到期日期为 None 或 "permanent"，则认为许可证永不过期
        expiry_date = license_data.get("expiry_date")

        # 将 current_timestamp 从时间戳转为datatime类型
        current_time = datetime.fromtimestamp(current_timestamp)
        # 将 expiry_date 从字符串转为datatime类型
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')


        # 如果 expiry_date 不为 None 且不等于 "permanent"，则需要进行过期检查
        if expiry_date is not None and expiry_date != "permanent":
            # 确保 expiry_date 已被转换为 datetime 对象，以便进行时间比较
            if current_time > expiry_date:
                # 如果当前时间大于到期时间，则许可证已过期
                feedback.CP(LT['03'])
                return False


        # 如果所有检查通过，返回True，表示许可证有效 并返回许可时间
        return True , expiry_date


    except InvalidSignature:
        feedback.CPW(LT['04'])
        return False
    except ValueError:
        feedback.CPW(LT['05'])
        return False
    except Exception as e:
        feedback.CPE(LT['06'])
        return False

#   获取许可证剩余时间
def get_license_remaining_time(license_package_b64, password=public_password):
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












#-------------------------------------------------------验证窗口

#   获取Maya主窗口
def MayaMainWindows():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr),QtWidgets.QWidget)



class LicenseWin(QtWidgets.QDialog):
    WINDOWS_NAME = "ArnoldMagic_Node_Tool_Node  License_Window"
    def __init__(self, parent = MayaMainWindows()):
        super(LicenseWin, self).__init__(parent)

        # 加载语言文件
        self.LT= language['LW']

        #   判断窗口是否存在，如果存在则删除
        if cmds.window(LicenseWin.WINDOWS_NAME, exists=True):
            cmds.deleteUI(LicenseWin.WINDOWS_NAME)

        #...窗口名字
        self.setObjectName(LicenseWin.WINDOWS_NAME)
        self.setWindowTitle(LicenseWin.WINDOWS_NAME)

        #...窗口长宽
        self.setFixedSize(700, 500)

        # 关闭高DPI缩放
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)

        self.create_widgets()
        self.create_layouts()


    def create_widgets(self):
        # 创建 QFont 对象，设置字体大小和加粗
        label_font = QtGui.QFont()
        label_font.setFamily("Microsoft YaHei")
        label_font.setPointSize(9)  # 设置字体大小为24
        label_font.setBold(True)  # 设置字体为粗体




        # 设备识别码标签和文本框
        self.device_id_label = QtWidgets.QLabel(self.LT["DIL"]) # "设备识别码（需要提供给开发者）"
        self.device_id_label.setAlignment(QtCore.Qt.AlignCenter)
        self.device_id_label.setFont(label_font)  # 应用字体到 QLabel


        self.device_id_text = QtWidgets.QLineEdit(cached_device_fingerprint)
        self.device_id_text.setReadOnly(True)
        self.device_id_text.setFixedHeight(45)
        self.device_id_text.setFixedWidth(680)

        # 序列号标签和文本框
        self.serial_number_label = QtWidgets.QLabel(self.LT["SUL"]) # "输入序列号"
        self.serial_number_label.setAlignment(QtCore.Qt.AlignCenter)
        self.serial_number_label.setFont(label_font)  # 应用字体到 QLabel


        self.serial_number_text = QtWidgets.QTextEdit()
        self.serial_number_text.setPlaceholderText(self.LT["SNT"]) # "请输入序列号"
        self.serial_number_text.setFixedHeight(300)
        self.serial_number_text.setFixedWidth(680)

        # 验证按钮
        self.verify_button = QtWidgets.QPushButton(self.LT["VB"]) # "验证许可"
        self.verify_button.clicked.connect(self.verify_license)

    def create_layouts(self):
        layout = QtWidgets.QVBoxLayout()

        # 每一行只放置一个控件
        layout.addWidget(self.device_id_label)
        layout.addWidget(self.device_id_text)
        layout.addWidget(self.serial_number_label)
        layout.addWidget(self.serial_number_text)
        layout.addWidget(self.verify_button)

        self.setLayout(layout)

    def verify_license(self):
        license = self.serial_number_text.toPlainText()

        if license == '' :
            feedback.CPW(language['LW']['01']) # 请输入序列号
            return
        # 获取当前时间戳
        try:
            try:
                current_timestamp = get_ntp_timestamp()
            except:
                current_timestamp = get_web_timestamp()
        except:
            feedback.CPW(language['MP']['02']) # 无法获取时间

        #   如果没有时间会直接停止验证
        if not current_timestamp:
            feedback.CPW(language['MP']['01']) # 无法获取在线时间
            return

        validating = verify_license(public_key, license, cached_device_fingerprint, current_timestamp, public_password)

        if validating[0] == True:
            #   写出许可证文件
            dataM.bin_save_data(os.path.join(Script_path, "Datas", "keys", "license.bin"), license)
            #   关闭验证窗口
            cmds.deleteUI(LicenseWin.WINDOWS_NAME)
            #   打开主程序
            MainStart(cached_device_fingerprint, public_key, public_password, datetime.fromtimestamp(current_timestamp), validating[1])
#-------------------------------------------------------验证窗口











def MainStart(cached_device_fingerprint, public_key, public_password, current_time, expiry_date):
    remaining_time = expiry_date - current_time

    import Arnold_Magic_Node
    importlib.reload(Arnold_Magic_Node)
    Arnold_Magic_Node.Main_program(cached_device_fingerprint, public_key, public_password, remaining_time.days)







def Main_program():
    global cached_device_fingerprint

    # 如果没有身份识别码会创建一个
    if cached_device_fingerprint == None:
        cached_device_fingerprint = generate_device_fingerprint(get_motherboard_id())


    if not os.path.exists(os.path.join(Script_path, "Datas", "keys", "license.bin")):
        LicenseM = LicenseWin()
        LicenseM.show()
    else:
        license = dataM.bin_load_data(os.path.join(Script_path, "Datas", "keys", "license.bin"))

        # 获取当前时间戳
        try:
            try:
                current_timestamp = get_ntp_timestamp()
            except:
                current_timestamp = get_web_timestamp()
        except:
            feedback.CPW(language['MP']['02']) # 无法获取时间

        # 如果没有时间会直接停止验证
        if not current_timestamp:
            feedback.CPW(language['MP']['01']) # 无法获取在线时间
            return

        validating = verify_license(public_key, license, cached_device_fingerprint, current_timestamp, public_password)

        if validating[0] == True:
            MainStart(cached_device_fingerprint, public_key, public_password, datetime.fromtimestamp(current_timestamp), validating[1])
        else:
            LicenseM = LicenseWin()
            LicenseM.show()
