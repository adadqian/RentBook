import sys
import os

# 添加SDK路径到Python路径
sdk_path = "python-sdk"
sys.path.append(sdk_path)

from client.bcosclient import BcosClient
from client.common.compiler import Compiler

# 编译SimpleStorage合约
print("编译SimpleStorage合约...")
compiler = Compiler()
try:
    compiler.compile_file("SimpleStorage.sol")
    print("合约编译成功")
except Exception as e:
    print(f"合约编译失败: {e}")
    sys.exit(1)

# 部署合约
try:
    print("\n初始化 BcosClient...")
    client = BcosClient()
    print("BcosClient 初始化成功!")
    
    # 读取编译后的bin文件
    bin_path = "contracts/SimpleStorage.bin"
    with open(bin_path, 'r') as f:
        contract_bin = f.read()
    
    print("\n部署SimpleStorage合约...")
    result = client.deploy(contract_bin)
    print(f"部署结果: {result}")
    
    if 'contractAddress' in result:
        contract_address = result['contractAddress']
        print(f"合约地址: {contract_address}")
        
        if contract_address != "0x0000000000000000000000000000000000000000":
            print("\n部署成功!")
        else:
            print("\n部署失败: 合约地址为0x0000000000000000000000000000000000000000")
    else:
        print("\n部署失败: 结果中没有contractAddress字段")
    
    client.finish()
except Exception as e:
    print(f"部署测试失败: {e}")
    import traceback
    traceback.print_exc()
