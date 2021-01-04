from flask import Flask
from flask import render_template

app = Flask(__name__)

UI_IP='127.0.0.1'
UI_PORT=8081
UI_BASE_URL='http://localhost'


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    global UI_PORT
    global UI_BASE_URL

    if UI_PORT == 80 or UI_PORT == 443:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template("index.html", url=my_url)


@app.route('/air-temperature')
def air_temperature():
    page_name ='Air Temperature'
    page_description ='this page contains data about air temperature in celsius degree'
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]

    if UI_PORT == 80 or UI_PORT == 443:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
 
    return render_template("chart.html", page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')

@app.route('/air-humidity')
def air_umidity():
    page_name ='Air Humidity'
    page_description ='this page contains data about air humidity in percentage'
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    
    if UI_PORT == 80 or UI_PORT == 443:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template("chart.html", page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')
 

@app.route('/light')
def light():
    page_name ='Light'
    page_description ='this page contains data about external ligth in percentage'
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    if UI_PORT == 80 or UI_PORT == 443:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template("chart.html", page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')
 

@app.route('/soil-moisture')
def soil_moisture():
    page_name ='Soil Moisture'
    page_description ='this page contains data about soil moisture'
    labels = ['January','February','March','April','May','June','July','August']
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    if UI_PORT == 80 or UI_PORT == 443:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template("chart.html", page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')
 

@app.route('/watering-sys-status')
def watering_sys():
    page_name ='Watering System'
    page_description ='this page contains data about watering system'
    labels = ["January","February","March","April","May","June","July","August"]
    values = [10,9,8,7,6,4,7,8]
    colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
    if UI_PORT == 80 or UI_PORT == 443:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template("chart.html", page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='bar')
 

app.run(host=UI_IP, port=UI_PORT)