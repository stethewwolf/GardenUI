from flask import Flask
from flask import render_template, request
from flask_mqtt import Mqtt
import sqlite3, json, datetime

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '127.0.0.1'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
mqtt = Mqtt(app)
mqtt.subscribe('garden/#')

UI_IP='127.0.0.1'
UI_PORT=8180
UI_BASE_URL='http://garden.stobi.local/'
IGNORE_PORTS=True

last_read_values = {
    'air_temperature' : 0,
    'air_humidity' : 0,
    'light' : 0,
    'soil_moisture' : 0,
    'watering_sys_stat' : 'unknow'
}
    
DB_FILE="garden-ui.sqlite"
DB_CREATE_TABLE_READ_VALUES = 'CREATE TABLE IF NOT EXISTS `read_values` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `value` TEXT, `datetime` TEXT, `device_id` INTEGER NOT NULL, `value_type_id` INTEGER NOT NULL)'
DB_CREATE_TABLE_DEVICES = 'CREATE TABLE IF NOT EXISTS `devices` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT NOT NULL UNIQUE, `weight` FLOAT DEFAULT 1)'
DB_CREATE_TABLE_VALUE_TYPES = 'CREATE TABLE IF NOT EXISTS `value_types` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT NOT NULL UNIQUE)'

DB_INSERT_VALUE_TYPE = 'INSERT OR IGNORE INTO `value_types` (`name`) VALUES (?);'
DB_INSERT_DEVICE = 'INSERT OR IGNORE INTO `devices` (`name`) VALUES (?);'
DB_INSERT_READ_VALUE = 'INSERT INTO `read_values`\
 (`value`,`datetime`,`device_id`,`value_type_id`) VALUES (?,?,?,?);'

DB_GET_DEVICE_BY_NAME = 'SELECT id,name,weight from `devices`\
 WHERE name == ?;'

DB_GET_VALUE_TYPE_BY_NAME = 'SELECT id,name from `value_types`\
 WHERE name == ?;'

DB_GET_VALUE = 'SELECT value,datetime,device_id from `read_values`\
 WHERE datetime >= ? AND datetime<= ? AND value_type_id == ?;'

DB_GET_VALUE_BY_DEVICE = 'SELECT value,datetime,device_id from `read_values`\
 WHERE datetime >= ? AND datetime<= ? AND device_id==? AND value_type_id == ?;'

INDEX_TEMPALTE="index.html"
CHART_TEMPALTE="chart.html"

def create_db():
    msg = "empty"
    try:  
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()  
        cur.execute(DB_CREATE_TABLE_READ_VALUES)
        cur.execute(DB_CREATE_TABLE_VALUE_TYPES)
        cur.execute(DB_CREATE_TABLE_DEVICES)
        con.commit()  
        msg = "db created"  
    except Exception:  
        con.rollback()  
        msg = "We can not create the db"  
    finally:
        con.close()
        print(msg)

def insert_device(device_name):
    msg = "empty"
    try:  
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()  
        cur.execute(DB_INSERT_DEVICE,[device_name])
        con.commit()  
        msg = "added {} to devices".format(device_name)  
    except Exception:  
        con.rollback()  
        msg = "We can not add {} to devices".format(device_name)  
    finally:
        con.close()
        print(msg)

    return get_device_id(device_name)

def insert_value_type(value_type):
    msg = "empty"
    try:  
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()  
        cur.execute(DB_INSERT_VALUE_TYPE,[value_type])
        con.commit()  
        msg = "added {} to value_types".format(value_type)  
    except Exception:  
        con.rollback()  
        msg = "We can not add {} to value_types".format(value_type)  
    finally:
        con.close()
        print(msg)
    
    return get_value_type_id(value_type)

def get_device_id(device_name):
    msg = "empty"
    device_id = None
    try:  
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()  
        cur.execute(DB_GET_DEVICE_BY_NAME,[device_name])
        row = cur.fetchone()

        if row is not None:
            device_id = int(row[0])

        msg = "found id {} for device {}".format(device_id,device_name)  
    except Exception:  
        msg = "Id for device {} not found".format(device_name)  
        device_id = None
    finally:
        con.close()
        print(msg)

    return device_id

def get_value_type_id(value_type):
    msg = "empty"
    value_id = None
    try:  
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()  
        cur.execute(DB_GET_VALUE_TYPE_BY_NAME,[value_type])
        row = cur.fetchone()

        if row is not None:
            value_id = int(row[0])
            msg = "found id {} for value_type {}".format(id,value_type)  
        else:
            msg = "not found  id for value_type {}".format(value_type)  
    except Exception:  
        msg = "Id for value_type {} lead to exception".format(value_type)  
        value_id = -1
    finally:
        con.close()
        print(msg)
    return value_id

