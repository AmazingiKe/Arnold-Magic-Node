##############################################################################################
# ++导入所需的库和模块

# 标准库
import os  # 提供操作系统功能的模块，例如文件和目录操作
import sys  # 提供与Python解释器和命令行参数交互的功能
import hashlib  # 提供用于生成哈希值的模块（例如MD5, SHA256等）
import json  # 提供用于处理JSON数据的模块
import base64  # 提供用于Base64编码和解码的模块
import importlib  # 提供动态加载和重新加载模块的功能
import time  # 提供时间相关函数，如时间戳、睡眠等
import subprocess  # 提供执行系统命令和启动新进程的功能
import wmi # 提供Windows管理规范接口的功能
import warnings  # 提供警告处理功能
from datetime import datetime, timedelta  # 提供日期和时间的操作功能

# 外部库
import cryptography  # 提供加密和解密相关功能的模块
from cryptography.fernet import Fernet  # 对称加密库，用于加密和解密
from cryptography.hazmat.primitives.asymmetric import rsa  # 提供非对称加密的RSA算法
from cryptography.hazmat.primitives import hashes  # 提供加密中的哈希算法
from cryptography.hazmat.primitives.asymmetric import padding  # 用于设置非对称加密中的填充方式
from cryptography.hazmat.primitives import serialization  # 提供序列化和反序列化密钥的功能
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # 提供密码派生函数
from cryptography.hazmat.backends import default_backend  # 提供默认加密后端支持
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # 提供对称加密的算法和模式
from cryptography.exceptions import InvalidSignature  # 异常处理，处理无效签名
from cryptography.utils import CryptographyDeprecationWarning

import ntplib  # 提供与NTP（网络时间协议）服务器交互的功能
import requests  # 提供HTTP请求功能，用于与网络API交互

# Maya相关库
import maya.OpenMayaUI as omui  # 提供与Maya UI交互的功能
import maya.cmds as cmds  # Maya的命令模块，用于操控Maya中的场景和对象

# 自己的库
import Arnold_Magic_Node_lib  # 自定义的Maya Arnold节点库

# 重新加载模块
importlib.reload(Arnold_Magic_Node_lib)

# 导入PySide，用于Maya中的UI开发
try:
    from PySide6 import QtCore, QtWidgets, QtGui  # PySide6库提供用于开发Qt应用程序的类
    from PySide6.QtCore import Signal, Slot  # 提供信号和槽机制
    from PySide6.QtGui import QAction  # 提供创建菜单和工具栏的动作
    from shiboken6 import wrapInstance  # 将Maya中的C++对象封装为Python对象
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui  # 如果PySide6不可用，使用PySide2
    from PySide2.QtCore import Signal, Slot  # 信号与槽机制
    from PySide2.QtWidgets import QAction  # 创建菜单和工具栏的动作
    from shiboken2 import wrapInstance  # Maya中将C++对象封装为Python对象


warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
##############################################################################################

script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))

dataM = Arnold_Magic_Node_lib.DataManager() # 导入储存模块
feedback = Arnold_Magic_Node_lib.FeedbackPrompt() # 导入报错模块

cached_device_fingerprint = None  # 全局变量，用于缓存主板ID

