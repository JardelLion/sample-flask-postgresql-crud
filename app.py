from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:%40jardeljr.7@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: Suppress warning

db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    specialisation = db.Column(db.String(50))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, name, specialisation):
        self.name = name
        self.specialisation = specialisation

    def __repr__(self):
        return f"Product {self.id}"
    
   
    

#serializer
class AuthorSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Author
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    specialisation = fields.String(required=True)

        
    

@app.route("/authors", methods=['GET'])
def index():
    get_authors = Author.query.all()
    author_schema = AuthorSchema(many=True)
    authors = author_schema.dump(get_authors)
    return make_response(jsonify({"autors": authors}))

@app.route("/authors", methods=['POST'])
def create_author():
    data = request.get_json()
    author_schema = AuthorSchema()
    author = author_schema.load(data)
    author_instance = Author(**author)

    created_author = author_instance.create()

    result = author_schema.dump(created_author)
    return make_response(jsonify({"author": author}), 201)


@app.route("/authors/<id>", methods=['GET'])
def get_author_by_id(id):
    get_author = Author.query.get(id)
    author_schema = AuthorSchema()

    author = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))


@app.route("/authors/<id>", methods=['PUT'])
def update_author_by_id(id):
    data = request.get_json()
    get_author = Author.query.get(id)
    if data.get("specialisation"):
        get_author.specialisation = data['specialisation']
    
    if data.get('name'):
        get_author.name = data['name']

    db.session.add(get_author)
    db.session.commit()

    author_schema = AuthorSchema(only=['id', 'name', 'specialisation'])
    author = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))


@app.route("/authors/<id>", methods=['DELETE'])
def delete_author_by_id(id):
    get_author = Author.query.get(id)
    db.session.delete(get_author)
    db.session.commit()
    return make_response("", 204)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates the tables if they don't already exist
    app.run(debug=True)
    

