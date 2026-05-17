from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# SECRET KEY
app.secret_key = 'bps_sumba_timur_2026_super_secure'

# DATABASE (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =========================
# MODEL USER
# =========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)


# =========================
# MODEL LINK
# =========================
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bidang = db.Column(db.String(100))
    judul = db.Column(db.String(200))
    link = db.Column(db.String(500))


# =========================
# LOGIN
# =========================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect('/admin')
            else:
                return redirect('/dashboard')

    return render_template('login.html')


# =========================
# DASHBOARD USER
# =========================
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')

    cari = request.args.get('cari')
    bidang = request.args.get('bidang')

    query = Link.query

    if cari:
        query = query.filter(Link.judul.contains(cari))

    if bidang and bidang != 'Semua':
        query = query.filter_by(bidang=bidang)

    data = query.all()

    return render_template(
        'dashboard.html',
        data_link=data,
        username=session['username'],
        total_link=Link.query.count(),
        total_bidang=6,
        total_user=User.query.count()
    )


# =========================
# TAMBAH LINK
# =========================
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if 'username' not in session:
        return redirect('/')

    if request.method == 'POST':
        data = Link(
            bidang=request.form['bidang'],
            judul=request.form['judul'],
            link=request.form['link']
        )

        db.session.add(data)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('tambah.html')


# =========================
# EDIT LINK
# =========================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    data = Link.query.get_or_404(id)

    if request.method == 'POST':
        data.bidang = request.form['bidang']
        data.judul = request.form['judul']
        data.link = request.form['link']

        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit.html', data=data)


# =========================
# HAPUS LINK
# =========================
@app.route('/hapus/<int:id>')
def hapus(id):
    data = Link.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    return redirect('/dashboard')


# =========================
# ADMIN PAGE
# =========================
@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect('/')

    return render_template(
        'admin.html',
        data_link=Link.query.all(),
        data_user=User.query.all(),
        username=session['username']
    )


# =========================
# TAMBAH USER (ADMIN)
# =========================
@app.route('/tambah_user', methods=['GET', 'POST'])
def tambah_user():
    if session.get('role') != 'admin':
        return redirect('/')

    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            role=request.form['role']
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/admin')

    return render_template('tambah_user.html')


# =========================
# EDIT USER
# =========================
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.password = request.form['password']
        user.role = request.form['role']

        db.session.commit()
        return redirect('/admin')

    return render_template('edit_user.html', user=user)


# =========================
# HAPUS USER
# =========================
@app.route('/hapus_user/<int:id>')
def hapus_user(id):
    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return redirect('/admin')


# =========================
# EXPORT EXCEL
# =========================
@app.route('/export_excel')
def export_excel():
    if session.get('role') != 'admin':
        return redirect('/')

    data = Link.query.all()

    hasil = []
    for item in data:
        hasil.append({
            'Bidang': item.bidang,
            'Judul': item.judul,
            'Link': item.link
        })

    df = pd.DataFrame(hasil)

    file_name = 'data_link.xlsx'
    df.to_excel(file_name, index=False)

    return send_file(file_name, as_attachment=True)


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================
# INIT DATABASE (RENDER SAFE)
# =========================
with app.app_context():
    db.create_all()

    # auto create admin
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()


# =========================
# RUN (LOCAL ONLY)
# =========================
if __name__ == '__main__':
    app.run(debug=True)