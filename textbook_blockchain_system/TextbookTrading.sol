pragma solidity ^0.4.25;

contract TextbookTrading {
    // 教材结构
    struct Textbook {
        string textbookId;
        string isbn;
        string version;
        string condition;
        uint initialPrice;
        bool exists;
    }
    
    // 交易结构
    struct Transaction {
        string transactionId;
        string textbookId;
        address buyer;
        uint offerPrice;
        string status; // pending, completed
        uint timestamp;
        bool exists;
    }
    
    // 事件定义
    event TextbookRegistered(string textbookId, string isbn, string version);
    event TransactionInitiated(string transactionId, string textbookId, address buyer, uint offerPrice);
    event TransactionConfirmed(string transactionId, string textbookId);
    
    // 存储映射
    mapping(string => Textbook) private textbooks;
    mapping(string => Transaction) private transactions;
    mapping(string => string[]) private textbookTransactions; // 教材ID到交易ID的映射
    
    // 注册教材
    function registerTextbook(
        string textbookId,
        string isbn,
        string version,
        string condition,
        uint initialPrice
    ) public {
        require(!textbooks[textbookId].exists, "Textbook already exists");
        
        Textbook memory newTextbook;
        newTextbook.textbookId = textbookId;
        newTextbook.isbn = isbn;
        newTextbook.version = version;
        newTextbook.condition = condition;
        newTextbook.initialPrice = initialPrice;
        newTextbook.exists = true;
        
        textbooks[textbookId] = newTextbook;
        
        emit TextbookRegistered(textbookId, isbn, version);
    }
    
    // 发起交易
    function initiateTransaction(
        string transactionId,
        string textbookId,
        uint offerPrice
    ) public {
        require(textbooks[textbookId].exists, "Textbook does not exist");
        require(!transactions[transactionId].exists, "Transaction already exists");
        
        Transaction memory newTransaction;
        newTransaction.transactionId = transactionId;
        newTransaction.textbookId = textbookId;
        newTransaction.buyer = msg.sender;
        newTransaction.offerPrice = offerPrice;
        newTransaction.status = "pending";
        newTransaction.timestamp = block.timestamp;
        newTransaction.exists = true;
        
        transactions[transactionId] = newTransaction;
        textbookTransactions[textbookId].push(transactionId);
        
        emit TransactionInitiated(transactionId, textbookId, msg.sender, offerPrice);
    }
    
    // 确认交易
    function confirmTransaction(string transactionId) public {
        require(transactions[transactionId].exists, "Transaction does not exist");
        require(keccak256(abi.encodePacked(transactions[transactionId].status)) == keccak256(abi.encodePacked("pending")), "Transaction is not in pending state");
        
        transactions[transactionId].status = "completed";
        transactions[transactionId].timestamp = block.timestamp;
        
        emit TransactionConfirmed(transactionId, transactions[transactionId].textbookId);
    }
    
    // 获取教材信息
    function getTextbook(string textbookId) public view returns (
        string, string, string, string, uint
    ) {
        require(textbooks[textbookId].exists, "Textbook does not exist");
        
        Textbook memory textbook = textbooks[textbookId];
        return (
            textbook.isbn,
            textbook.version,
            textbook.condition,
            textbook.textbookId,
            textbook.initialPrice
        );
    }
    
    // 获取交易信息
    function getTransaction(string transactionId) public view returns (
        string, string, address, uint, string, uint
    ) {
        require(transactions[transactionId].exists, "Transaction does not exist");
        
        Transaction memory transaction = transactions[transactionId];
        return (
            transaction.transactionId,
            transaction.textbookId,
            transaction.buyer,
            transaction.offerPrice,
            transaction.status,
            transaction.timestamp
        );
    }
    
    // 获取教材的交易数量
    function getTextbookTransactionCount(string textbookId) public view returns (uint) {
        return textbookTransactions[textbookId].length;
    }
    
    // 获取教材的交易ID
    function getTextbookTransaction(string textbookId, uint index) public view returns (string) {
        require(index < textbookTransactions[textbookId].length, "Index out of bounds");
        return textbookTransactions[textbookId][index];
    }
    
    // 检查教材是否存在
    function textbookExists(string textbookId) public view returns (bool) {
        return textbooks[textbookId].exists;
    }
    
    // 检查交易是否存在
    function transactionExists(string transactionId) public view returns (bool) {
        return transactions[transactionId].exists;
    }
}