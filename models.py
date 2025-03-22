from flask_sqlalchemy import SQLAlchemy
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
    images = db.Column(db.Text, default="[]")  # Í¼Æ¬ URL ÁÐ±í

    def get_images(self):
        return json.loads(self.images) if self.images else []
    
    def add_image(self, image_url):
        image_list = self.get_images()
        image_list.append(image_url)
        self.images = json.dumps(image_list)
        
    def __repr__(self):
        return f"<Book {self.book_name}>"
