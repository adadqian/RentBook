# FISCO BCOS 配置文件

class FiscoConfig:
    def __init__(self):
        # 节点信息
        self.node_url = "http://192.168.1.160:8545"
        
        # 合约信息
        self.contract_name = "TextbookTrading"
        self.contract_file = "TextbookTrading.sol"
        
        # 账户信息
        self.account_file = "accounts"
        self.account_name = "default"
        self.account_password = "123456"
        
        # SDK路径
        self.sdk_path = "python-sdk"

# 创建全局配置实例
config = FiscoConfig()