import os
import uuid
import secrets
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session
from markupsafe import escape
from textbook import TextbookTransaction
from database import DatabaseManager
import hashlib
from datetime import datetime

app = Flask(__name__)
# 持久化 SECRET_KEY
secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.flask_secret')
if os.path.exists(secret_file):
    with open(secret_file, 'r', encoding='utf-8') as f:
        app.secret_key = f.read().strip()
else:
    key = secrets.token_hex(32)
    with open(secret_file, 'w', encoding='utf-8') as f:
        f.write(key)
    app.secret_key = key

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# 确保上传目录存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 初始化系统（使用FISCO BCOS智能合约）
transaction_system = TextbookTransaction()
db_manager = DatabaseManager()

# 静态文件服务
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def generate_user_id(name):
    data = f"{name}_{datetime.now().timestamp()}"
    return hashlib.sha256(data.encode()).hexdigest()[:12]


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login', next=request.path))
        user = db_manager.get_user(user_id)
        if not user or user.get('role') != 'admin':
            return render_error('您没有管理员权限', 403)
        return view_func(*args, **kwargs)

    return wrapper


def render_error(message, status_code=400):
    safe_message = escape(message)
    return render_template('error.html', message=safe_message, status_code=status_code), status_code


def _ensure_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)


def _validate_csrf():
    token = session.get('csrf_token')
    if not token or token != request.form.get('csrf_token'):
        return render_error('CSRF token 验证失败', 403)
    return None


@app.before_request
def before_request():
    _ensure_csrf_token()


@app.route('/')
def index():
    return render_template('index.html')

import os
from werkzeug.utils import secure_filename

# 确保上传目录存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

@app.route('/textbook/register', methods=['GET', 'POST'])
@login_required
def register_textbook():
    if request.method == 'POST':
        isbn = request.form['isbn']
        version = request.form['version']
        condition = request.form['condition']
        initial_price = float(request.form['initial_price'])
        description = request.form['description']
        location = request.form['location']
        
        # 处理文件上传
        photos = []
        if 'photos' in request.files:
            uploaded_files = request.files.getlist('photos')
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # 生成唯一文件名
                    unique_filename = f"{datetime.now().timestamp()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    photos.append(unique_filename)
        
        photos_str = ','.join(photos) if photos else ''
        
        seller_id = session['user_id']
        
        # 教材信息上链
        textbook_id = transaction_system.add_textbook(isbn, version, condition, initial_price)
        
        # 添加教材辅助信息
        db_manager.add_textbook_metadata(
            textbook_id=textbook_id,
            photos=photos_str,
            description=description,
            seller_id=seller_id,
            location=location
        )
        
        return redirect(url_for('textbook_detail', textbook_id=textbook_id))
    return render_template('register_textbook.html')

@app.route('/transaction/initiate', methods=['GET', 'POST'])
@login_required
def initiate_transaction():
    if request.method == 'POST':
        textbook_id = request.form['textbook_id']
        offer_price = float(request.form['offer_price'])

        buyer_id = session['user_id']
        
        # 发起交易
        transaction = transaction_system.initiate_transaction(textbook_id, buyer_id, offer_price)
        
        # 跳转到教材详情页面，显示交易ID
        return redirect(url_for('textbook_detail', textbook_id=textbook_id))
    return render_template('initiate_transaction.html')

@app.route('/transaction/confirm', methods=['GET', 'POST'])
@login_required
def confirm_transaction():
    if request.method == 'POST':
        textbook_id = request.form['textbook_id']
        transaction_id = request.form['transaction_id']

        metadata = db_manager.get_textbook_metadata(textbook_id)
        if not metadata:
            return render_error('教材不存在', 404)
        if metadata.get('seller_id') != session.get('user_id'):
            return render_error('只有卖家才能确认交易', 403)

        transaction_system.confirm_transaction(textbook_id, transaction_id)
        
        # 跳转到教材详情页面，显示交易状态
        return redirect(url_for('textbook_detail', textbook_id=textbook_id))
    return render_template('confirm_transaction.html')


@app.route('/transaction/reject', methods=['POST'])
@login_required
def reject_transaction():
    textbook_id = request.form.get('textbook_id', '').strip()
    transaction_id = request.form.get('transaction_id', '').strip()

    if not textbook_id or not transaction_id:
        return render_error('参数缺失', 400)

    metadata = db_manager.get_textbook_metadata(textbook_id)
    if not metadata:
        return render_error('教材不存在', 404)
    if metadata.get('seller_id') != session.get('user_id'):
        return render_error('只有卖家才能拒绝交易', 403)

    try:
        transaction_system.reject_transaction(textbook_id, transaction_id)
    except ValueError as e:
        return render_error(str(e), 400)
    except Exception as e:
        return render_error(f'拒绝交易失败：{e}', 500)

    return redirect(url_for('dashboard'))

