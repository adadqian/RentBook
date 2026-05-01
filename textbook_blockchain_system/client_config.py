# FISCO BCOS Python SDK配置文件
import os
from eth_utils.crypto import CRYPTO_TYPE_GM, CRYPTO_TYPE_ECDSA, set_crypto_type


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ClientConfig:
    def __init__(self):
        # 加密类型
        self.crypto_type = CRYPTO_TYPE_ECDSA  # 使用ECDSA加密类型
        self.ssl_type = "ECDSA"  # 和节点tls通信方式
        set_crypto_type(self.crypto_type)  # 使其全局生效
        
        # 节点信息
        self.ip = "127.0.0.1"
        self.port = "20200"
        self.ssl = False
        
        # 账户信息
        self.account_keyfile_path = os.path.join(BASE_DIR, "python-sdk", "bin", "accounts")  # 保存keystore文件的路径
        self.account_keyfile = "pyaccount.keystore"
        self.account = "default"
        self.password = "123456"
        self.account_password = "123456"  # 账户密码
        self.gm_account_keyfile = "gm_account.json"  # 国密账号的存储文件
        self.gm_account_password = "123456"  # 如果不设密码，置为None或""则不加密
        
        # 合约信息
        self.contract_abi_path = ""
        self.contract_bin_path = ""
        self.contract_address = ""
        self.contract_dir = os.path.join(BASE_DIR, "contracts")
        self.contract_info_file = os.path.join(BASE_DIR, "python-sdk", "bin", "contract.ini")  # 保存已部署合约信息的文件
        
        # 日志配置
        self.log_level = "info"
        self.logdir = os.path.join(BASE_DIR, "logs")
        
        # 协议配置
        self.PROTOCOL_RPC = "rpc"
        self.PROTOCOL_CHANNEL = "channel"
        self.client_protocol = "rpc"  # 使用RPC协议
        self.fiscoChainId = 1  # 链ID，和要通信的节点*必须*一致
        self.groupid = 1  # 群组ID，和要通信的节点*必须*一致
        
        # RPC配置
        self.remote_rpcurl = "http://192.168.146.129:8545"  # 采用rpc通信时，节点的rpc端口
        
        # Channel配置
        self.channel_host = "127.0.0.1"  # 采用channel通信时，节点的channel ip地址
        self.channel_port = 20200  # 节点的channel 端口
        self.channel_ca = ""  # 采用channel协议时，需要设置链证书
        self.channel_node_cert = ""  # 采用channel协议时，需要设置sdk证书
        self.channel_node_key = ""  # 采用channel协议时，需要设置sdk私钥
        self.channel_en_crt = ""  # 仅国密双证书使用，加密证书
        self.channel_en_key = ""  # 仅国密双证书使用，加密key
        
        # 其他配置
        self.gas_price = 1000000000
        self.gas_limit = 999999999
        self.abi_file = ""
        self.bin_file = ""
        self.cert = ""
        self.key = ""
        self.ca = ""
        self.solc_path = "D:\\Solc\\solc.exe"  # Solidity编译器路径
        self.gm_solc_path = "gm_solc"  # 国密编译器路径
        self.solcjs_path = "solcjs"  # JavaScript编译器路径
        
        # 背景运行
        self.background = True

# 创建全局配置实例
client_config = ClientConfig()

# 确保日志目录存在
if not os.path.exists(client_config.logdir):
    os.makedirs(client_config.logdir)

# 确保accounts目录存在
if not os.path.exists(client_config.account_keyfile_path):
    os.makedirs(client_config.account_keyfile_path)
