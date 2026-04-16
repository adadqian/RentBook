import sys
import os

# 添加SDK路径到Python路径
sdk_path = "python-sdk"
sys.path.append(sdk_path)

from client.bcosclient import BcosClient
from client_config import client_config

# 测试连接
try:
    print("正在初始化 BcosClient...")
    client = BcosClient()
    print("BcosClient 初始化成功!")
    
    print("\n获取节点版本信息...")
    version = client.getNodeVersion()
    print(f"节点版本: {version}")
    
    print("\n获取区块高度...")
    block_number = client.getBlockNumber()
    print(f"区块高度: {block_number}")
    
    print("\n连接测试成功!")
    client.finish()
except Exception as e:
    print(f"连接测试失败: {e}")
    import traceback
    traceback.print_exc()
