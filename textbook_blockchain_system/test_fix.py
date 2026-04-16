import requests
import json

# 测试教材注册
def test_register_textbook():
    print("=== 测试教材注册 ===")
    url = "http://127.0.0.1:5000/textbook/register"
    data = {
        'isbn': '9787111601939',
        'version': '第1版',
        'condition': '九成新',
        'initial_price': '50',
        'description': '测试教材，用于链上链下数据关联测试',
        'location': '测试位置',
        'seller_name': '测试卖家',
        'seller_contact': '13800138000',
        'seller_email': 'test@example.com'
    }
    response = requests.post(url, data=data)
    print(f"注册响应状态码: {response.status_code}")
    print(f"注册响应内容: {response.text}")
    return response

# 测试发起交易
def test_initiate_transaction(textbook_id):
    print("\n=== 测试发起交易 ===")
    url = "http://127.0.0.1:5000/transaction/initiate"
    data = {
        'textbook_id': textbook_id,
        'buyer_name': '测试买家',
        'buyer_contact': '13900139000',
        'buyer_email': 'buyer@example.com',
        'offer_price': '45'
    }
    response = requests.post(url, data=data)
    print(f"发起交易响应状态码: {response.status_code}")
    print(f"发起交易响应内容: {response.text}")
    return response

# 测试区块链状态
def test_blockchain_status():
    print("\n=== 测试区块链状态 ===")
    url = "http://127.0.0.1:5000/blockchain/status"
    response = requests.get(url)
    print(f"区块链状态响应状态码: {response.status_code}")
    # 打印响应内容的前1000个字符，以查看是否有卖家信息
    print(f"区块链状态响应内容前1000字符: {response.text[:1000]}")
    return response

if __name__ == "__main__":
    # 使用手动提取的教材ID
    textbook_id = "9140612a11d348a7"
    print(f"使用教材ID: {textbook_id}")
    
    # 发起交易
    initiate_response = test_initiate_transaction(textbook_id)
    
    # 查看区块链状态
    blockchain_response = test_blockchain_status()