@app.route('/textbook/<textbook_id>')
def textbook_detail(textbook_id):
    # 获取教材交易历史
    history = transaction_system.get_textbook_history(textbook_id)
    
    # 获取教材完整信息
    combined_info = db_manager.get_combined_textbook_info(textbook_id, history)
    
    return render_template('textbook_detail.html', 
                         textbook_id=textbook_id, 
                         history=history, 
                         combined_info=combined_info)


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not name or not contact or not email or not password:
            return render_error('请填写完整信息', 400)

        user_id = uuid.uuid4().hex[:12]
        ok = db_manager.create_user_with_password(user_id, name, contact, email, password)
        if not ok:
            return render_error('注册失败：邮箱已存在或用户已存在', 400)

        # 注册成功，显示等待审核页面
        return render_template('auth_pending.html', email=email)

    return render_template('auth_register.html')


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = db_manager.authenticate_user(email, password)
        if not user:
            return render_error('邮箱或密码错误', 401)

        # 检查用户状态
        if user['status'] == 'pending':
            return render_error('您的账号正在审核中，请等待管理员审批', 403)
        if user['status'] == 'banned':
            return render_error('您的账号已被封禁，请联系管理员', 403)

        session['user_id'] = user['user_id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']

        next_path = request.args.get('next')
        return redirect(next_path or url_for('dashboard'))

    return render_template('auth_login.html')


@app.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ============ Admin Routes ============

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # 统计数据
    user_counts = db_manager.count_users_by_status()
    all_users = db_manager.get_all_users()
    total_users = len(all_users)
    pending_users = sum(1 for u in all_users if u['status'] == 'pending')
    banned_users = sum(1 for u in all_users if u['status'] == 'banned')
    active_users = sum(1 for u in all_users if u['status'] == 'active')

    all_transactions = db_manager.get_all_transactions_with_details()
    total_transactions = len(all_transactions)
    pending_transactions = sum(1 for t in all_transactions if t['status'] == 'pending')
    completed_transactions = sum(1 for t in all_transactions if t['status'] == 'completed')

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        pending_users=pending_users,
        banned_users=banned_users,
        active_users=active_users,
        total_transactions=total_transactions,
        pending_transactions=pending_transactions,
        completed_transactions=completed_transactions,
    )


@app.route('/admin/users')
@admin_required
def admin_users():
    users = db_manager.get_all_users()
    return render_template('admin_users.html', users=users, csrf_token=session.get('csrf_token'))


@app.route('/admin/user/<user_id>/status', methods=['POST'])
@admin_required
def admin_user_status(user_id):
    csrf_error = _validate_csrf()
    if csrf_error:
        return csrf_error

    status = request.form.get('status')
    if status not in ('active', 'banned', 'pending'):
        return render_error('无效的状态', 400)

    # 不允许封禁自己
    if user_id == session.get('user_id') and status == 'banned':
        return render_error('不能封禁自己', 400)

    ok = db_manager.update_user_status(user_id, status)
    if not ok:
        return render_error('操作失败', 500)

    return redirect(url_for('admin_users'))


@app.route('/admin/user/<user_id>/role', methods=['POST'])
@admin_required
def admin_user_role(user_id):
    csrf_error = _validate_csrf()
    if csrf_error:
        return csrf_error

    role = request.form.get('role')
    if role not in ('user', 'admin'):
        return render_error('无效的角色', 400)

    # 不允许将自己降级为普通用户
    if user_id == session.get('user_id') and role == 'user':
        return render_error('不能将自己降级为普通用户', 400)

    ok = db_manager.update_user_role(user_id, role)
    if not ok:
        return render_error('操作失败', 500)

    return redirect(url_for('admin_users'))


@app.route('/admin/transactions')
@admin_required
def admin_transactions():
    transactions = db_manager.get_all_transactions_with_details()
    return render_template('admin_transactions.html', transactions=transactions)


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    textbooks = db_manager.get_textbooks_by_seller(user_id)
    pending_transactions = db_manager.get_pending_transactions_for_seller(user_id)
    buyer_transactions = db_manager.get_transactions_by_buyer(user_id)
    return render_template(
        'dashboard.html',
        textbooks=textbooks,
        pending_transactions=pending_transactions,
        buyer_transactions=buyer_transactions,
    )

