# FISCO BCOS 配置文件
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class FiscoConfig:
    def __init__(self):
        self.base_dir = BASE_DIR

        # 节点信息
        self.node_url = "http://192.168.146.129:8545"
        
        # 合约信息
        self.contract_name = "TextbookTrading"
        self.contract_file = os.path.join(self.base_dir, "TextbookTrading.sol")
        self.contracts_dir = os.path.join(self.base_dir, "contracts")
        
        # 账户信息
        self.account_file = "accounts"
        self.account_name = "default"
        self.account_password = "123456"
        
        # SDK路径
        self.sdk_path = os.path.join(self.base_dir, "python-sdk")

# 创建全局配置实例
config = FiscoConfig()