def add_value(value, value_type, device):
    msg = "empty"
    device_id = get_device_id(device)

    if device_id is None:
        device_id = insert_device(device)

    value_id = get_value_type_id(value_type)

    if value_id is None:
        value_id = insert_value_type(value_type)

    read_time = datetime.datetime.now()

    try:  
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()  
        cur.execute(DB_INSERT_READ_VALUE,[value,read_time,device_id,value_id])
        con.commit()  
        msg = "added value {} type {} for device {} at {}".format(value,value_type,device,read_time)  
    except Exception:  
        con.rollback()  
        msg = "failed to add value {} type {} for device {} at {}".format(value,value_type,device,read_time)  
    finally:
        con.close()
        print(msg)

def get_values(value_type, device=None, start_datetime=datetime.datetime.now()-datetime.timedelta(hours=24),end_datetime=datetime.datetime.now()):
    msg = "empty"
    ret_values = []

    value_type_id = get_value_type_id(value_type)

    device_id = None
    if device is not None:
        device_id = get_device_id(device)

    if value_type_id is not None:   
        try:  
            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()  

            if device_id is None:
                cur.execute(DB_GET_VALUE,[start_datetime,end_datetime,value_type_id])
            else:
                cur.execute(DB_GET_VALUE,[start_datetime,end_datetime,value_type_id,device_id])

            ret_values = [{'value':row[0],'time':datetime.datetime.strptime(row[1],"%Y-%m-%d %H:%M:%S.%f"),'device':device} for row in cur.fetchall()]

            msg = "found value_type"  
        except Exception:  
            msg = "Id for value_type {} lead to exception".format(value_type)  
        finally:
            con.close()
            print(msg)
    
    print("raw values for {} : {}".format(value_type,ret_values))
    return ret_values

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    global UI_PORT
    global UI_BASE_URL
    global last_read_values
    print(last_read_values)

    if UI_PORT == 80 or UI_PORT == 443 or IGNORE_PORTS:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template(INDEX_TEMPALTE, url=my_url, **last_read_values)

@app.route('/air-temperature')
def air_temperature():
    page_name ='Air Temperature'
    page_description ='this page contains data about air temperature in celsius degree'
    data = get_values('air/temperature')
    labels = [ str(d['time']) for d in data ]
    values = [ float(d['value']) for d in data ]

    print("handled values {}".format(values)) 

    if UI_PORT == 80 or UI_PORT == 443 or IGNORE_PORTS:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)

    return render_template(CHART_TEMPALTE, page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')

@app.route('/air-humidity')
def air_umidity():
    page_name ='Air Humidity'
    page_description ='this page contains data about air humidity in percentage'
    data = get_values('air/humidity')
    labels = [ str(d['time']) for d in data ]
    values = [ float(d['value']) for d in data ]
    
    if UI_PORT == 80 or UI_PORT == 443 or IGNORE_PORTS:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    
    return render_template(CHART_TEMPALTE, page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')

@app.route('/light')
def light():
    page_name ='Light'
    page_description ='this page contains data about external ligth in percentage'
    data = get_values('light')
    labels = [ str(d['time']) for d in data ]
    values = [ float(d['value']) for d in data ]

    if UI_PORT == 80 or UI_PORT == 443 or IGNORE_PORTS:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template(CHART_TEMPALTE, page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')

@app.route('/soil-moisture')
def soil_moisture():
    page_name ='Soil Moisture'
    page_description ='this page contains data about soil moisture'
    data = get_values('soil/moisture')
    labels = [ str(d['time']) for d in data ]
    values = [ float(d['value']) for d in data ]
 
    if UI_PORT == 80 or UI_PORT == 443 or IGNORE_PORTS:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template(CHART_TEMPALTE, page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='line')

@app.route('/watering-sys-status')
def watering_sys():
    page_name ='Watering System'
    page_description ='this page contains data about watering system'
    data = get_values('watering_system/status')
    labels = [ str(d['time']) for d in data ]
    values = []
    for d in data:
        if 'on' in d['value']:
            values.append(1)
        else:
            values.append(0)

    if UI_PORT == 80 or UI_PORT == 443 or IGNORE_PORTS:
        my_url=UI_BASE_URL
    else:
        my_url='{}:{}/'.format(UI_BASE_URL, UI_PORT)
    return render_template(CHART_TEMPALTE, page_name=page_name, page_description=page_description, url=my_url, labels=labels, values=values, graph_type='bar')

@app.route("/cmd",methods = ["POST"])
def cmd_handler():  
    cmd = request.form["cmd"] 
    message ={
        'id' : 'garden-ui',
        'tag' : 'cmd',
        'value' : cmd
    }
    mqtt.publish('garden/cmd', json.dumps(message))
    return "command sent"

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global last_read_values
    print("received message : {}".format(message))
    topic=message.topic
    payload=json.loads(message.payload.decode())

    add_value(payload['value'],payload['tag'],payload['id'])

    if 'air/temperature' in topic:
        last_read_values['air_temperature'] = payload['value']
    elif 'air/humidity' in topic:
        last_read_values['air_humidity'] = payload['value']
    elif 'soil_moisture' in topic:
        last_read_values['soil_moisture'] = payload['value']
    elif 'light' in topic:
        last_read_values['light'] = payload['value']
    elif 'water' in topic:
        last_read_values['watering_sys_stat'] = payload['value']

create_db()
app.run(host=UI_IP, port=UI_PORT)