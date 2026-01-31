from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "minisocial.db"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- INIT DB ----------
def init_db():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        profile_pic TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        image TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_id INTEGER
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        post_id INTEGER,
        content TEXT
    )
    """)

    db.commit()


# ---------- HOME ----------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/feed")
    return redirect("/login")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            db.commit()
        except:
            return "Username već postoji"

        return redirect("/login")

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            return redirect("/feed")

        return "Pogrešan login"

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- FEED ----------
@app.route("/feed")
def feed():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    posts = db.execute("""
        SELECT posts.*, users.username,
        (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """).fetchall()

    comments = db.execute("""
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
    """).fetchall()

    return render_template("feed.html", posts=posts, comments=comments)


# ---------- NEW POST ----------
@app.route("/post", methods=["GET", "POST"])
def post():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        content = request.form["content"]
        image = request.files.get("image")

        filename = None
        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        db = get_db()
        db.execute(
            "INSERT INTO posts (user_id, content, image) VALUES (?, ?, ?)",
            (session["user_id"], content, filename)
        )
        db.commit()

        return redirect("/feed")

    return render_template("post.html")


# ---------- LIKE ----------
@app.route("/like/<int:post_id>")
def like(post_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    existing = db.execute(
        "SELECT * FROM likes WHERE user_id=? AND post_id=?",
        (session["user_id"], post_id)
    ).fetchone()

    if not existing:
        db.execute(
            "INSERT INTO likes (user_id, post_id) VALUES (?, ?)",
            (session["user_id"], post_id)
        )
        db.commit()

    return redirect("/feed")


# ---------- COMMENT ----------
@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    if "user_id" not in session:
        return redirect("/login")

    content = request.form["content"]

    db = get_db()
    db.execute(
        "INSERT INTO comments (user_id, post_id, content) VALUES (?, ?, ?)",
        (session["user_id"], post_id, content)
    )
    db.commit()

    return redirect("/feed")


# ---------- PROFILE ----------
@app.route("/profile/<int:user_id>")
def profile(user_id):
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    posts = db.execute(
        "SELECT * FROM posts WHERE user_id=?",
        (user_id,)
    ).fetchall()

    return render_template("profile.html", user=user, posts=posts)


# ---------- RUN ----------
if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    init_db()
    app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)