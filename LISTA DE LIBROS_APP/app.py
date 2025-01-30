from flask import Flask, render_template, redirect, url_for, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        """Establecer la contraseña de manera segura usando hashing"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verificar si la contraseña ingresada coincide con el hash"""
        return check_password_hash(self.password, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')  
        db.session.add(admin)
        db.session.commit()

def login_required(f):
    """Decorador para restringir acceso a usuarios autenticados"""
    def wrap(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route("/")
@login_required
def index():
    books = Book.query.all()  
    return render_template('index.html', username=session["username"], books=books)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("logout.html")

@app.route("/add_book", methods=["POST"])
@login_required
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")

    if title and author:
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()

    return redirect(url_for("index"))

@app.route("/delete_book/<int:book_id>")
@login_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="El usuario ya existe.")
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.errorhandler(404)
def error_404(error):
    return render_template("error404.html"), 404

@app.errorhandler(401)
def error_401(error):
    return render_template("error401.html"), 401

@app.route("/cv.html")
def cv():
    return render_template("cv.html")    

if __name__ == "__main__":
    app.run(debug=True)
