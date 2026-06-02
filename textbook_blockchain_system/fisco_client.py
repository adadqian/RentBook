import sys
import os
from fisco_config import config

# 添加SDK路径到Python路径
if config.sdk_path not in sys.path:
    sys.path.append(config.sdk_path)

try:
    from client.bcosclient import BcosClient
    from client.datatype_parser import DatatypeParser
    from client.common.compiler import Compiler
    _sdk_available = True
except ImportError as e:
    print(f"FISCO BCOS SDK 未安装或配置不正确: {e}")
    print("系统将以模拟模式运行（仅使用 SQLite 数据库）")
    _sdk_available = False
    BcosClient = None
    DatatypeParser = None
    Compiler = None

class FiscoClient:
    def __init__(self):
        if not _sdk_available:
            print("FISCO BCOS SDK 不可用，FiscoClient 将以离线模式运行")
            self.client = None
            self.parser = None
            self.contract_abi = None
            self.contract_address = None
            return

        # 编译合约
        self._compile_contract()

        # 初始化客户端
        self.client = BcosClient()
        print("BcosClient 初始化成功!")

        # 解析合约ABI
        self.contract_abi_path = os.path.join(config.contracts_dir, f"{config.contract_name}.abi")
        self.contract_bin_path = os.path.join(config.contracts_dir, f"{config.contract_name}.bin")

        self.parser = DatatypeParser(self.contract_abi_path)
        self.parser.load_abi_file(self.contract_abi_path)
        self.contract_abi = self.parser.contract_abi

        # 合约地址文件
        self.contract_address_file = os.path.join(config.base_dir, "contract_address.txt")

        # 尝试加载已保存的合约地址
        if os.path.exists(self.contract_address_file):
            try:
                with open(self.contract_address_file, 'r') as f:
                    self.contract_address = f.read().strip()
                print(f"加载已保存的合约地址: {self.contract_address}")
            except Exception as e:
                print(f"加载合约地址失败: {e}")
                # 加载失败，重新部署
                self.contract_address = self._deploy_contract()
                self._save_contract_address()
        else:
            # 部署新合约
            self.contract_address = self._deploy_contract()
            self._save_contract_address()

        print(f"合约地址: {self.contract_address}")
    
    def is_available(self):
        """检查节点与合约地址当前是否可用。"""
        if not _sdk_available:
            return False
        if not getattr(self, "client", None):
            return False
        if not getattr(self, "contract_address", ""):
            return False
        if self.contract_address == "0x0000000000000000000000000000000000000000":
            return False

        try:
            self.client.getBlockNumber()
            return True
        except Exception as e:
            print(f"FISCO BCOS 节点不可用: {e}")
            return False

    def _save_contract_address(self):
        """保存合约地址到文件"""
        try:
            with open(self.contract_address_file, 'w') as f:
                f.write(self.contract_address)
            print(f"合约地址已保存到 {self.contract_address_file}")
        except Exception as e:
            print(f"保存合约地址失败: {e}")
    
    def _compile_contract(self):
        """编译Solidity合约"""
        print("编译合约...")
        compiler = Compiler()
        try:
            compiler.compile_file(config.contract_file, config.contracts_dir)
            print("合约编译成功")
        except Exception as e:
            print(f"合约编译失败: {e}")
            raise Exception(f"合约编译失败: {e}")
    
    def _deploy_contract(self):
        """部署智能合约"""
        print("部署合约...")
        with open(self.contract_bin_path, 'r') as f:
            contract_bin = f.read()
        
        result = self.client.deploy(contract_bin)
        print(f"部署结果: {result}")
        
        if 'contractAddress' in result:
            contract_address = result['contractAddress']
            print(f"获取到合约地址: {contract_address}")
            return contract_address
        else:
            print("部署结果中没有contractAddress字段")
            # 尝试从其他字段获取合约地址
            if 'output' in result:
                print(f"output字段: {result['output']}")
            raise Exception("部署合约失败，无法获取合约地址")
    
    def register_textbook(self, textbook_id, isbn, version, condition, initial_price, off_chain_data_hash):
        """注册教材"""
        print(f"注册教材: {textbook_id}")
        func_name = "registerTextbook"
        args = [textbook_id, isbn, version, condition, initial_price, off_chain_data_hash]

        receipt = self.client.sendRawTransactionGetReceipt(self.contract_address, self.contract_abi, func_name, args)
        print(f"注册教材结果: {receipt}")
        return receipt
    
    def initiate_transaction(self, transaction_id, textbook_id, offer_price):
        """发起交易"""
        print(f"发起交易: {transaction_id}")
        func_name = "initiateTransaction"
        args = [transaction_id, textbook_id, offer_price]
        
        receipt = self.client.sendRawTransactionGetReceipt(self.contract_address, self.contract_abi, func_name, args)
        print(f"发起交易结果: {receipt}")
        return receipt
    
    def confirm_transaction(self, transaction_id):
        """确认交易"""
        print(f"确认交易: {transaction_id}")
        func_name = "confirmTransaction"
        args = [transaction_id]

        receipt = self.client.sendRawTransactionGetReceipt(self.contract_address, self.contract_abi, func_name, args)
        print(f"确认交易结果: {receipt}")
        return receipt

    def reject_transaction(self, transaction_id):
        """拒绝交易"""
        print(f"拒绝交易: {transaction_id}")
        func_name = "rejectTransaction"
        args = [transaction_id]

        receipt = self.client.sendRawTransactionGetReceipt(self.contract_address, self.contract_abi, func_name, args)
        print(f"拒绝交易结果: {receipt}")
        return receipt
    
    def get_textbook(self, textbook_id):
        """获取教材信息"""
        func_name = "getTextbook"
        args = [textbook_id]
        
        result = self.client.call(self.contract_address, self.contract_abi, func_name, args)
        print(f"获取教材信息: {result}")
        return result
    
    def get_transaction(self, transaction_id):
        """获取交易信息"""
        func_name = "getTransaction"
        args = [transaction_id]
        
        result = self.client.call(self.contract_address, self.contract_abi, func_name, args)
        print(f"获取交易信息: {result}")
        return result
    
    def get_textbook_transaction_count(self, textbook_id):
        """获取教材的交易数量"""
        func_name = "getTextbookTransactionCount"
        args = [textbook_id]
        
        result = self.client.call(self.contract_address, self.contract_abi, func_name, args)
        return result
    
    def get_textbook_transaction(self, textbook_id, index):
        """获取教材的交易ID"""
        func_name = "getTextbookTransaction"
        args = [textbook_id, index]
        
        result = self.client.call(self.contract_address, self.contract_abi, func_name, args)
        return result
    
    def close(self):
        """关闭客户端"""
        if self.client:
            self.client.finish()

# 创建全局客户端实例
try:
    fisco_client = FiscoClient()
except Exception as e:
    print(f"初始化FISCO客户端失败: {e}")
    print("警告: FISCO BCOS节点未运行，系统将使用本地模拟模式")
    fisco_client = None
