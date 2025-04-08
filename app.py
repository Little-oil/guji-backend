from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Book
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"  # 允许所有来源
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# 处理 OPTIONS 预检请求
@app.route("/api/books", methods=["OPTIONS"])
def handle_options():
    return jsonify({"message": "OK"}), 200


# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tang4.7.sql' # 原本是用books.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "F:/guji/cantaloupe/cantaloupe-5.0.6/images/"  # 图片存储目录
IIIF_SERVER_URL = "http://localhost:8182/iiif/2"  # Cantaloupe 服务器地址

db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 创建数据库
with app.app_context():
    db.create_all()

# 创建书目
@app.route("/api/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        # 获取前端发送的 JSON 数据
        print("123")
        data = request.get_json()
        new_book = Book(
            book_name=data['bookName'],
            version=data['version'],
            author_type=data['authorType'],
            author_name=data['authorName'],
            category=data['category'],
            create_date=data['createDate']
        )
        db.session.add(new_book)
        db.session.commit()

        return jsonify({"message": "Book added successfully!"}), 201

    elif request.method == "GET":
        books = Book.query.all()
        result = [{"bookName": book.book_name, "bookId": book.id, "status": [], "createDate": book.create_date} for book in books]
        return jsonify(result)

# 图片上传
@app.route("/api/upload_image", methods=["POST"])
def upload_image():
    book_id = request.form.get("bookId")
    files = request.files.getlist("files")

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "书籍不存在"}), 404

    image_urls = []  # Cantaloupe 的 URL
    osd_urls = []  # OpenSeadragon 的 URL
    for file in files:
        ext = file.filename.split('.')[-1]  # 获取原始文件扩展名
        filename = f"{uuid.uuid4().hex}.{ext}"  # 生成新的唯一文件名
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)  # 存储到 Cantaloupe 目录

        # Cantaloupe的 URL
        iiif_url = f"{IIIF_SERVER_URL}/{filename}/full/full/0/default.jpg"
        # OpenSeadragon 的 info.json URL
        osd_url = f"{IIIF_SERVER_URL}/{filename}/info.json"

        book.add_image(iiif_url)
        image_urls.append(iiif_url)
        osd_urls.append(osd_url)

    db.session.commit()
    return jsonify({"message": "图片上传成功", "images": book.get_images(), "osd_urls": osd_urls}), 200

# 删除书籍
@app.route("/api/books/<int:book_id>", methods=["DELETE", "OPTIONS"])
def delete_book(book_id):
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200  # 处理 OPTIONS 预检请求

    # 查找书籍
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "书籍不存在"}), 404

    # 获取该书籍的所有图片链接
    images = book.get_images()

    # 删除本地存储的图片文件
    for image_url in images:
        filename = image_url.split("/")[-3]  # 从 IIIF URL 获取文件名
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(file_path):
            os.remove(file_path)  # 删除本地文件
            print(f"已删除图片: {file_path}")
        else:
            print(f"图片不存在: {file_path}")

    # 从数据库中删除该书籍
    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": "书籍和相关图片删除成功"}), 200

# 获取单个书籍信息，包括图片
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "书籍不存在"}), 404

    osd_urls = [url.replace("/full/full/0/default.jpg", "/info.json") for url in book.get_images()]

    # 返回书籍信息，包括图片链接

    return jsonify({
        "bookName": book.book_name,
        "bookId": book.id,
        "version": book.version,
        "authorType": book.author_type,
        "authorName": book.author_name,
        "category": book.category,
        "createDate": book.create_date,
        "images": book.get_images(),
        "osd_urls": osd_urls
    }), 200

# 导入视图文件
from views import *

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
