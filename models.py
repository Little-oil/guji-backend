from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    author_type = db.Column(db.String(50), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    create_date = db.Column(db.String(50), nullable=False)
    images = db.Column(db.Text, default="[]")  # ?? URL ?б?

    def get_images(self):
        return json.loads(self.images) if self.images else []
    
    def add_image(self, image_url):
        image_list = self.get_images()
        image_list.append(image_url)
        self.images = json.dumps(image_list)
        
    def __repr__(self):
        return f"<Book {self.book_name}>"


class Words(db.Model):
    __tablename__ = 'Words'

    id = db.Column(db.Integer, primary_key=True)  # 字库的唯一标识符（主键）
    wid = db.Column(db.Integer, nullable=True)  # 可能的外部字库编号
    prefix = db.Column(db.String(255), nullable=False, default='')  # 字的前缀（如部首信息）
    articleId = db.Column(db.Integer, db.ForeignKey('Articles.id'), nullable=True)  # 文章 ID（外键，关联 `Articles` 表）
    epigraphId = db.Column(db.String(255), db.ForeignKey('epigraphs.epigraphId'), nullable=False,
                           default='')  # 墓志 ID（外键，关联 `epigraphs` 表）
    notation = db.Column(db.String(255), nullable=False, default='')  # 字的注释信息
    articleName = db.Column(db.String(255), nullable=False, default='')  # 文章名称
    sid = db.Column(db.Integer, nullable=False)  # 句子 ID
    uniqueSId = db.Column(db.Integer, nullable=False)  # 唯一的句子编号
    sOrder = db.Column(db.Integer, nullable=False)  # 字在句子中的顺序
    bookName = db.Column(db.String(255), nullable=False, default='')  # 所属书籍名称
    imageId = db.Column(db.String(255), nullable=False, default='')  # 该字的图片 ID
    realArticleId = db.Column(db.Integer, nullable=True)  # 真实文章 ID
    fArticleName = db.Column(db.String(255), nullable=False, default='')  # 可能的原始文章名称
    createdAt = db.Column(db.DateTime, nullable=False)  # 记录创建时间
    updatedAt = db.Column(db.DateTime, nullable=False)  # 记录最后更新时间

    def __repr__(self):
        return f"<Word {self.prefix} ({self.notation})>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False, unique=True)  # 用户手机号
    password = db.Column(db.String(128), nullable=False)  # 加密后的密码
    verification_code = db.Column(db.String(6), nullable=True)  # 验证码
    code_expiry = db.Column(db.DateTime, nullable=True)  # 验证码过期时间

    def __repr__(self):
        return f"<User {self.phone}>"
