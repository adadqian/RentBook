from blockchain import Blockchain
from textbook import TextbookTransaction
from database import DatabaseManager
import hashlib
from datetime import datetime

def generate_user_id(name):
    data = f"{name}_{datetime.now().timestamp()}"
    return hashlib.sha256(data.encode()).hexdigest()[:12]

def main():
    print("=== 简易私有链教材交易系统测试 ===")
    
    # 初始化系统
    blockchain = Blockchain()
    textbook_transaction = TextbookTransaction(blockchain)
    db_manager = DatabaseManager()
    
    print("\n1. 测试区块链基本功能")
    print(f"区块链初始化完成，当前区块数量: {len(blockchain.chain)}")
    print(f"区块链有效性: {blockchain.is_chain_valid()}")
    
    print("\n2. 添加用户信息到数据库")
    # 添加卖家用户
    seller_name = "张三"
    seller_id = generate_user_id(seller_name)
    seller_added = db_manager.add_user(seller_id, seller_name, "13800138001", "zhangsan@example.com")
    print(f"卖家 {seller_name} 添加: {'成功' if seller_added else '失败'}")
    
    # 添加买家用户
    buyer_name = "李四"
    buyer_id = generate_user_id(buyer_name)
    buyer_added = db_manager.add_user(buyer_id, buyer_name, "13900139001", "lisi@example.com")
    print(f"买家 {buyer_name} 添加: {'成功' if buyer_added else '失败'}")
    
    print("\n3. 教材信息上链")
    # 录入教材信息
    isbn = "9787111640605"
    version = "第3版"
    condition = "九成新"
    initial_price = 50.0
    
    textbook_id = textbook_transaction.add_textbook(isbn, version, condition, initial_price)
    print(f"教材上链成功，教材ID: {textbook_id}")
    print(f"当前区块数量: {len(blockchain.chain)}")
    
    # 添加教材辅助信息到数据库
    metadata_added = db_manager.add_textbook_metadata(
        textbook_id=textbook_id,
        photos="photo1.jpg,photo2.jpg",
        description="计算机网络教材，轻微使用痕迹",
        seller_id=seller_id,
        location="图书馆三楼"
    )
    print(f"教材辅助信息添加: {'成功' if metadata_added else '失败'}")
    
    print("\n4. 发起交易")
    offer_price = 45.0
    initiate_result = textbook_transaction.initiate_transaction(textbook_id, buyer_id, offer_price)
    print(f"交易发起成功，交易状态: {initiate_result['status']}")
    print(f"当前区块数量: {len(blockchain.chain)}")
    
    print("\n5. 确认交易")
    confirm_result = textbook_transaction.confirm_transaction(textbook_id)
    print(f"交易确认成功，交易状态: {confirm_result['status']}")
    print(f"当前区块数量: {len(blockchain.chain)}")
    
    print("\n6. 查询教材交易历史")
    history = textbook_transaction.get_textbook_history(textbook_id)
    print(f"教材 {textbook_id} 的交易历史:")
    for record in history:
        print(f"  区块 #{record['block_index']} - {record['timestamp']}")
        print(f"  类型: {record['transaction']['type']}")
        print(f"  状态: {record['transaction']['status']}")
        if 'offer_price' in record['transaction']:
            print(f"  价格: {record['transaction']['offer_price']}")
        print()
    
    print("\n7. 测试链上链下数据协同查询")
    combined_info = db_manager.get_combined_textbook_info(textbook_id, history)
    print("=== 完整教材信息 ===")
    print(f"教材ID: {textbook_id}")
    print(f"ISBN: {isbn}")
    print(f"版本: {version}")
    print(f"品相: {condition}")
    print(f"初始定价: {initial_price}元")
    
    if combined_info['metadata']:
        print(f"\n=== 链下辅助信息 ===")
        print(f"照片: {combined_info['metadata']['photos']}")
        print(f"描述: {combined_info['metadata']['description']}")
        print(f"位置: {combined_info['metadata']['location']}")
    
    if combined_info['seller_info']:
        print(f"\n=== 卖家信息 ===")
        print(f"卖家: {combined_info['seller_info']['name']}")
        print(f"联系方式: {combined_info['seller_info']['contact']}")
        print(f"邮箱: {combined_info['seller_info']['email']}")
    
    print("\n8. 验证区块链完整性")
    print(f"区块链有效性: {blockchain.is_chain_valid()}")
    print(f"最终区块数量: {len(blockchain.chain)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()