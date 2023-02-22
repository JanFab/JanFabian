from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from send_email import send_email
from sqlalchemy.sql import func

import yfinance as yf

app=Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/height_collector'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wvbuzieydcngrr:6ff8a9a1c7a2187ec1f0f897e064956b6509627318514f308817b1a3433bb074@ec2-18-215-111-67.compute-1.amazonaws.com:5432/d2uj132js0farb?sslmode=require'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kbqlahjvzmlizu:dd8dafab365744375f74fb7f47e6d770afe7ce684ae1e856d307463bb46c8e8a@ec2-54-163-254-204.compute-1.amazonaws.com:5432/d7911aqu6f6oj5?sslmode=require'
db=SQLAlchemy(app)

class Data(db.Model):
    __tablename__="data"
    id=db.Column(db.Integer, primary_key=True)
    email_=db.Column(db.String(120), unique=True)
    height_=db.Column(db.Integer)
    
    def __init__(self, email_, height_):
        self.email_ = email_
        self.height_ = height_


@app.route('/python/')
def python():
    from pandas_datareader import data as pdr
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.date.today() - datetime.timedelta(days=90)
    end = datetime.date.today()
    yf.pdr_override()
    df = pdr.get_data_yahoo("SPY", start, end)

    date_decrease = df.index[df.Close > df.Open]
    date_increase = df.index[df.Close < df.Open]

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]
    df["Middle"] = (df.Open+df.Close)/2
    df["Height"] = abs(df.Open-df.Close)

    p = figure(x_axis_type='datetime', width=1000,
               height=300, sizing_mode="scale_width")
    p.title.text = "Atlassian, cena akcií v dňoch v USD"
    p.grid.grid_line_alpha = 0.3

    hours_12 = 12*60*60*1000

    p.segment(df.index, df.High, df.index, df.Low, color="black")
    p.rect(df.index[df.Status == "Increase"], df.Middle[df.Status == "Increase"], hours_12, df.Height[df.Status == "Increase"],
           fill_color="green", line_color="black")
    p.rect(df.index[df.Status == "Decrease"], df.Middle[df.Status == "Decrease"], hours_12, df.Height[df.Status == "Decrease"],
           fill_color="red", line_color="black")

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    # cdn_css = CDN.css_files[0]

    return render_template("python.html",
    script1 = script1,
    div1 = div1,
    # cdn_css = cdn_css,
    cdn_js = cdn_js)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/hobbies/')
def hobbies():
    return render_template("hobbies.html")

@app.route("/school/")
def school():
    return render_template("school.html")


@app.route("/success/", methods=['POST'])
def success():
    if request.method == 'POST':
        email=request.form["email_name"]
        height=request.form["height_name"]
        
        if db.session.query(Data).filter(Data.email_==email).count() == 0:
            data=Data(email, height)
            db.session.add(data)
            db.session.commit()
            average_height = db.session.query(func.avg(Data.height_)).scalar()
            average_height = round(average_height)
            count = db.session.query(Data.height_).count()
            send_email(email, height, average_height, count)
            return render_template("success.html")
        else:
            return render_template('python.html', text="Seems like we've got something from that email address already!")

if __name__ == "__main__":
    # app.debug=True
    app.run(debug=True)