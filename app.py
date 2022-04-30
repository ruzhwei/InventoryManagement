from unicodedata import name
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # relative path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Create model for Products and Warehouses with the following attributes.
class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)  # must have a name
    quantity = db.Column(db.Integer, default=1)
    comments = db.Column(db.String(200))
    ware_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"))
    #dp = db.relationship("Warehouse", backref='pers')
# Creates the SQLite database (db).
@app.before_first_request
def create_table():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def index():
    columns = [column.name for column in Products.__mapper__.columns if column.name != "id"]
    # Add new record to the db
    if request.method == "POST":
        new_task = Products(**request.form)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue creating your product"

    # List all.
    else:
        
        products = Products.query.all()
        return render_template("index.html", products=products, columns=columns)


@app.route("/delete/<int:id>")
def delete(id):
    # Delete product with given id value from the db.
    product_to_delete = Products.query.get_or_404(id)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "There was an issue deleting that product"


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    columns = [column.name for column in Products.__mapper__.columns if column.name != "id"]
    product_to_update = Products.query.get_or_404(id)

    # Update a product info, then redirect to "list all".
    if request.method == "POST":
        for column in columns:
            setattr(product_to_update, column, request.form[column])
        try:
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue updating that product"

    # Display the update page for uses to update info.
    else:
        return render_template("update.html", product=product_to_update, columns=columns)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)