public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwuxCNMPlIHxyMiKieHem
AgsQNMQjXM9n2i1zN8nWftrmiUAp92QlfJPa17dMZZ64pzTYDMlRGW0fdiXTjkyn
KPrpW4EDhDcA/6ktdOaGBd7tine5WlmJKP979dQ1TapPChWvj3oPDsO/SvskiDaN
9Dp3SxyrpvJEvlrVAYQHcSJ4vqXgBEqeGKSBQUkg3WemuAPXAdGXc+Vxoia+mVbE
A9LOBamOiDcbnKUI8ymtrs26Ukyg6Fqu4+RhS5GDoK77wsK5wdb7X/aXz6m3bwFm
0edzIcRSHDPgd+qHWO69pqQAxTEk+aUoSuAkatqCfyNOEDNtBfw0IxSszEYul+dK
lwIDAQAB
-----END PUBLIC KEY-----"""

public_password = "ea54b522ed180be0691d084cde28c930".encode()

# 获取语言
# 获取语言设置
language_config = dataM.ascii_load_data(os.path.join(script_path, 'Datas', 'settings', 'language_config.json' ))['language_config']
# 加载语言文件
language = dataM.ascii_load_data(os.path.join(script_path, 'Datas', 'languages', f'{language_config}.json' ))["LicenseV"]

##############################################################################################

# 获取主板的ID
def get_motherboard_id():
    LT = language['GMI']

    # Windows 系统
    if os.name == 'nt':  # 'nt' 表示 Windows 系统
        try:
            # 尝试使用 subprocess 获取主板序列号
            output = subprocess.check_output("wmic baseboard get serialnumber", shell=True)
            lines = output.decode().split('\n')
            if len(lines) > 1:
                serial_number = lines[1].strip()  # 获取序列号并去除空白
                if serial_number:
                    return serial_number  # 返回获取到的序列号
            return False  # 序列号为空，返回 False
        except Exception:
            # 如果获取序列号失败，则使用 WMI 作为备选方案
            try:
                c = wmi.WMI()  # 创建 WMI 客户端
                for board in c.Win32_BaseBoard():  # 遍历主板信息
                    return board.SerialNumber  # 返回主板序列号
            except Exception:
                return False  # 如果 WMI 也失败，则返回 False

    # Linux/Unix 系统
    else:
        try:
            # 使用 subprocess 获取产品 UUID
            output = subprocess.check_output("cat /sys/class/dmi/id/product_uuid", shell=True)
            uuid = output.decode().strip()  # 获取 UUID 并去除空白
            if uuid:
                return uuid  # 返回获取到的 UUID
            feedback.CPW(LT['03'])  # "Linux/Unix系统 无法找到主板序列号"
            return False  # 如果 UUID 为空，返回 False
        except Exception as e:
            feedback.CPW(f"{LT['04']} {str(e)}")  # 输出错误信息
            return False  # 捕获到异常，返回 False

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

    LT = language['GWTS']

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
            feedback.CPW(LT['01']) # 无法获取淘宝时间戳"
            return False
    except Exception as e:
        feedback.CPW(LT['02'] + str(e)) # 获取link时间失败:
        return False

# 从阿里云 NTP 服务器获取时间戳
def get_ntp_timestamp(ntp_servers = None):

    LT = language['GNTS']

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
        feedback.CPW(LT['01'] + str(e))
        return False

# 获取本地的时间戳
def get_local_timestamp():
    """
    获取当前本地时间的 Unix 时间戳
    """
    current_timestamp = datetime.now()
    return current_timestamp.timestamp()

#------------------------------------------获取时间戳





# 生成加密密钥
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

# 检查给定的字符串是否是有效的 JSON 格式
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

# 验证许可证并解密
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


        # 验证步骤------------
        # [0]获取许可证内容
        # 获取到期日
        expiry_date = license_data.get("expiry_date")

        # [1]验证指纹锁
        # 检查设备标识符是否匹配：如果提供了当前设备的标识符，确保它与许可证中的设备指纹匹配
        if current_device_fingerprint and license_data["device_fingerprint"] != current_device_fingerprint:
            feedback.CP(LT['02'])
            return False

        # [2]特殊许可证通过
        # 如果是开发者模式的话跳过其他所有的检查
        if license_data['license_type'] == "developer_license":
            return {'validate': True, 'license_type': license_data['license_type'], 'expiry_date' : expiry_date}

        # [3]永久许可证不需要验证时间
        # 如果是永久的许可将不需要验证时间
        if license_data['license_type'] in ['free_license', 'permanent_standard_license', 'permanent_premium_license']:
            return {'validate': True, 'license_type': license_data['license_type'], 'expiry_date': expiry_date}
        else:
            # 以下是非永久许可认证时间

            # 将 current_timestamp 从时间戳转为datatime类型
            current_time = datetime.fromtimestamp(current_timestamp)

            # 将 expiry_date 从字符串转为datatime类型
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')

            # 确保 expiry_date 已被转换为 datetime 对象，以便进行时间比较
            if current_time > expiry_date:
                # 如果当前时间大于到期时间，则许可证已过期
                feedback.CP(LT['03'])
                return False
            else:
                # 如果所有检查通过，返回True，表示许可证有效 并返回许可时间
                return {'validate': True, 'license_type': license_data['license_type'], 'expiry_date': expiry_date}

    except InvalidSignature as e:
        feedback.CPW(LT['04'])
        return False
    except ValueError as e:
        feedback.CPW(LT['05'])
        return False
    except Exception as e:
        feedback.CPE(LT['06'])
        return False

# 获取许可证剩余时间
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

# 获取Maya主窗口
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

        # 判断窗口是否存在，如果存在则删除
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
        self.verify_button.clicked.connect(lambda *args: self.verify_license())

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

        # 如果没有时间会直接停止验证
        if not current_timestamp:
            feedback.CPW(language['MP']['01']) # 无法获取在线时间
            return

        validating = verify_license(public_key, license, cached_device_fingerprint, current_timestamp, public_password)

        if not validating:
            return

        if validating['validate'] == True:
            # 写出许可证文件
            dataM.bin_save_data(os.path.join(script_path, "Datas", "keys", "license.bin"), license)
            # 关闭验证窗口
            cmds.deleteUI(LicenseWin.WINDOWS_NAME)
            # 打开主程序
            MainStart(cached_device_fingerprint, public_key, public_password, validating)

#-------------------------------------------------------验证窗口

def MainStart(cached_device_fingerprint, public_key, public_password, validating):

    import Arnold_Magic_Node
    importlib.reload(Arnold_Magic_Node)
    Arnold_Magic_Node.Main_program(cached_device_fingerprint, public_key, public_password, validating)

def Main_program():
    global cached_device_fingerprint

    # 如果没有身份识别码，则创建一个新的识别码
    if cached_device_fingerprint is None:
        # 获取主板ID
        motherboard_id = get_motherboard_id()

        # 检查是否成功获取主板ID
        if motherboard_id is False:
            feedback.CPW(language['MP']['03'])  # 无法获取设备码
        else:
            # 生成设备指纹
            cached_device_fingerprint = generate_device_fingerprint(motherboard_id)

    if not os.path.exists(os.path.join(script_path, "Datas", "keys", "license.bin")):
        LicenseM = LicenseWin()
        LicenseM.show()
    else:
        license = dataM.bin_load_data(os.path.join(script_path, "Datas", "keys", "license.bin"))

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

        if 'validate' not in validating or validating['validate'] == False:
            LicenseM = LicenseWin()
            LicenseM.show()
        else:
            MainStart(cached_device_fingerprint, public_key, public_password, validating)