@app.route('/transaction/<textbook_id>')
def transaction_detail(textbook_id):
    # 获取教材交易历史
    history = transaction_system.get_textbook_history(textbook_id)
    
    # 获取教材完整信息
    combined_info = db_manager.get_combined_textbook_info(textbook_id, history)
    
    return render_template('textbook_detail.html', 
                         textbook_id=textbook_id, 
                         history=history, 
                         combined_info=combined_info)

@app.route('/blockchain/status')
def blockchain_status():
    from datetime import datetime
    import sqlite3
    from fisco_client import fisco_client

    chain = []
    is_valid = True
    chain_length = 0

    users = {}
    textbooks = {}
    textbook_sellers = {}

    conn = sqlite3.connect('textbook_trade.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name FROM users')
    for user_id, name in cursor.fetchall():
        users[user_id] = name

    cursor.execute('SELECT textbook_id, description, seller_id FROM textbook_metadata')
    for textbook_id, description, seller_id in cursor.fetchall():
        textbooks[textbook_id] = description or '无描述'
        if seller_id:
            textbook_sellers[textbook_id] = seller_id
    conn.close()

    page_size = 5
    try:
        page = int(request.args.get('page', '1'))
    except ValueError:
        page = 1
    if page < 1:
        page = 1

    if fisco_client and fisco_client.is_available():
        try:
            raw_block_number = fisco_client.client.getBlockNumber()
            if isinstance(raw_block_number, str) and raw_block_number.startswith("0x"):
                latest_index = int(raw_block_number, 16)
            else:
                latest_index = int(raw_block_number)

            chain_length = latest_index + 1

            total_pages = max(1, (chain_length + page_size - 1) // page_size)
            if page > total_pages:
                page = total_pages

            end_index = latest_index - (page - 1) * page_size
            start_index = max(0, end_index - page_size + 1)

            for i in range(start_index, end_index + 1):
                block = fisco_client.client.getBlockByNumber(i, True)
                if not block:
                    continue

                timestamp_hex = block.get('timestamp', '0')
                try:
                    timestamp = int(str(timestamp_hex), 16)
                    readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    readable_time = str(timestamp_hex)

                block_info = {
                    'index': i,
                    'timestamp': readable_time,
                    'previous_hash': block.get('parentHash', ''),
                    'hash': block.get('hash', ''),
                    'transactions': []
                }

                for tx in block.get('transactions', []):
                    tx_hash = tx.get('hash', '')
                    tx_input = tx.get('input', '')
                    parsed = None
                    if tx_input and getattr(fisco_client, 'parser', None):
                        try:
                            parsed = fisco_client.parser.parse_transaction_input(tx_input)
                        except Exception:
                            parsed = None

                    tx_info = {
                        'type': '交易',
                        'hash': tx_hash,
                        'from': tx.get('from', ''),
                        'to': tx.get('to', ''),
                        'value': tx.get('value', '0')
                    }

                    if parsed and isinstance(parsed, dict):
                        func_name = parsed.get('name')
                        args = parsed.get('args')
                        if func_name == 'initiateTransaction' and args and len(args) >= 3:
                            transaction_id = args[0]
                            textbook_id = args[1]
                            db_tx = db_manager.get_transaction(transaction_id)
                            buyer_id = db_tx['buyer_id'] if db_tx else ''
                            seller_id = textbook_sellers.get(textbook_id, '')
                            tx_info.update({
                                'type': '交易发起',
                                'textbook_id': textbook_id,
                                'textbook_description': textbooks.get(textbook_id, ''),
                                'buyer_id': buyer_id,
                                'buyer_name': users.get(buyer_id, '未知买家') if buyer_id else '未知买家',
                                'seller_id': seller_id,
                                'seller_name': users.get(seller_id, '未知卖家') if seller_id else '未知卖家',
                                'offer_price': float(args[2]) / 100,
                                'price_label': '买方报价',
                                'status': db_tx['status'] if db_tx else 'pending',
                            })
                        elif func_name == 'confirmTransaction' and args and len(args) >= 1:
                            transaction_id = args[0]
                            db_tx = db_manager.get_transaction(transaction_id)
                            textbook_id = db_tx['textbook_id'] if db_tx else ''
                            buyer_id = db_tx['buyer_id'] if db_tx else ''
                            seller_id = textbook_sellers.get(textbook_id, '')
                            tx_info.update({
                                'type': '交易确认',
                                'textbook_id': textbook_id,
                                'textbook_description': textbooks.get(textbook_id, ''),
                                'buyer_id': buyer_id,
                                'buyer_name': users.get(buyer_id, '未知买家') if buyer_id else '未知买家',
                                'seller_id': seller_id,
                                'seller_name': users.get(seller_id, '未知卖家') if seller_id else '未知卖家',
                                'offer_price': db_tx['offer_price'] if db_tx else 0,
                                'status': db_tx['status'] if db_tx else 'completed',
                            })
                        elif func_name == 'registerTextbook' and args and len(args) >= 5:
                            textbook_id = args[0]
                            seller_id = textbook_sellers.get(textbook_id, '')
                            tx_info.update({
                                'type': '教材注册',
                                'textbook_id': textbook_id,
                                'textbook_description': textbooks.get(textbook_id, ''),
                                'isbn': args[1],
                                'version': args[2],
                                'condition': args[3],
                                'buyer_id': '',
                                'buyer_name': '',
                                'seller_id': seller_id,
                                'seller_name': users.get(seller_id, '未知卖家') if seller_id else '未知卖家',
                                'offer_price': float(args[4]) / 100,
                                'price_label': '初始定价',
                                'status': 'available',
                            })

                    if 'textbook_id' not in tx_info:
                        tx_info.update({
                            'textbook_description': '未知教材',
                            'buyer_name': '未知买家',
                            'offer_price': 0,
                            'status': '未知状态',
                        })

                    block_info['transactions'].append(tx_info)

                chain.append(block_info)

            chain.sort(key=lambda b: b.get('index', 0), reverse=True)
        except Exception as e:
            print(f"获取区块链状态失败: {e}")

    if not chain:
        all_transactions = db_manager.get_all_transactions()
        block_info = {
            'index': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'previous_hash': '0x0000000000000000000000000000000000000000',
            'hash': '0x0000000000000000000000000000000000000000',
            'transactions': []
        }
        for db_tx in all_transactions:
            textbook_id = db_tx.get('textbook_id', '')
            if not textbook_id:
                continue
            buyer_id = db_tx.get('buyer_id', '')
            seller_id = textbook_sellers.get(textbook_id, '')
            block_info['transactions'].append({
                'type': '交易',
                'hash': db_tx.get('blockchain_hash', ''),
                'from': '',
                'to': '',
                'value': '0',
                'textbook_id': textbook_id,
                'textbook_description': textbooks.get(textbook_id, ''),
                'buyer_id': buyer_id,
                'buyer_name': users.get(buyer_id, '未知买家') if buyer_id else '未知买家',
                'seller_id': seller_id,
                'seller_name': users.get(seller_id, '未知卖家') if seller_id else '未知卖家',
                'offer_price': db_tx.get('offer_price', 0),
                'status': db_tx.get('status', '')
            })

        chain = [block_info]
        chain_length = 1

    total_pages = locals().get('total_pages', 1)
    page = locals().get('page', 1)

    return render_template(
        'blockchain_status.html',
        chain=chain,
        is_valid=is_valid,
        chain_length=chain_length,
        page=page,
        total_pages=total_pages,
    )

@app.route('/textbook/search', methods=['GET', 'POST'])
def search_textbook():
    if request.method == 'POST':
        textbook_id = request.form['textbook_id']
        # 获取教材交易历史
        history = transaction_system.get_textbook_history(textbook_id)
        # 获取教材完整信息
        combined_info = db_manager.get_combined_textbook_info(textbook_id, history)
        # 从链上查询真实区块数据构建 related_blocks
        related_blocks = _get_related_blocks_from_chain(textbook_id)
        return render_template('search_result.html',
                             textbook_id=textbook_id,
                             history=history,
                             combined_info=combined_info,
                             related_blocks=related_blocks)
    return render_template('search_textbook.html')


def _get_related_blocks_from_chain(textbook_id):
    """从 FISCO BCOS 链上查询与指定教材相关的区块数据"""
    from datetime import datetime
    from fisco_client import fisco_client

    related_blocks = []

    if not (fisco_client and fisco_client.is_available()):
        return related_blocks

    try:
        raw_block_number = fisco_client.client.getBlockNumber()
        if isinstance(raw_block_number, str) and raw_block_number.startswith("0x"):
            latest_index = int(raw_block_number, 16)
        else:
            latest_index = int(raw_block_number)

        all_transactions = db_manager.get_transactions_by_textbook(textbook_id)
        tx_hashes = {tx['blockchain_hash'] for tx in all_transactions if tx.get('blockchain_hash')}

        for i in range(latest_index + 1):
            block = fisco_client.client.getBlockByNumber(i, True)
            if not block:
                continue

            # 检查该区块是否包含与该教材相关的交易
            block_has_related_tx = False
            for tx in block.get('transactions', []):
                if tx.get('hash', '') in tx_hashes:
                    block_has_related_tx = True
                    break
                # 也检查合约调用中的 textbook_id 参数
                tx_input = tx.get('input', '')
                if tx_input and getattr(fisco_client, 'parser', None):
                    try:
                        parsed = fisco_client.parser.parse_transaction_input(tx_input)
                        if parsed and isinstance(parsed, dict):
                            args = parsed.get('args', [])
                            # registerTextbook / initiateTransaction 的 args 中包含 textbook_id
                            if args and textbook_id in args:
                                block_has_related_tx = True
                                break
                    except Exception:
                        pass

            if not block_has_related_tx:
                continue

            timestamp_hex = block.get('timestamp', '0')
            try:
                readable_time = datetime.fromtimestamp(int(str(timestamp_hex), 16)).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                readable_time = str(timestamp_hex)

            block_info = {
                'index': i,
                'timestamp': readable_time,
                'previous_hash': block.get('parentHash', ''),
                'hash': block.get('hash', ''),
                'transactions': block.get('transactions', [])
            }
            related_blocks.append(block_info)

    except Exception as e:
        print(f"查询相关区块失败: {e}")

    return related_blocks


@app.route('/marketplace')
def marketplace():
    keyword = request.args.get('keyword', '').strip()
    textbooks = db_manager.get_available_textbooks(keyword if keyword else None)
    return render_template('marketplace.html', textbooks=textbooks, keyword=keyword)


def _register_textbook_v2():
    if request.method != 'POST':
        return render_template('register_textbook.html')

    try:
        isbn = request.form['isbn']
        version = request.form['version']
        condition = request.form['condition']
        initial_price = float(request.form['initial_price'])
        description = request.form['description']
        seller_name = request.form['seller_name']
        seller_contact = request.form['seller_contact']
        seller_email = request.form['seller_email']
        location = request.form['location']

        photos = []
        if 'photos' in request.files:
            for file in request.files.getlist('photos'):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().timestamp()}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    photos.append(unique_filename)

        seller_id = generate_user_id(seller_name)
        textbook_id = transaction_system.add_textbook(
            isbn, version, condition, initial_price
        )

        db_manager.add_user(seller_id, seller_name, seller_contact, seller_email)
        db_manager.add_textbook_metadata(
            textbook_id=textbook_id,
            photos=','.join(photos),
            description=description,
            seller_id=seller_id,
            location=location
        )
        return redirect(url_for('textbook_detail', textbook_id=textbook_id))
    except Exception as e:
        return render_error(f"教材登记失败：{e}", 500)


