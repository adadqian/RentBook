import sqlite3
import os

from werkzeug.security import check_password_hash, generate_password_hash

class DatabaseManager:
    def __init__(self, db_path='textbook_trade.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 字段迁移：兼容旧表
        cursor.execute("PRAGMA table_info(users)")
        existing_user_columns = {row[1] for row in cursor.fetchall()}
        if 'password_hash' not in existing_user_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
        if 'role' not in existing_user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        if 'status' not in existing_user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
        
        # 创建教材辅助信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS textbook_metadata (
            textbook_id TEXT PRIMARY KEY,
            photos TEXT,
            description TEXT,
            seller_id TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(user_id)
        )
        ''')
        
        # 创建交易表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            textbook_id TEXT,
            buyer_id TEXT,
            offer_price REAL,
            status TEXT,
            blockchain_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (textbook_id) REFERENCES textbook_metadata(textbook_id),
            FOREIGN KEY (buyer_id) REFERENCES users(user_id)
        )
        ''')
        
        conn.commit()
        conn.close()

        # 创建默认管理员账号
        self._ensure_admin_exists()

    def get_user_by_email(self, email):
        if not email:
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, name, contact, email, password_hash, role, status, created_at FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None
        return {
            'user_id': row[0],
            'name': row[1],
            'contact': row[2],
            'email': row[3],
            'password_hash': row[4],
            'role': row[5],
            'status': row[6],
            'created_at': row[7],
        }

    def create_user_with_password(self, user_id, name, contact, email, password):
        if not password:
            raise ValueError('密码不能为空')
        if not email:
            raise ValueError('邮箱不能为空')

        if self.get_user_by_email(email):
            return False

        password_hash = generate_password_hash(password)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (user_id, name, contact, email, password_hash, role, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (user_id, name, contact, email, password_hash, 'user', 'pending'),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def authenticate_user(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not user.get('password_hash'):
            return None
        if not check_password_hash(user['password_hash'], password):
            return None
        return {
            'user_id': user['user_id'],
            'name': user['name'],
            'contact': user['contact'],
            'email': user['email'],
            'role': user['role'],
            'status': user['status'],
        }

    def get_textbooks_by_seller(self, seller_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT textbook_id, photos, description, seller_id, location, created_at FROM textbook_metadata WHERE seller_id = ? ORDER BY created_at DESC',
            (seller_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append(
                {
                    'textbook_id': row[0],
                    'photos': row[1],
                    'description': row[2],
                    'seller_id': row[3],
                    'location': row[4],
                    'created_at': row[5],
                }
            )
        return result

    def get_pending_transactions_for_seller(self, seller_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.transaction_id,
                t.textbook_id,
                t.buyer_id,
                t.offer_price,
                t.status,
                t.blockchain_hash,
                t.created_at,
                u.name as buyer_name,
                u.contact as buyer_contact,
                u.email as buyer_email,
                m.description as textbook_description,
                m.location as textbook_location
            FROM transactions t
            JOIN textbook_metadata m ON m.textbook_id = t.textbook_id
            LEFT JOIN users u ON u.user_id = t.buyer_id
            WHERE m.seller_id = ? AND t.status = 'pending'
            ORDER BY t.created_at DESC
            """,
            (seller_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append(
                {
                    'transaction_id': row[0],
                    'textbook_id': row[1],
                    'buyer_id': row[2],
                    'offer_price': row[3],
                    'status': row[4],
                    'blockchain_hash': row[5],
                    'created_at': row[6],
                    'buyer_name': row[7],
                    'buyer_contact': row[8],
                    'buyer_email': row[9],
                    'textbook_description': row[10],
                    'textbook_location': row[11],
                }
            )
        return result

    def get_transactions_by_buyer(self, buyer_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.transaction_id,
                t.textbook_id,
                t.buyer_id,
                t.offer_price,
                t.status,
                t.blockchain_hash,
                t.created_at,
                t.updated_at,
                m.description as textbook_description,
                m.location as textbook_location,
                m.seller_id as seller_id,
                su.name as seller_name,
                su.contact as seller_contact,
                su.email as seller_email
            FROM transactions t
            LEFT JOIN textbook_metadata m ON m.textbook_id = t.textbook_id
            LEFT JOIN users su ON su.user_id = m.seller_id
            WHERE t.buyer_id = ?
            ORDER BY t.created_at DESC
            """,
            (buyer_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append(
                {
                    'transaction_id': row[0],
                    'textbook_id': row[1],
                    'buyer_id': row[2],
                    'offer_price': row[3],
                    'status': row[4],
                    'blockchain_hash': row[5],
                    'created_at': row[6],
                    'updated_at': row[7],
                    'textbook_description': row[8],
                    'textbook_location': row[9],
                    'seller_id': row[10],
                    'seller_name': row[11],
                    'seller_contact': row[12],
                    'seller_email': row[13],
                }
            )
        return result
    
    def add_user(self, user_id, name, contact, email=None, role='user', status='active'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO users (user_id, name, contact, email, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, contact, email, role, status))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT user_id, name, contact, email, password_hash, role, status, created_at FROM users WHERE user_id = ?',
            (user_id,)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                'user_id': user[0],
                'name': user[1],
                'contact': user[2],
                'email': user[3],
                'password_hash': user[4],
                'role': user[5],
                'status': user[6],
                'created_at': user[7]
            }
        return None
    
    def add_textbook_metadata(self, textbook_id, photos=None, description=None, seller_id=None, location=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO textbook_metadata (textbook_id, photos, description, seller_id, location)
            VALUES (?, ?, ?, ?, ?)
            ''', (textbook_id, photos, description, seller_id, location))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_textbook_metadata(self, textbook_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM textbook_metadata WHERE textbook_id = ?', (textbook_id,))
        metadata = cursor.fetchone()
        conn.close()
        
        if metadata:
            return {
                'textbook_id': metadata[0],
                'photos': metadata[1],
                'description': metadata[2],
                'seller_id': metadata[3],
                'location': metadata[4],
                'created_at': metadata[5]
            }
        return None
    
    def get_combined_textbook_info(self, textbook_id, blockchain_history):
        metadata = self.get_textbook_metadata(textbook_id)
        
        combined_info = {
            'blockchain_history': blockchain_history,
            'metadata': metadata
        }
        
        if metadata and metadata['seller_id']:
            seller_info = self.get_user(metadata['seller_id'])
            combined_info['seller_info'] = seller_info
        
        return combined_info
    
    def update_textbook_metadata(self, textbook_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = []
        update_values = []
        
        for key, value in kwargs.items():
            if key in ['photos', 'description', 'seller_id', 'location']:
                update_fields.append(f"{key} = ?")
                update_values.append(value)
        
        if update_fields:
            update_query = f"UPDATE textbook_metadata SET {', '.join(update_fields)} WHERE textbook_id = ?"
            update_values.append(textbook_id)
            
            cursor.execute(update_query, update_values)
            conn.commit()
            result = cursor.rowcount > 0
        else:
            result = False
        
        conn.close()
        return result
    
    def delete_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result
    
    def delete_textbook_metadata(self, textbook_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM textbook_metadata WHERE textbook_id = ?', (textbook_id,))
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result
    
    def add_transaction(self, transaction_id, textbook_id, buyer_id, offer_price, status='pending', blockchain_hash=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO transactions (transaction_id, textbook_id, buyer_id, offer_price, status, blockchain_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction_id, textbook_id, buyer_id, offer_price, status, blockchain_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_transaction(self, transaction_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = []
        update_values = []
        
        for key, value in kwargs.items():
            if key in ['textbook_id', 'buyer_id', 'offer_price', 'status', 'blockchain_hash']:
                update_fields.append(f"{key} = ?")
                update_values.append(value)
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE transaction_id = ?"
            update_values.append(transaction_id)
            
            cursor.execute(update_query, update_values)
            conn.commit()
            result = cursor.rowcount > 0
        else:
            result = False
        
        conn.close()
        return result

    def reject_other_pending_transactions(self, textbook_id, accepted_transaction_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
            WHERE textbook_id = ? AND status = 'pending' AND transaction_id <> ?
            """,
            (textbook_id, accepted_transaction_id),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected
    
    def get_transaction(self, transaction_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions WHERE transaction_id = ?', (transaction_id,))
        tx = cursor.fetchone()
        conn.close()
        
        if tx:
            return {
                'transaction_id': tx[0],
                'textbook_id': tx[1],
                'buyer_id': tx[2],
                'offer_price': tx[3],
                'status': tx[4],
                'blockchain_hash': tx[5],
                'created_at': tx[6],
                'updated_at': tx[7]
            }
        return None
    
    def get_all_transactions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions ORDER BY created_at DESC')
        txs = cursor.fetchall()
        conn.close()
        
        transactions = []
        for tx in txs:
            transactions.append({
                'transaction_id': tx[0],
                'textbook_id': tx[1],
                'buyer_id': tx[2],
                'offer_price': tx[3],
                'status': tx[4],
                'blockchain_hash': tx[5],
                'created_at': tx[6],
                'updated_at': tx[7]
            })
        return transactions
    
    def get_transactions_by_textbook(self, textbook_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM transactions WHERE textbook_id = ? ORDER BY created_at DESC', (textbook_id,))
        txs = cursor.fetchall()
        conn.close()

        transactions = []
        for tx in txs:
            transactions.append({
                'transaction_id': tx[0],
                'textbook_id': tx[1],
                'buyer_id': tx[2],
                'offer_price': tx[3],
                'status': tx[4],
                'blockchain_hash': tx[5],
                'created_at': tx[6],
                'updated_at': tx[7]
            })
        return transactions

    # ============ Admin methods ============

    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_id, name, contact, email, role, status, created_at FROM users ORDER BY created_at DESC'
        )
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                'user_id': row[0],
                'name': row[1],
                'contact': row[2],
                'email': row[3],
                'role': row[4],
                'status': row[5],
                'created_at': row[6],
            })
        return result

    def update_user_status(self, user_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result

    def update_user_role(self, user_id, role):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', (role, user_id))
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result

    def count_users_by_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status, COUNT(*) FROM users GROUP BY status"
        )
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    def get_all_transactions_with_details(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.transaction_id,
                t.textbook_id,
                t.buyer_id,
                t.offer_price,
                t.status,
                t.blockchain_hash,
                t.created_at,
                t.updated_at,
                b.name as buyer_name,
                b.email as buyer_email,
                m.description as textbook_description,
                m.location as textbook_location,
                s.name as seller_name,
                s.email as seller_email
            FROM transactions t
            LEFT JOIN users b ON b.user_id = t.buyer_id
            LEFT JOIN textbook_metadata m ON m.textbook_id = t.textbook_id
            LEFT JOIN users s ON s.user_id = m.seller_id
            ORDER BY t.created_at DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                'transaction_id': row[0],
                'textbook_id': row[1],
                'buyer_id': row[2],
                'offer_price': row[3],
                'status': row[4],
                'blockchain_hash': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'buyer_name': row[8],
                'buyer_email': row[9],
                'textbook_description': row[10],
                'textbook_location': row[11],
                'seller_name': row[12],
                'seller_email': row[13],
            })
        return result

    def _ensure_admin_exists(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", ('admin',))
        if not cursor.fetchone():
            import os
            default_password = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin')
            password_hash = generate_password_hash(default_password)
            cursor.execute(
                '''INSERT INTO users (user_id, name, contact, email, password_hash, role, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                ('admin_root', '管理员', '13800138000', 'admin', password_hash, 'admin', 'active')
            )
            conn.commit()
        conn.close()
