from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
import requests
import json
import time
import datetime
import requests
from requests.structures import CaseInsensitiveDict

app = Flask(__name__)


def homepagef(searchjson):
    result = requests.post(
        'http://clip3.cs.nccu.edu.tw:9200/meta/_search', json=searchjson)
    result = result.json()  # result is a dictionary
    chart = requests.post(
        'http://clip3.cs.nccu.edu.tw:9200/chart/_search', json=searchjson)
    chart = chart.json()  # result is a dictionary

    if result['hits']['total']['value'] != 0:
        # print(result['hits']['hits'][0]['_source'])
        stockname = result['hits']['hits'][0]['_source']['nameZhTw']
        id = result['hits']['hits'][0]['_source']['symbolId']
        priceReference = result['hits']['hits'][0]['_source']['priceReference']
        priceHighLimit = result['hits']['hits'][0]['_source']['priceHighLimit']
        priceLowLimit = result['hits']['hits'][0]['_source']['priceLowLimit']
        industryZhTw = result['hits']['hits'][0]['_source']['industryZhTw']
    return stockname, id, priceReference, priceHighLimit, priceLowLimit, industryZhTw


# Index
@app.route('/')
def index():
    stockname1, id1, priceReference1, priceHighLimit1, priceLowLimit1, industryZhTw1 = homepagef(
        {"query": {"term": {"symbolId": {"value": 1101}}}})
    stockname2, id2, priceReference2, priceHighLimit2, priceLowLimit2, industryZhTw2 = homepagef(
        {"query": {"term": {"symbolId": {"value": 1234}}}})
    stockname3, id3, priceReference3, priceHighLimit3, priceLowLimit3, industryZhTw3 = homepagef(
        {"query": {"term": {"symbolId": {"value": 1203}}}})
    stockname4, id4, priceReference4, priceHighLimit4, priceLowLimit4, industryZhTw4 = homepagef(
        {"query": {"term": {"symbolId": {"value": 1201}}}})
    stockname5, id5, priceReference5, priceHighLimit5, priceLowLimit5, industryZhTw5 = homepagef(
        {"query": {"term": {"symbolId": {"value": 1301}}}})
    stockname6, id6, priceReference6, priceHighLimit6, priceLowLimit6, industryZhTw6 = homepagef(
        {"query": {"term": {"symbolId": {"value": 1218}}}})
    stockname = [stockname1, stockname2, stockname3,
                 stockname4, stockname5, stockname6]
    id = [id1, id2, id3, id4, id5, id6]
    priceReference = [priceReference1, priceReference2, priceReference3,
                      priceReference4, priceReference5, priceReference6]
    priceHighLimit = [priceHighLimit1, priceHighLimit2, priceHighLimit3,
                      priceHighLimit4, priceHighLimit5, priceHighLimit5, priceHighLimit6]
    priceLowLimit = [priceLowLimit1, priceLowLimit2, priceLowLimit3,
                     priceLowLimit4, priceLowLimit5, priceLowLimit6]
    industryZhTw = [industryZhTw1, industryZhTw2, industryZhTw3,
                    industryZhTw4, industryZhTw5, industryZhTw6]
    return render_template('homepage.html', stockname=stockname, id=id, priceReference=priceReference,
                           priceHighLimit=priceHighLimit, priceLowLimit=priceLowLimit, industryZhTw=industryZhTw)


# About
@app.route('/about')
def about():
    return render_template('about.html')

# Register Form Class


