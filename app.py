from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render上の環境変数 DATABASE_URL があればそれを使い、なければローカルの sqlite を使う
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///todo.db'

db = SQLAlchemy(app)


# --- 変更前 ---
# class Post(db.Model):
#     ...
# with app.app_context():
#     db.create_all()

# --- 変更後（このように書き換えてください） ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)

# 明示的に Post をコンテキスト内で意識させてから create_all を呼ぶ
with app.app_context():
    _ = Post
    db.create_all()
    print("Database tables created successfully!") # ログ確認用

















# # 1. 先にモデル（テーブルの構造）を定義する
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(30), nullable=False)
#     detail = db.Column(db.String(100))
#     due = db.Column(db.DateTime, nullable=False)

# # 2. モデルを定義した「後」に create_all を実行する
# with app.app_context():
#     db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()
        return render_template('index.html', posts=posts)
    
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')
    
        # インデントを正しく修正し、due が空（Noneや空文字）の場合の安全対策を入れる
        if due:
            due = datetime.strptime(due, '%Y-%m-%d')
        else:
            due = datetime.today() # 期限が空なら、とりあえず今日のインダストリをセット（任意で変更してください）
        
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()

        return redirect('/')


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/detail/<int:id>')
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)

    if request.method == 'GET':
        return render_template('update.html', post=post)
        
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        
        # update側も due が空だった場合の安全対策
        due_form = request.form.get('due')
        if due_form:
            post.due = datetime.strptime(due_form, '%Y-%m-%d')
        
        db.session.commit()
        return redirect('/')
    
   
@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()

    return redirect('/')

@app.route('/init-db')
def init_db():
    try:
        # 明示的にモデルを意識させてからテーブルを作成
        _ = Post
        db.create_all()
        return "データベーステーブルの作成に成功しました！トップページ（ / ）に戻ってください。"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"





if __name__ == '__main__':
    app.run(debug=True)