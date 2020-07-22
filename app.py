from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'us-cdbr-east-02.cleardb.com'
app.config['MYSQL_USER'] = 'b9b893912cc97e'
app.config['MYSQL_PASSWORD'] = '5f6c2324'
app.config['MYSQL_DB'] = 'heroku_d1fcf268b8cf02f'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


# Index
@app.route('/' ,methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        song = request.form['Song']
        return redirect(url_for('/quicksearch/'+song))
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result >0:
            error = 'Username has already been registered.'
            return render_template('register.html', form=form,error=error)
        cur.close();
        cur = mysql.connection.cursor()
        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/quicksearch/<string:song>', methods=['GET', 'POST'])
@is_logged_in
def quicksearch(song):
    if request.method == 'POST':
        song = request.form['Song']
        cur = mysql.connection.cursor()
        sql='Select * from song_records where Performer like %s union Select distinct * from song_records where Song like %s union Select distinct * from song_records where spotify_track_album like %s'
        args=[song+'%',song+'%',song+'%']
        result = cur.execute(sql,args)
        if result > 0:
            data = cur.fetchall()
            return render_template('search.html', songs = data)
        else:
            msg = 'NO SONGS FOUND'
            return render_template('search.html', msg = msg)

    cur = mysql.connection.cursor()
    sql='Select * from song_records where Performer like %s union Select distinct * from song_records where Song like %s union Select distinct * from song_records where spotify_track_album like %s'
    args=[song+'%',song+'%',song+'%']
    result = cur.execute(sql,args)
    if result > 0:
        data = cur.fetchall()
        return render_template('search.html', songs = data)
    else:
        msg = 'NO SONGS FOUND'
        return render_template('search.html', msg = msg)

@app.route('/search', methods=['GET', 'POST'])
@is_logged_in
def search():
    if request.method == 'POST':
        song = request.form['Song']
        cur = mysql.connection.cursor()
        sql='Select * from song_records where Performer like %s union Select distinct * from song_records where Song like %s union Select distinct * from song_records where spotify_track_album like %s'
        args=[song+'%',song+'%',song+'%']
        result = cur.execute(sql,args)
        if result > 0:
            data = cur.fetchall()
            return render_template('search.html', songs = data)
        else:
            msg = 'NO SONGS FOUND'
            return render_template('search.html', msg = msg)
    return render_template('search.html')

@app.route('/playlist')
@is_logged_in
def playlist():
    # Create cursor
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM playlists,song_records WHERE user = %s AND song_records.songID = playlists.recordsongID", [session['username']])
    mysongs = cur.fetchall()

    if result > 0:
        return render_template('playlist.html', mysongs=mysongs)
    else:
        msg = 'No Songs Yet'
        return render_template('playlist.html', msg=msg)
    # Close connection
    cur.close()

@app.route('/addtoPlaylist/<string:song>')
@is_logged_in
def addtoPlaylist(song):

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM playlists WHERE recordsongID = %s", [song])
    if result > 0:
        flash('Song Already in your playlist', 'danger')
        return redirect(url_for('search'))
        cur.close()
    else:

        cur1 = mysql.connection.cursor()
        cur1.execute("INSERT INTO playlists(recordsongID, user) VALUES(%s, %s)", (song, [session['username']]))
        mysql.connection.commit()
        cur1.close()
        cur.close()
        flash('Song Added to your playlist', 'success')
        return redirect(url_for('search'))

@app.route('/removesong/<string:id>')
@is_logged_in
def removesong(id):
    # Create cursor
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM playlists WHERE recordsongID = %s", [id])
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Song Removed From Playlist', 'success')
    return redirect(url_for('playlist'))

class SettingForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
@app.route('/setting', methods=['GET', 'POST'])
@is_logged_in
def setting():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users WHERE username = %s", [session['username']])
    detail = cur.fetchone()
    cur.close()
    form = SettingForm(request.form)
    form.name.data = detail['name']
    form.email.data = detail['email']
    if request.method == 'POST' and form.validate():
        print('123')
        name = request.form['name']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute ("UPDATE users SET name=%s, email=%s WHERE username=%s",(name,email,session['username']))
        mysql.connection.commit()
        #Close connection
        cur.close()
        flash('Your profile have been updated', 'success')
        return redirect(url_for('index'))
    return render_template('setting.html', form=form)

@app.route('/reccomend')
@is_logged_in
def reccomend():
    cur = mysql.connection.cursor()
    result = cur.execute("WITH avgval AS  ( SELECT AVG(danceability) as avgdance, AVG(energy) as avgenergy, AVG(loudness) as avgloudness, AVG(speechiness) as avgspeech, avg(acousticness) as avgacoustic, avg(liveness) as avglive FROM playlists, song_records WHERE playlists.recordsongID = song_records.SongID AND playlists.user = %s ) SELECT * FROM song_records, avgval WHERE song_records.danceability between avgval.avgdance-0.2 and avgval.avgdance+0.2 and song_records.energy between avgval.avgenergy-0.2 and avgval.avgenergy+0.2 and song_records.loudness between avgval.avgloudness-0.2 and avgval.avgloudness+0.2 and song_records.speechiness between avgval.avgspeech-0.2 and avgval.avgspeech+0.2 and song_records.acousticness between avgval.avgacoustic-0.2 and avgval.avgacoustic+0.2 and song_records.liveness between avgval.avglive-0.2 and avgval.avglive+0.2 LIMIT 15", [session['username']])
    if result > 0:
        data = cur.fetchall()
        return render_template('reccomend.html', songs = data)
    else:
        msg = 'NO SONGS FOUND'
        return render_template('reccomend.html', msg = msg)
    return render_template('reccomend.html')



if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
