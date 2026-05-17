from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SECRET KEY
app.secret_key = 'bps_sumba_timur_2026_super_secure'

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# TABEL USER
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))

    role = db.Column(db.String(20))

# TABEL LINK
class Link(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    bidang = db.Column(db.String(100))

    judul = db.Column(db.String(200))

    link = db.Column(db.String(500))

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # CEK USER DATABASE
        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['username'] = user.username
            session['role'] = user.role

            # ADMIN
            if user.role == 'admin':
                return redirect('/admin')

            # USER
            else:
                return redirect('/dashboard')

    return render_template('login.html')

# DASHBOARD USER
@app.route('/dashboard')
def dashboard():

    # CEK LOGIN
    if 'username' not in session:
        return redirect('/')

    # SEARCH
    cari = request.args.get('cari')

    # FILTER BIDANG
    bidang = request.args.get('bidang')

    query = Link.query

    # SEARCH JUDUL
    if cari:
        query = query.filter(
            Link.judul.contains(cari)
        )

    # FILTER BIDANG
    if bidang and bidang != 'Semua':
        query = query.filter_by(
            bidang=bidang
        )

    semua_link = query.all()

    total_link = Link.query.count()

    total_bidang = 6

    total_user = User.query.count()

    return render_template(
        'dashboard.html',
        data_link=semua_link,
        username=session['username'],
        total_link=total_link,
        total_bidang=total_bidang,
        total_user=total_user
    )

# TAMBAH LINK
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():

    # CEK LOGIN
    if 'username' not in session:
        return redirect('/')

    if request.method == 'POST':

        bidang = request.form['bidang']
        judul = request.form['judul']
        link = request.form['link']

        data_baru = Link(
            bidang=bidang,
            judul=judul,
            link=link
        )

        db.session.add(data_baru)

        db.session.commit()

        return redirect('/dashboard')

    return render_template('tambah.html')

# EDIT LINK
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    data = Link.query.get(id)

    if request.method == 'POST':

        data.bidang = request.form['bidang']
        data.judul = request.form['judul']
        data.link = request.form['link']

        db.session.commit()

        return redirect('/dashboard')

    return render_template(
        'edit.html',
        data=data
    )

# HAPUS LINK
@app.route('/hapus/<int:id>')
def hapus(id):

    data = Link.query.get(id)

    db.session.delete(data)

    db.session.commit()

    return redirect('/dashboard')

# ADMIN
@app.route('/admin')
def admin():

    # CEK LOGIN
    if 'username' not in session:
        return redirect('/')

    semua_link = Link.query.all()

    semua_user = User.query.all()

    return render_template(
        'admin.html',
        data_link=semua_link,
        data_user=semua_user,
        username=session['username']
    )

# TAMBAH USER
@app.route('/tambah_user', methods=['GET', 'POST'])
def tambah_user():

    # HANYA ADMIN
    if session.get('role') != 'admin':
        return redirect('/')

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user_baru = User(
            username=username,
            password=password,
            role=role
        )

        db.session.add(user_baru)

        db.session.commit()

        return redirect('/admin')

    return render_template('tambah_user.html')

# EDIT USER
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):

    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get(id)

    if request.method == 'POST':

        user.username = request.form['username']
        user.password = request.form['password']
        user.role = request.form['role']

        db.session.commit()

        return redirect('/admin')

    return render_template(
        'edit_user.html',
        user=user
    )



    # HAPUS USER
@app.route('/hapus_user/<int:id>')
def hapus_user(id):

    if session.get('role') != 'admin':
        return redirect('/')

    user = User.query.get(id)

    db.session.delete(user)

    db.session.commit()

    return redirect('/admin')

    db.session.delete(user)

    db.session.commit()

    return redirect('/admin')

# EXPORT EXCEL
@app.route('/export_excel')
def export_excel():

    # HANYA ADMIN
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

    nama_file = 'data_link.xlsx'

    df.to_excel(nama_file, index=False)

    return send_file(
        nama_file,
        as_attachment=True
    )

# SHINY


# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# MENJALANKAN FLASK
if __name__ == '__main__':

    with app.app_context():

        db.create_all()

        # CEK ADMIN
        cek_admin = User.query.filter_by(
            username='admin'
        ).first()

        if not cek_admin:

            admin = User(
                username='admin',
                password='admin123',
                role='admin'
            )

            db.session.add(admin)

            db.session.commit()

    app.run(debug=True)