class RegisterForm(Form):
    username = StringField('Email (Username)', [
                           validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate() == False:
            error = 'Passwords do not match'
            return render_template('register.html', form=form, error=error)

        username = form.username.data
        password = form.password.data
        # Create cursor
        result = requests.post('http://stock-recommender-backend.herokuapp.com/signup/',
                               json={"email": username, "password": password})

        result = result.json()

        if "detail" in result:
            error = result["detail"]
            return render_template('register.html', form=form, error=error)

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password = request.form['password']

        result = requests.post('http://stock-recommender-backend.herokuapp.com/login/',
                               json={"username": username, "password": password})

        result = result.json()

        if "detail" in result:
            error = result["detail"]
            return render_template('login.html', error=error)

        session['access_token'] = result['access_token']
        session['logged_in'] = True
        session['username'] = username
        flash('You are now logged in', 'success')
        return redirect(url_for('index'))

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


@app.route('/stockpage/<string:stocknum>', methods=['GET'])
@is_logged_in
def stockpage(stocknum):
    print("page for ", stocknum)
    return render_template('stockpage.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        stock = request.form['Stock']
        searchjson = {"query": {"term": {"symbolId": {"value": stock}}}}
        # print(searchjson)
        result = requests.post(
            'http://clip3.cs.nccu.edu.tw:9200/meta/_search', json=searchjson)
        result = result.json()  # result is a dictionary
        chart = requests.post(
            'http://clip3.cs.nccu.edu.tw:9200/chart/_search?size=1000', json=searchjson)
        chart = chart.json()  # result is a dictionary
        # print(chart)
        if result['hits']['total']['value'] != 0:
            # print(result['hits']['hits'][0]['_source'])
            stockname = result['hits']['hits'][0]['_source']['nameZhTw']
            id = result['hits']['hits'][0]['_source']['symbolId']
            priceReference = result['hits']['hits'][0]['_source']['priceReference']
            priceHighLimit = result['hits']['hits'][0]['_source']['priceHighLimit']
            priceLowLimit = result['hits']['hits'][0]['_source']['priceLowLimit']
            industryZhTw = result['hits']['hits'][0]['_source']['industryZhTw']
            # return render_template('search.html', stockname = stockname)
            #id = result['hits']['hits'][0]['_source']['1101']
            return render_template('search.html', stockname=stockname, id=id, priceReference=priceReference,
                                   priceHighLimit=priceHighLimit, priceLowLimit=priceLowLimit, industryZhTw=industryZhTw)
        else:
            msg = 'NO STOCKS FOUND'
            return render_template('search.html', error=msg)

    return render_template('search.html')


@app.route('/playlist')
@is_logged_in
def playlist():
    # Create cursor

    access_token = session.get('access_token')

    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer "+access_token

    result = requests.get('http://stock-recommender-backend.herokuapp.com/user/likes/list' , headers = headers)

    result=result.json()

    return render_template('playlist.html', result=result['stocks'])


@app.route('/addtoPlaylist/<string:id>')
@is_logged_in
def addtoPlaylist(id):

        access_token = session.get('access_token')
        headers = CaseInsensitiveDict()

        headers["Authorization"] = "Bearer "+access_token

        result = requests.post('http://stock-recommender-backend.herokuapp.com/user/likes/'+id , headers = headers)

        flash('Add success', 'success')

        return redirect(url_for('search'))


@app.route('/removesong/<string:id>')
@is_logged_in
def removesong(id):
    # Create cursor
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM playlists WHERE recordsongID = %s", [id])
    mysql.connection.commit()

    # Close connection
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
    result = cur.execute(
        "SELECT * FROM users WHERE username = %s", [session['username']])
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
        cur.execute("UPDATE users SET name=%s, email=%s WHERE username=%s",
                    (name, email, session['username']))
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash('Your profile have been updated', 'success')
        return redirect(url_for('index'))
    return render_template('setting.html', form=form)


@app.route('/reccomend')
@is_logged_in
def reccomend():
    cur = mysql.connection.cursor()
    result = cur.execute(
        "WITH avgval AS  ( SELECT AVG(danceability) as avgdance, AVG(energy) as avgenergy, AVG(loudness) as avgloudness, AVG(speechiness) as avgspeech, avg(acousticness) as avgacoustic, avg(liveness) as avglive FROM playlists, song_records WHERE playlists.recordsongID = song_records.SongID AND playlists.user = %s ) SELECT * FROM song_records, avgval WHERE song_records.danceability between avgval.avgdance-0.2 and avgval.avgdance+0.2 and song_records.energy between avgval.avgenergy-0.2 and avgval.avgenergy+0.2 and song_records.loudness between avgval.avgloudness-0.2 and avgval.avgloudness+0.2 and song_records.speechiness between avgval.avgspeech-0.2 and avgval.avgspeech+0.2 and song_records.acousticness between avgval.avgacoustic-0.2 and avgval.avgacoustic+0.2 and song_records.liveness between avgval.avglive-0.2 and avgval.avglive+0.2 LIMIT 15", [session['username']])
    if result > 0:
        data = cur.fetchall()
        return render_template('reccomend.html', songs=data)
    else:
        msg = 'NO SONGS FOUND'
        return render_template('reccomend.html', msg=msg)
    return render_template('reccomend.html')


@app.route("/chartdata/<string:stocknum>", methods=['GET'])  # 函式的裝飾()
def chartdata(stocknum):
    print(stocknum)
    searchjson = {"query": {"term": {"symbolId": {"value": stocknum}}}}
    # print(searchjson)
    chart = requests.post(
        'http://clip3.cs.nccu.edu.tw:9200/chart/_search?size=1000', json=searchjson)
    chart = chart.json()  # result is a dictionary
    # print(chart)
    mydata = []
    for data in chart['hits']['hits']:
        # print(data)
        s = data['_source']['time']
        t = time.mktime(datetime.datetime.strptime(
            s, "%Y-%m-%dT%H:%M:%S.000+08:00").timetuple())*1000 + 28800000000
        print(t)
        price = data['_source']['close']
        # print(price)
        arr = []
        arr.append(t)
        arr.append(price)
        mydata.append(arr)
    # print(mydata)
    return json.dumps(mydata)

@app.route('/delete/<string:id>')
@is_logged_in
def delete(id):

        access_token = session.get('access_token')
        headers = CaseInsensitiveDict()

        headers["Authorization"] = "Bearer "+access_token

        result = requests.delete('http://stock-recommender-backend.herokuapp.com/user/dislike/'+id , headers = headers)

        flash('Delete success', 'success')

        return redirect(url_for('playlist'))


@app.route('/show', methods=['GET', 'POST']) # 我的最愛裡印出圖表
def show():

        stock = request.args.get('id')
        searchjson = {"query": {"term": {"symbolId": {"value": stock}}}}
        # print(searchjson)
        result = requests.post(
            'http://clip3.cs.nccu.edu.tw:9200/meta/_search', json=searchjson)
        result = result.json()  # result is a dictionary
        chart = requests.post(
            'http://clip3.cs.nccu.edu.tw:9200/chart/_search?size=1000', json=searchjson)
        chart = chart.json()  # result is a dictionary
        # print(chart)
        if result['hits']['total']['value'] != 0:
            # print(result['hits']['hits'][0]['_source'])
            stockname = result['hits']['hits'][0]['_source']['nameZhTw']
            id = result['hits']['hits'][0]['_source']['symbolId']
            priceReference = result['hits']['hits'][0]['_source']['priceReference']
            priceHighLimit = result['hits']['hits'][0]['_source']['priceHighLimit']
            priceLowLimit = result['hits']['hits'][0]['_source']['priceLowLimit']
            industryZhTw = result['hits']['hits'][0]['_source']['industryZhTw']
            # return render_template('search.html', stockname = stockname)
            #id = result['hits']['hits'][0]['_source']['1101']
            return render_template('search.html', stockname=stockname, id=id, priceReference=priceReference,
                                   priceHighLimit=priceHighLimit, priceLowLimit=priceLowLimit, industryZhTw=industryZhTw)
        else:
            msg = 'NO STOCKS FOUND'
            return render_template('search.html', error=msg)

        return render_template('search.html')


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
