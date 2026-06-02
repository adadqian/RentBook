from datetime import datetime
import hashlib
import sqlite3
import time

from database import DatabaseManager
from fisco_client import fisco_client


class TextbookTransaction:
    def __init__(self, blockchain=None):
        self.db_manager = DatabaseManager()

    def generate_textbook_id(self, isbn, version):
        data = f"{isbn}_{version}_{datetime.now().timestamp()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _chain_available(self):
        return bool(fisco_client and fisco_client.is_available())

    def _ensure_chain_available(self):
        if not self._chain_available():
            raise RuntimeError("FISCO BCOS 节点当前不可用，无法完成链上操作。")

    def _extract_transaction_hash(self, receipt):
        if isinstance(receipt, dict):
            for key in ("transactionHash", "hash", "transaction_hash", "txhash", "tx_hash"):
                value = receipt.get(key)
                if value:
                    return value

            result = receipt.get("result")
            if isinstance(result, dict):
                return self._extract_transaction_hash(result)
            if isinstance(result, str) and result.startswith("0x"):
                return result

        if isinstance(receipt, tuple):
            for item in receipt:
                tx_hash = self._extract_transaction_hash(item)
                if tx_hash:
                    return tx_hash

        if isinstance(receipt, str) and receipt.startswith("0x"):
            return receipt

        return None

    def _receipt_successful(self, receipt):
        if isinstance(receipt, dict):
            status = receipt.get("status")
            if status is not None:
                status_str = str(status).strip().lower()
                if status_str in {"0x0", "0", "success"}:
                    return True
            if receipt.get("output") == "0x":
                return True
            result = receipt.get("result")
            if isinstance(result, dict):
                return self._receipt_successful(result)
            if isinstance(result, str) and result.startswith("0x"):
                return True

        return self._extract_transaction_hash(receipt) is not None

    def _normalize_count(self, count_result):
        if isinstance(count_result, tuple):
            count_result = count_result[0]
        elif isinstance(count_result, dict):
            count_result = count_result.get("count", 0)
        return int(count_result)

    def _normalize_transaction_id(self, tx_id_result):
        if isinstance(tx_id_result, tuple):
            return tx_id_result[0]
        if isinstance(tx_id_result, dict):
            return tx_id_result.get("transactionId") or tx_id_result.get("transaction_id") or ""
        return tx_id_result

    def _normalize_chain_transaction(self, tx_result):
        if isinstance(tx_result, tuple):
            transaction_id, textbook_id, buyer, offer_price, status, timestamp = tx_result
        elif isinstance(tx_result, dict):
            transaction_id = tx_result.get("transactionId") or tx_result.get("transaction_id") or ""
            textbook_id = tx_result.get("textbookId") or tx_result.get("textbook_id") or ""
            buyer = tx_result.get("buyer") or tx_result.get("buyerAddress") or ""
            offer_price = tx_result.get("offerPrice") or tx_result.get("offer_price") or 0
            status = tx_result.get("status") or ""
            timestamp = tx_result.get("timestamp") or 0
        else:
            raise ValueError("无法解析链上交易数据")

        readable_time = self._timestamp_to_iso(timestamp)

        return {
            "transaction_id": transaction_id,
            "textbook_id": textbook_id,
            "buyer_address": buyer,
            "offer_price": float(offer_price) / 100,
            "status": status,
            "timestamp": readable_time,
        }

    def _normalize_chain_textbook(self, textbook_result):
        if isinstance(textbook_result, tuple):
            isbn, version, condition, textbook_id, initial_price = textbook_result
        elif isinstance(textbook_result, dict):
            isbn = textbook_result.get("isbn") or ""
            version = textbook_result.get("version") or ""
            condition = textbook_result.get("condition") or ""
            textbook_id = textbook_result.get("textbookId") or textbook_result.get("textbook_id") or ""
            initial_price = textbook_result.get("initialPrice") or textbook_result.get("initial_price") or 0
        else:
            raise ValueError("无法解析链上教材数据")

        return {
            "textbook_id": textbook_id,
            "isbn": isbn,
            "version": version,
            "condition": condition,
            "initial_price": float(initial_price) / 100,
        }

    def _timestamp_to_iso(self, timestamp):
        if not timestamp:
            return datetime.now().isoformat()

        try:
            timestamp_value = int(timestamp)
        except (TypeError, ValueError):
            return datetime.now().isoformat()

        # FISCO BCOS 返回值在当前环境里是毫秒时间戳。
        if timestamp_value > 10**12:
            timestamp_value = timestamp_value / 1000.0

        try:
            return datetime.fromtimestamp(timestamp_value).isoformat()
        except (OSError, OverflowError, ValueError):
            return datetime.now().isoformat()

    def _db_update_with_retry(self, func, max_retries=3, delay=0.5):
        """对 DB 写入操作做重试，应对 SQLite 瞬态锁超时等错误"""
        for attempt in range(max_retries):
            try:
                result = func()
                if result:
                    return True
            except sqlite3.OperationalError:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                raise
        return False

    def add_textbook(self, isbn, version, condition, initial_price, description="", photos="", location=""):
        self._ensure_chain_available()

        textbook_id = self.generate_textbook_id(isbn, version)

        # 计算链下辅助数据（描述、照片文件名、交易地点）的哈希摘要，锚定到链上
        off_chain_data = f"{description}|{photos}|{location}"
        off_chain_data_hash = hashlib.sha256(off_chain_data.encode()).hexdigest()

        receipt = fisco_client.register_textbook(
            textbook_id=textbook_id,
            isbn=isbn,
            version=version,
            condition=condition,
            initial_price=int(initial_price * 100),
            off_chain_data_hash=off_chain_data_hash,
        )

        if not self._receipt_successful(receipt):
            raise RuntimeError("教材信息上链失败。")

        return textbook_id

    def initiate_transaction(self, textbook_id, buyer_id, offer_price):
        self._ensure_chain_available()

        # 防止卖家自购（防御性校验）
        metadata = self.db_manager.get_textbook_metadata(textbook_id)
        if metadata and metadata.get('seller_id') == buyer_id:
            raise ValueError("不能购买自己发布的教材。")

        transaction_id = hashlib.sha256(
            f"{textbook_id}_{buyer_id}_{datetime.now().timestamp()}".encode()
        ).hexdigest()[:16]

        # Step 1: 先写入 DB（provisional 状态），确保 DB 成功后再上链
        success = self.db_manager.add_transaction(
            transaction_id=transaction_id,
            textbook_id=textbook_id,
            buyer_id=buyer_id,
            offer_price=offer_price,
            status="pending",
            blockchain_hash="pending",
        )
        if not success:
            raise RuntimeError("链下交易记录写入失败。")

        # Step 2: 链上操作
        receipt = fisco_client.initiate_transaction(
            transaction_id=transaction_id,
            textbook_id=textbook_id,
            offer_price=int(offer_price * 100),
        )

        if not self._receipt_successful(receipt):
            # 链失败 → 回滚 DB 记录
            self.db_manager.delete_transaction(transaction_id)
            raise RuntimeError("交易发起失败，链上未确认。")

        blockchain_hash = self._extract_transaction_hash(receipt)
        if not blockchain_hash:
            # 拿不到 hash → 回滚 DB 记录
            self.db_manager.delete_transaction(transaction_id)
            raise RuntimeError("交易已提交，但未获取到链上交易哈希。")

        # Step 3: 更新 DB 中的真实 blockchain_hash
        self._db_update_with_retry(
            lambda: self.db_manager.update_transaction(transaction_id, blockchain_hash=blockchain_hash),
        )

        return {
            "transaction_id": transaction_id,
            "textbook_id": textbook_id,
            "buyer_id": buyer_id,
            "offer_price": offer_price,
            "status": "pending",
            "blockchain_hash": blockchain_hash,
            "timestamp": datetime.now().isoformat(),
        }

    def confirm_transaction(self, textbook_id, transaction_id):
        self._ensure_chain_available()

        db_tx = self.db_manager.get_transaction(transaction_id)
        if not db_tx:
            raise ValueError("交易不存在。")
        if db_tx["textbook_id"] != textbook_id:
            raise ValueError("交易与教材编号不匹配。")
        if db_tx["status"] != "pending":
            raise ValueError("只有待确认的交易才能完成确认。")

        receipt = fisco_client.confirm_transaction(transaction_id)
        if not self._receipt_successful(receipt):
            raise RuntimeError("链上确认失败，交易状态未更新。")

        blockchain_hash = self._extract_transaction_hash(receipt)
        update_data = {"status": "completed"}
        if blockchain_hash:
            update_data["blockchain_hash"] = blockchain_hash

        # 链上已确认（不可逆），DB 更新加重试防止瞬态错误导致链/库不一致
        db_success = self._db_update_with_retry(
            lambda: self.db_manager.update_transaction(transaction_id, **update_data),
        )
        if not db_success:
            chain_info = f"链上已确认(hash={blockchain_hash or 'unknown'})，但本地DB更新失败。请手动修复 transaction_id={transaction_id}"
            print(f"链/库不一致: {chain_info}")
            raise RuntimeError(chain_info)

        # 对同一教材的其他 pending 交易，先逐个上链拒绝，再批量更新 SQLite
        other_pending_ids = self.db_manager.get_other_pending_transaction_ids(
            textbook_id=textbook_id,
            accepted_transaction_id=transaction_id,
        )
        for tx_id in other_pending_ids:
            try:
                receipt = fisco_client.reject_transaction(tx_id)
                if self._receipt_successful(receipt):
                    chain_hash = self._extract_transaction_hash(receipt)
                    if chain_hash:
                        self.db_manager.update_transaction(tx_id, status="rejected", blockchain_hash=chain_hash)
            except Exception as e:
                print(f"链上拒绝交易 {tx_id} 失败（将在SQLite中标记为rejected）: {e}")

        self.db_manager.reject_other_pending_transactions(
            textbook_id=textbook_id,
            accepted_transaction_id=transaction_id,
        )

        return {
            "transaction_id": transaction_id,
            "textbook_id": textbook_id,
            "status": "completed",
            "blockchain_hash": blockchain_hash or db_tx["blockchain_hash"],
            "timestamp": datetime.now().isoformat(),
        }

    def reject_transaction(self, textbook_id, transaction_id):
        self._ensure_chain_available()

        db_tx = self.db_manager.get_transaction(transaction_id)
        if not db_tx:
            raise ValueError("交易不存在。")
        if db_tx["textbook_id"] != textbook_id:
            raise ValueError("交易与教材编号不匹配。")
        if db_tx["status"] != "pending":
            raise ValueError("只有待确认的交易才能拒绝。")

        # 先链上：调用智能合约拒绝交易
        receipt = fisco_client.reject_transaction(transaction_id)
        if not self._receipt_successful(receipt):
            raise RuntimeError("链上拒绝失败，交易状态未更新。")

        blockchain_hash = self._extract_transaction_hash(receipt)

        # 后链下：更新SQLite状态（加重试防止瞬态错误）
        update_data = {"status": "rejected"}
        if blockchain_hash:
            update_data["blockchain_hash"] = blockchain_hash

        db_success = self._db_update_with_retry(
            lambda: self.db_manager.update_transaction(transaction_id, **update_data),
        )
        if not db_success:
            chain_info = f"链上已拒绝(hash={blockchain_hash or 'unknown'})，但本地DB更新失败。请手动修复 transaction_id={transaction_id}"
            print(f"链/库不一致: {chain_info}")
            raise RuntimeError(chain_info)

        return {
            "transaction_id": transaction_id,
            "textbook_id": textbook_id,
            "status": "rejected",
            "blockchain_hash": blockchain_hash or db_tx.get("blockchain_hash"),
            "timestamp": datetime.now().isoformat(),
        }

    def get_textbook_history(self, textbook_id):
        history = []
        db_transactions = {
            tx["transaction_id"]: tx
            for tx in self.db_manager.get_transactions_by_textbook(textbook_id)
        }

        if self._chain_available():
            try:
                textbook_info = self._normalize_chain_textbook(
                    fisco_client.get_textbook(textbook_id)
                )
                history.append(
                    {
                        "block_index": 0,
                        "timestamp": datetime.now().isoformat(),
                        "transaction": {
                            "type": "textbook",
                            "textbook_id": textbook_id,
                            "isbn": textbook_info["isbn"],
                            "version": textbook_info["version"],
                            "condition": textbook_info["condition"],
                            "initial_price": textbook_info["initial_price"],
                            "status": "available",
                            "data_source": "chain",
                        },
                    }
                )

                count = self._normalize_count(
                    fisco_client.get_textbook_transaction_count(textbook_id)
                )

                for index in range(count):
                    tx_id = self._normalize_transaction_id(
                        fisco_client.get_textbook_transaction(textbook_id, index)
                    )
                    if not tx_id:
                        continue

                    chain_tx = self._normalize_chain_transaction(
                        fisco_client.get_transaction(tx_id)
                    )
                    db_tx = db_transactions.get(tx_id)

                    history.append(
                        {
                            "block_index": index + 1,
                            "timestamp": chain_tx["timestamp"],
                            "transaction": {
                                "type": "transaction",
                                "transaction_id": tx_id,
                                "textbook_id": textbook_id,
                                "buyer_id": db_tx["buyer_id"] if db_tx else "",
                                "buyer_address": chain_tx["buyer_address"],
                                "offer_price": db_tx["offer_price"] if db_tx else chain_tx["offer_price"],
                                "status": db_tx["status"] if db_tx else chain_tx["status"],
                                "timestamp": chain_tx["timestamp"],
                                "blockchain_hash": db_tx["blockchain_hash"] if db_tx else "",
                                "data_source": "chain+sqlite" if db_tx else "chain",
                            },
                        }
                    )

                return history
            except Exception as e:
                print(f"链上历史查询失败，回退到 SQLite: {e}")

        for index, db_tx in enumerate(db_transactions.values(), start=1):
            history.append(
                {
                    "block_index": index,
                    "timestamp": db_tx["created_at"],
                    "transaction": {
                        "type": "transaction",
                        "transaction_id": db_tx["transaction_id"],
                        "textbook_id": db_tx["textbook_id"],
                        "buyer_id": db_tx["buyer_id"],
                        "buyer_address": "",
                        "offer_price": db_tx["offer_price"],
                        "status": db_tx["status"],
                        "timestamp": db_tx["created_at"],
                        "blockchain_hash": db_tx["blockchain_hash"],
                        "data_source": "sqlite-fallback",
                    },
                }
            )

        return history

    def get_all_transactions(self):
        return self.db_manager.get_all_transactions()
