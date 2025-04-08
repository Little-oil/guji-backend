from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
from app import app
from models import db, Book, Character, User

# 获取汉字信息
@app.route('/api/characters/<string:char>', methods=['GET'])
def get_character(char):
    character = Character.query.filter_by(simplified=char).first()  # 查询简体字
    if not character:
        character = Character.query.filter_by(traditional=char).first()  # 查询繁体字
    if not character:
        character = Character.query.filter_by(variant=char).first()  # 查询异体字

    if character:
        # 返回汉字信息
        response = {
            'simplified': character.simplified,
            'traditional': character.traditional,
            'variant': character.variant,
            'pronunciation': character.pronunciation,
            'notation': character.meaning,
            'image_url': character.image_url
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Character not found'}), 404

# 生成并发送验证码
@app.route("/api/create_code", methods=["POST"])
def create_code():
    data = request.get_json()
    phone = data['phone']

    user = User.query.filter_by(phone=phone).first()
    if user:
        # 生成
        verification_code = str(random.randint(100000, 999999))
        user.verification_code = verification_code
        user.code_expiry = datetime.now() + timedelta(minutes=5)
        db.session.commit()
        # 发送

        return jsonify({"message": "验证码已发送"}), 200
    else:
        return jsonify({"message": "该用户尚未注册"}), 400

# 验证验证码
@app.route("/api/verify_code", methods=["POST"])
def verify_code(phone, input_code):
    user = User.query.filter_by(phone=phone).first()
    if user and user.verification_code == input_code:
        if user.code_expiry > datetime.now():
            return True, {"message": "验证成功"}
        else:
            return False, {"error": "验证码已过期"}
    return False, {"error": "验证码错误"}

# 注册用户
@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json()
    phone = data['phone']
    password = data['password']

    # 检查手机号是否已存在
    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "手机号已被注册"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(phone=phone, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "注册成功"}), 201

# 用户登录
@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    phone = data['phone']
    user = User.query.filter_by(phone=phone).first()

    # 密码登录
    if 'password' in data:
        password = data['password']
        if user and check_password_hash(user.password, password):
            return jsonify({"message": "登录成功"}), 200
        return jsonify({"error": "手机号或密码错误"}), 400
    # 验证码登录
    elif 'code' in data:
        input_code = data['code']
        is_valid, response = verify_code(phone, input_code)
        if is_valid:
            return jsonify({"message": "登录成功"}), 200
        else:
            return jsonify(response),400

# 重置密码
@app.route("/api/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json()
    phone = data['phone']
    input_code = data['code']
    new_password = data['new_password']

    user = User.query.filter_by(phone=phone).first()
    if user:
        is_valid, response = verify_code(phone, input_code)
        if is_valid:
            hashed_password = generate_password_hash(new_password)
            user.password = hashed_password
            user.verification_code = None  # 清空验证码
            user.code_expiry = None  # 清空过期时间
            db.session.commit()
            return jsonify({"message": "密码已重置成功"}), 200
        else:
            return jsonify({"error": "验证码已过期"}), 400
    return jsonify({"error": "验证码错误"}), 400