def _initiate_transaction_v2():
    if request.method != 'POST':
        return render_template('initiate_transaction.html')

    try:
        textbook_id = request.form['textbook_id']
        buyer_name = request.form['buyer_name']
        buyer_contact = request.form['buyer_contact']
        buyer_email = request.form['buyer_email']
        offer_price = float(request.form['offer_price'])

        buyer_id = generate_user_id(buyer_name)
        db_manager.add_user(buyer_id, buyer_name, buyer_contact, buyer_email)
        transaction_system.initiate_transaction(textbook_id, buyer_id, offer_price)
        return redirect(url_for('textbook_detail', textbook_id=textbook_id))
    except Exception as e:
        return render_error(f"交易发起失败：{e}", 500)


def _confirm_transaction_v2():
    if request.method != 'POST':
        return render_template('confirm_transaction.html')

    try:
        textbook_id = request.form['textbook_id']
        transaction_id = request.form['transaction_id']
        transaction_system.confirm_transaction(textbook_id, transaction_id)
        return redirect(url_for('textbook_detail', textbook_id=textbook_id))
    except ValueError as e:
        return render_error(f"交易确认失败：{e}", 400)
    except Exception as e:
        return render_error(f"交易确认失败：{e}", 500)


def _blockchain_status_v2():
    from fisco_client import fisco_client

    chain = []
    chain_length = 0
    is_valid = True
    all_transactions = db_manager.get_all_transactions()

    users = {}
    for tx in all_transactions:
        buyer_id = tx.get('buyer_id')
        if buyer_id and buyer_id not in users:
            user = db_manager.get_user(buyer_id)
            if user:
                users[buyer_id] = user['name']

    textbook_meta = {}
    textbook_sellers = {}
    for tx in all_transactions:
        textbook_id = tx.get('textbook_id')
        if textbook_id and textbook_id not in textbook_meta:
            metadata = db_manager.get_textbook_metadata(textbook_id)
            if metadata:
                textbook_meta[textbook_id] = metadata.get('description') or ''
                if metadata.get('seller_id'):
                    textbook_sellers[textbook_id] = metadata['seller_id']
                    seller = db_manager.get_user(metadata['seller_id'])
                    if seller:
                        users[metadata['seller_id']] = seller['name']

    tx_by_hash = {
        tx['blockchain_hash']: tx
        for tx in all_transactions
        if tx.get('blockchain_hash')
    }

    if fisco_client and fisco_client.is_available():
        try:
            chain_length = fisco_client.client.getBlockNumber()
            for i in range(max(0, chain_length - 5), chain_length):
                block = fisco_client.client.getBlockByNumber(i, True)
                if not block:
                    continue

                timestamp_hex = block.get('timestamp', '0')
                try:
                    readable_time = datetime.fromtimestamp(
                        int(timestamp_hex, 16)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    readable_time = str(timestamp_hex)

                block_info = {
                    'index': i,
                    'timestamp': readable_time,
                    'previous_hash': block.get('parentHash', ''),
                    'hash': block.get('hash', ''),
                    'transactions': []
                }

                for tx in block.get('transactions', []):
                    tx_hash = tx.get('hash', '')
                    business_tx = tx_by_hash.get(tx_hash)
                    tx_info = {
                        'type': '交易',
                        'hash': tx_hash,
                        'from': tx.get('from', ''),
                        'to': tx.get('to', ''),
                        'value': tx.get('value', '0')
                    }

                    if business_tx:
                        textbook_id = business_tx.get('textbook_id', '')
                        seller_id = textbook_sellers.get(textbook_id, '')
                        tx_info.update({
                            'textbook_id': textbook_id,
                            'textbook_description': textbook_meta.get(textbook_id, ''),
                            'buyer_id': business_tx.get('buyer_id', ''),
                            'buyer_name': users.get(business_tx.get('buyer_id', ''), '未知买家'),
                            'seller_id': seller_id,
                            'seller_name': users.get(seller_id, '未知卖家'),
                            'offer_price': business_tx.get('offer_price', 0),
                            'status': business_tx.get('status', '')
                        })
                    else:
                        tx_info.update({
                            'textbook_description': '未知教材',
                            'buyer_id': '',
                            'buyer_name': '未知买家',
                            'seller_id': '',
                            'seller_name': '未知卖家',
                            'offer_price': 0,
                            'status': 'unknown'
                        })

                    block_info['transactions'].append(tx_info)

                chain.append(block_info)
        except Exception as e:
            print(f"获取区块链状态失败: {e}")

    if not chain:
        fallback_block = {
            'index': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'previous_hash': '0x0000000000000000000000000000000000000000',
            'hash': '0x0000000000000000000000000000000000000000',
            'transactions': []
        }
        for tx in all_transactions:
            textbook_id = tx.get('textbook_id', '')
            seller_id = textbook_sellers.get(textbook_id, '')
            fallback_block['transactions'].append({
                'type': '交易',
                'hash': tx.get('blockchain_hash', ''),
                'from': '',
                'to': '',
                'value': '0',
                'textbook_id': textbook_id,
                'textbook_description': textbook_meta.get(textbook_id, ''),
                'buyer_id': tx.get('buyer_id', ''),
                'buyer_name': users.get(tx.get('buyer_id', ''), '未知买家'),
                'seller_id': seller_id,
                'seller_name': users.get(seller_id, '未知卖家'),
                'offer_price': tx.get('offer_price', 0),
                'status': tx.get('status', '')
            })

        chain = [fallback_block]
        chain_length = len(chain)

    return render_template(
        'blockchain_status.html',
        chain=chain,
        is_valid=is_valid,
        chain_length=chain_length
    )


# 回退到初始版路由实现，不覆盖原始视图函数。

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
