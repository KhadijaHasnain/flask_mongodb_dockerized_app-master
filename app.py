import os
import json
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

# Set the URI for the MongoDB instance
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb+srv://root:root@cluster0.dj1uvnv.mongodb.net/myDatabase?retryWrites=true&w=majority")

# Create a PyMongo instance
mongo = PyMongo(app)

# Get the MongoDB collection for books
books_collection = mongo.db.books

def initialize_database():
    # Read data from bookstore.json
    with open('bookstore.json', 'r') as file:
        books_data = json.load(file)

    # Insert data into the MongoDB collection
    books_collection.insert_many(books_data)

# Initialize the database when the application starts
initialize_database()

@app.route('/')
def ping_server():
    return "Welcome to the world."

@app.route('/books', methods=['POST'])
def add_book():
    """
    Inserts a book into the books collection.
    """
    data = request.get_json()
    book_doc = {
        'isbn': data['isbn'],
        'title': data['title'],
        'year': data['year'],
        'price': data['price'],
        'page': data['page'],
        'category': data['category'],
        'coverPhoto': data['coverPhoto'],
        'publisher': data['publisher'],
        'author': data['author']
    }
    books_collection.insert_one(book_doc)
    return jsonify({"message": "Book added successfully"})

@app.route('/genres', methods=['GET'])
def get_all_genres():
    """
    Returns list of all genres in the database.
    """
    genres = books_collection.distinct("category")
    return jsonify({"genres": genres})

@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Updates the book in the books collection.
    """
    data = request.get_json()
    response = books_collection.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {
            "title": data['title'],
            "year": data['year'],
            "price": data['price'],
            "page": data['page'],
            "category": data['category'],
            "coverPhoto": data['coverPhoto'],
            "publisher": data['publisher'],
            "author": data['author']
        }}
    )
    if response.modified_count > 0:
        return jsonify({"message": "Book updated successfully"})
    else:
        return jsonify({"error": "Book not found or user does not have permission to update"}), 404

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Deletes a book from the books collection.
    """
    response = books_collection.delete_one({"_id": ObjectId(book_id)})
    if response.deleted_count > 0:
        return jsonify({"message": "Book deleted successfully"})
    else:
        return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
