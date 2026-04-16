import hashlib
import json
from datetime import datetime
import os

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, block_dict):
        block = cls(
            index=block_dict['index'],
            timestamp=block_dict['timestamp'],
            transactions=block_dict['transactions'],
            previous_hash=block_dict['previous_hash']
        )
        # 验证存储的哈希值与计算的哈希值是否一致
        if 'hash' in block_dict:
            stored_hash = block_dict['hash']
            calculated_hash = block.calculate_hash()
            if stored_hash == calculated_hash:
                block.hash = stored_hash
            # 如果哈希值不一致，保持计算的哈希值（可能是数据被篡改或计算逻辑变更）
        return block

class Blockchain:
    def __init__(self, data_file='blockchain_data.json'):
        self.data_file = data_file
        self.chain = self._load_from_file()
    
    def _load_from_file(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    chain_data = json.load(f)
                    return [Block.from_dict(block_dict) for block_dict in chain_data]
            except:
                return [self.create_genesis_block()]
        else:
            return [self.create_genesis_block()]
    
    def _save_to_file(self):
        chain_data = [block.to_dict() for block in self.chain]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(chain_data, f, indent=2, ensure_ascii=False)
    
    def create_genesis_block(self):
        return Block(0, datetime.now().isoformat(), [], "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        self._save_to_file()
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
    
    def get_chain(self):
        return [block.to_dict() for block in self.chain]
    
    def clear_chain(self):
        self.chain = [self.create_genesis_block()]
        self._save_to_file()