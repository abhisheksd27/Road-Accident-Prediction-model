import flask
import os
from flask import render_template, request, jsonify, session
from flask_session import Session
import pandas as pd
import pickle
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier
import requests, json
from flask_mysqldb import MySQL
import MySQLdb.cursors
from twilio.rest import Client
import geocoder
import json
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)


# The Twilio phone number
from_number = os.getenv('TWILIO_FROM_NUMBER')

app = flask.Flask(__name__, template_folder='Templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#code for connection
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)
@app.route('/')

#User Login   
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return(flask.render_template('login.html'))
    if flask.request.method == 'POST':
        msg=''
        if request.method == 'POST':
            phone    = request.form['phone']
            password = request.form['password']

            con = mysql.connect
            con.autocommit(True)
            cursor = con.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM userdetails WHERE phonennumber = % s and password = %s', (phone, password,))
            result = cursor.fetchone()
           
            
        if result:
            #return render_template('main.html', usernameins=username)
            msg = "1"
            session["userid"]   = result["userid"]
            session["email"]   = result["email"]
            session["name"]   = result["username"]
            session["userphone"] = '+91'+result["phonennumber"]
        else:
           msg = "0"
    return msg
       
@app.route('/registeruser', methods=['GET', 'POST'])
def registeruser():
    if flask.request.method == 'GET':
        return(flask.render_template('register.html'))
    if flask.request.method == 'POST':
        msg=''
        #applying empty validation
        if request.method == 'POST':
            
            #passing HTML form data into python variable
            username    = request.form['username']
            role        = request.form['role']
            email       = request.form['email']
            phone       = request.form['phone']
            purpose     = request.form['purpose']
            dob         = request.form['dob']
            bloodgroup  = request.form['bloodgroup']
            password    = request.form['password']
            
            #creating variable for connection
            con = mysql.connect
            con.autocommit(True)
            cursor = con.cursor(MySQLdb.cursors.DictCursor)
            #query to check given data is present in database or no
            cursor.execute('SELECT * FROM userdetails WHERE phonennumber = %s', (phone,))
            #fetching data from MySQL
            result = cursor.fetchone()
            
        if result:
            msg = '0'#'User Details Already Exists! Please Login.'
            #return render_template('register.html', msg=msg)
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO userdetails VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, NULL)', (username, role, phone, dob, bloodgroup, email, purpose, password,))
            mysql.connect.commit()
            #displaying message
            msg = '1'#'Registeration completed! Please login.'
            #return render_template('login.html', msg=msg)  
    return msg
        
@app.route('/main', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        """if not session.get("userid"):
            return(flask.render_template('login.html'))
        elif session.get("userid") is None:
            return(flask.render_template('login.html'))
        else:"""
        return(flask.render_template('main.html'))
    
    
#Prediction
model = pickle.load(open('Model/accidentSeverityPredictor.pkl', 'rb'))

@app.route('/anotherlocation', methods=['GET', 'POST'])
def another():
    if flask.request.method == 'POST':    
        roveg1    = request.form['roveh']
        roadsurf1 = request.form['roadsurf']
        light1    = request.form['light']
        weather1  = request.form['weather']
        cclass1   = request.form['cclass']
        typeveg1  = request.form['typeveh']
        place     = request.form['place']
        userid    = session.get("userid")

        input_variables = pd.DataFrame([[roveg1, roadsurf1, light1, weather1, cclass1,  typeveg1]],
                                       columns=['1st Road Class', 'Road Surface','Lighting Conditions','Weather Conditions','Casualty Class','Type of Vehicle'], dtype=float)
        prediction = model.predict(input_variables)[0]
        
        if prediction == 1:
            prediction="Serious Accident"
        else:
            prediction="Slight Accident"
            
        roveg2 = roadsurf2 = light2 = weather2 = cclass2 = typeveg2 = ''
        
        if int(roveg1) == 0:
           roveg2 = 'A - Type'
        elif int(roveg1) == 1:
           roveg2 = 'A(M) - Type'
        elif int(roveg1) == 2:
           roveg2 = 'B - Type'
        elif int(roveg1) == 3:
           roveg2 = 'Motor way - Type'
        elif int(roveg1) == 4:
           roveg2 = 'Unclassified - Type'
              
        if int(roadsurf1) == 0:
           roadsurf2 = 'Dry'
        elif int(roadsurf1) == 1:
           roadsurf2 = 'Frost'
        elif int(roadsurf1) == 2:
           roadsurf2 = 'Flood'
        elif int(roadsurf1) == 3:
           roadsurf2 = 'Snow'
        elif int(roadsurf1) == 4:
           roadsurf2 = 'Wet'          
              
        if int(light1) == 0:
            light2 = 'No street lighting'
        elif int(light1) == 1:
            light2 = 'Street lighting unknown'
        elif int(light1) == 2:
            light2 = 'Street lights present and lit'
        elif int(light1) == 3:
            light2 = 'Darkness'
             
        if int(weather1) == 0:
            weather2 = 'Fine without high winds'
        elif int(weather1) == 1:
            weather2 = 'Fog or mist – if hazardn'
        #elif weather == 2:
           # weather1 = 'Street lights present and lit'
        elif int(weather1) == 3:
            weather2 = 'Other'
        elif int(weather1) == 4:
            weather2 = 'Raining without high winds'
        elif int(weather1) == 5:
            weather2 = 'Raining with high winds'
        elif int(weather1) == 6:
            weather2 = 'Snowing without high winds'
        elif int(weather1) == 7:
            weather2 = 'Snowing with high winds'
        elif int(weather1) == 8:
            weather2 = 'Unknown'
             
        if int(cclass1) == 0:
            cclass2 = 'Driver'
        elif int(cclass1) == 1:
            cclass2 = 'Passenger'
        elif int(cclass1) == 2:
            cclass2 = 'Pedestrian'
              
        
        if int(typeveg1) == 0:
            typeveg2 = 'Agri vehicle'
        elif int(typeveg1) == 1:
            typeveg2 = 'Bus'
        elif int(typeveg1) == 2:
            typeveg2 = 'Car'
        elif int(typeveg1) == 3:
            typeveg2 = 'Goods Vehicle'
        elif int(typeveg1) == 4:
            typeveg2 = 'Motorcycle'
        elif int(typeveg1) == 5:
            typeveg2 = 'Pedal cycle'
        elif int(typeveg1) == 6:
            typeveg2 = 'Other vehicle'
        
        #store in db
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO accidentdetails VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s)", (roveg2, roadsurf2, light2, weather2, cclass2,  typeveg2, prediction, userid, place))
        refid = cursor.lastrowid
        mysql.connect.commit()
        
        pred = {"prediction":prediction, "refid":refid}
    return jsonify(pred)

@app.route('/desitinationfound', methods=['GET', 'POST'])
def destination():
    if flask.request.method == 'POST':    
        predtype  = request.form['predtype']
        src       = request.form['src']
        dest1     = request.form['dest']
        src_long  = request.form['longtitude']
        src_lat   = request.form['latitude']
        roveg     = int(request.form['liveroad'])
        typeveg   = int(request.form['livevehicle'])
        cclass    = int(request.form['livecasuality'])
        
        return_data = []
        
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM indian_cities_database WHERE city = %s', (dest1, ))
        result = cursor.fetchone();
        
        if(predtype != "current"):
            cursor.execute('SELECT * FROM indian_cities_database WHERE city = %s', (src, ))
            from_result = cursor.fetchone();
            if (from_result is not None):
                src_long =  from_result["longt"]
                src_lat = from_result["lat"]
        
    
        if(result is None):
            src_data =  getpred(src_long, src_lat, roveg, typeveg, cclass)
            return_data.append(src_data)
        else:
            dest_long  = result["longt"]
            dest_lat   = result["lat"]
            dest_state = result["state"]
            
            
            cursor.execute('SELECT * FROM indian_cities_database WHERE longt >= %s AND longt <= %s  AND state = %s LIMIT 4' , (src_long, dest_long,  dest_state,))
            result1 = cursor.fetchall();
            
            #print(result1)
            
            src_data =  getpred(src_long, src_lat, roveg, typeveg, cclass)
            return_data.append(src_data)
            
            if len(result1) >= 1:
               for i in range(len(result1)):
                   dest_data =  getpred(result1[i]["longt"], result1[i]["lat"], roveg, typeveg, cclass)
                   return_data.append(dest_data)
            else:
                dest_data =  getpred(dest_long, dest_lat, roveg, typeveg, cclass)
                return_data.append(dest_data)
            
            to_number = session.get("userphone")
            location = geocoder.ip('me')
            curloc = location.city
            
            loc_exists = loc_exists = any(item['curlocation'] == curloc for item in return_data if item.get('prediction', '') == 'Serious Accident')
            serious_accidents_locations = ", ".join(item['curlocation'] for item in return_data if item['prediction'] == 'Serious Accident')

            if loc_exists == True:
                # The message you want to send
                message = 'Message From Highway authority: Your current Location : '+curloc+' is deteced as Acciental zone. Take care while you driving.'
                if serious_accidents_locations is not None:
                    message += 'Also be carefull while driving in the : '+serious_accidents_locations+'. That are also detected as accidental zones.'
                # Send the SMS
                message = client.messages.create(
                    body=message,
                    from_=from_number,
                    to=to_number
                )
            
    return jsonify(return_data)


@app.route('/detectlive', methods=['GET', 'POST'])
def detect():
    if flask.request.method == 'POST':
       longtitude       = request.form['longitude']
       latitude         = request.form['latitude']
       roveg            = int(request.form['liveroad'])
       typeveg          = int(request.form['livevehicle'])
       cclass           = int(request.form['livecasuality'])
       
       pred = getpred(longtitude, latitude, roveg, typeveg, cclass)
       current_loc_accid(latitude, longtitude, roveg, typeveg, cclass)
    return jsonify(pred)

def getpred(longtitude, latitude, roveg, typeveg, cclass):
    
  
    accesskey = ""
    base_url = ""
    full_url = base_url+"access_key="+accesskey+"&query="+latitude+","+longtitude
    response = requests.get(full_url) 
    x = response.json()
    #print(x)
    
    roadsurf        = "0"
    light           = ""
    weather         = ""
    basicroadsurf  = x['current']['weather_code']
    wind_speed     = x['current']['wind_speed']
    is_day         =  x['current']['is_day']
    
    if basicroadsurf in [389, 353, 176, 302, 299, 296, 386, 284, 281, 266, 263]:
        roadsurf = 4  #Wet
        if wind_speed > 24:
            weather = 5  #Raining with high winds
        else:
            weather = 4  #Raining without high winds
    elif basicroadsurf in [143, 179, 182, 185, 248, 260, 395, 338, 335, 260]:
        roadsurf = 1  #Frost
        weather = 1  #Fog or mist – if hazard
    elif basicroadsurf in [359, 356, 308, 305, 320, 314, 311, 293, 317]:
        roadsurf = 2  #Flood
    elif basicroadsurf in [200, 227, 230, 263, 392, 377, 374, 371, 368, 365, 362, 350, 332, 329, 326, 323]:
        roadsurf = 3  #Snow
        if wind_speed > 24:
            weather = 7  #Snow with high winds
        else:
            weather = 6  #Snow without high winds
    else:
        roadsurf = 0  #Dry
        if wind_speed > 24:
            weather = 2  #Fine with high winds
        else:
            weather = 0  #Fine without high winds
            
    
    if is_day == "no":
        light = 3
    else:
        light = 0
 
    input_variables = pd.DataFrame([[roveg, roadsurf, light, weather, cclass,  typeveg]],
                                  columns=['1st Road Class', 'Road Surface','Lighting Conditions','Weather Conditions','Casualty Class','Type of Vehicle'], dtype=float)
    prediction = model.predict(input_variables)[0]
           
   
    if prediction == 1:
       prediction="Serious Accident"
    else:
       prediction="Slight Accident"
    roveg1 = roadsurf1 = light1 = weather1 = cclass1 = typeveg1 = ''
    if roveg == 0:
       roveg1 = 'A - Type'
    elif roveg == 1:
       roveg1 = 'A(M) - Type'
    elif roveg == 2:
       roveg1 = 'B - Type'
    elif roveg == 3:
       roveg1 = 'Motor way - Type'
    elif roveg == 4:
       roveg1 = 'Unclassified - Type'
          
    if roadsurf == 0:
       roadsurf1 = 'Dry'
    elif roadsurf == 1:
       roadsurf1 = 'Frost'
    elif roadsurf == 2:
       roadsurf1 = 'Flood'
    elif roadsurf == 3:
       roadsurf1 = 'Snow'
    elif roadsurf == 4:
       roadsurf1 = 'Wet'
          
          
    if light == 0:
        light1 = 'No street lighting'
    elif light == 1:
        light1 = 'Street lighting unknown'
    elif light == 2:
        light1 = 'Street lights present and lit'
    elif light == 3:
        light1 = 'Darkness'
         
    if weather == 0:
        weather1 = 'Fine without high winds'
    elif weather == 1:
        weather1 = 'Fog or mist – if hazardn'
    #elif weather == 2:
       # weather1 = 'Street lights present and lit'
    elif weather == 3:
        weather1 = 'Other'
    elif weather == 4:
        weather1 = 'Raining without high winds'
    elif weather == 5:
        weather1 = 'Raining with high winds'
    elif weather == 6:
        weather1 = 'Snowing without high winds'
    elif weather == 7:
        weather1 = 'Snowing with high winds'
    elif weather == 8:
        weather1 = 'Unknown'
         
    if cclass == 0:
        cclass1 = 'Driver'
    elif cclass == 1:
        cclass1 = 'Passenger'
    elif cclass == 2:
        cclass1 = 'Pedestrian'
          
    
    if typeveg == 0:
        typeveg1 = 'Agri vehicle'
    elif typeveg == 1:
        typeveg1 = 'Bus'
    elif typeveg == 2:
        typeveg1 = 'Car'
    elif typeveg == 3:
        typeveg1 = 'Goods Vehicle'
    elif typeveg == 4:
        typeveg1 = 'Motorcycle'
    elif typeveg == 5:
        typeveg1 = 'Pedal cycle'
    elif typeveg == 6:
        typeveg1 = 'Other vehicle'
    
    place  = x["location"]["name"]
    userid = session.get("userid")
    
    #store in db
    
    con = mysql.connect
    con.autocommit(True)
    cursor = con.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO accidentdetails VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s)", (roveg1, roadsurf1, light1, weather1, cclass1,  typeveg1, prediction, userid, place))
    refid = cursor.lastrowid
    mysql.connect.commit()
    
    pred = {"prediction":prediction,
            "curlocation":x["location"]["name"],
            "region":x["location"]["region"],
            "temperature":x["current"]["temperature"],
            "localtime":x["location"]["localtime"],
            "sroveg":roveg1,
            "basicroadsurf":roadsurf1,
            "light":light1,
            "weather":weather1,
            "scclass":cclass1,
            "stypeveg":typeveg1,
            "refid":refid,
            "latitude":latitude,
            "longitude":longtitude}
    
    return pred

def futurepred(longtitude, latitude, roveg, typeveg, cclass):
    if flask.request.method == 'POST':
       
       nextdatetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
       userid    = session.get("userid")
       
       full_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+latitude+","+longtitude+"?unitGroup=us&key="
       response = requests.get(full_url) 
       asc = response.text
       weatherdata =  json.loads(asc)
       current_hour = datetime.now().hour
       current_epoch_time = int(datetime.now().timestamp())

       current_hour_map = None
       for day in weatherdata['days']:
           for hour in day['hours']:
               if hour['datetimeEpoch'] <= current_epoch_time < hour['datetimeEpoch'] + 3600:  # Adding 3600 seconds for an hour
                   current_hour_map = hour
                   #print(current_hour_map)
                   break
       
       
       whethercond = weatherdata["days"][0]["conditions"]
       #print(whethercond)
       
       is_day = datetime.today().hour + 12
       
       if is_day > 18 or is_day < 20:
           light = 2
       elif  is_day >=20 or is_day <= 5:
           light = 3
       else:
           light = 0
           
       if  "clear" in weatherdata:
           weather = 0
       if  "cloud" in weatherdata:
           weather = 1
       elif "rain" in weatherdata  and "wind" not in weatherdata:
           weather = 4
       elif "rain" in weatherdata  and "wind" in weatherdata:
           weather = 5
       elif "snow" in weatherdata  and  "wind" not in weatherdata:
           weather = 6
       elif "snow" in weatherdata  and "wind" in weatherdata:
           weather = 7
       else:
           weather = 0
        
       
       if weather == 4:
           roadsurf = 2
       elif weather == 5:
           roadsurf = 4
       elif weather == 6 or weather == 7:
           roadsurf = 3
       else:
           roadsurf = 0
           
       input_variables = pd.DataFrame([[roveg, roadsurf, light, weather, cclass,  typeveg]],
                                     columns=['1st Road Class', 'Road Surface','Lighting Conditions','Weather Conditions','Casualty Class','Type of Vehicle'], dtype=float)
       prediction = model.predict(input_variables)[0]
      
       if prediction == 1:
          prediction="Serious Accident"
       else:
          prediction="Slight Accident"
          
       roveg2 = roadsurf2 = light2 = weather2 = cclass2 = typeveg2 = ''
        
       if int(roveg) == 0:
           roveg2 = 'A - Type'
       elif int(roveg) == 1:
           roveg2 = 'A(M) - Type'
       elif int(roveg) == 2:
           roveg2 = 'B - Type'
       elif int(roveg) == 3:
           roveg2 = 'Motor way - Type'
       elif int(roveg) == 4:
           roveg2 = 'Unclassified - Type'
            
       if int(roadsurf) == 0:
         roadsurf2 = 'Dry'
       elif int(roadsurf) == 1:
         roadsurf2 = 'Frost'
       elif int(roadsurf) == 2:
         roadsurf2 = 'Flood'
       elif int(roadsurf) == 3:
         roadsurf2 = 'Snow'
       elif int(roadsurf) == 4:
         roadsurf2 = 'Wet'          
            
       if int(light) == 0:
          light2 = 'No street lighting'
       elif int(light) == 1:
          light2 = 'Street lighting unknown'
       elif int(light) == 2:
          light2 = 'Street lights present and lit'
       elif int(light) == 3:
          light2 = 'Darkness'
           
       if int(weather) == 0:
          weather2 = 'Fine without high winds'
       elif int(weather) == 1:
          weather2 = 'Fog or mist – if hazardn'
       elif weather == 2:
          weather1 = 'Street lights present and lit'
       elif int(weather) == 3:
          weather2 = 'Other'
       elif int(weather) == 4:
          weather2 = 'Raining without high winds'
       elif int(weather) == 5:
          weather2 = 'Raining with high winds'
       elif int(weather) == 6:
          weather2 = 'Snowing without high winds'
       elif int(weather) == 7:
          weather2 = 'Snowing with high winds'
       elif int(weather) == 8:
          weather2 = 'Unknown'
           
       if int(cclass) == 0:
          cclass2 = 'Driver'
       elif int(cclass) == 1:
          cclass2 = 'Passenger'
       elif int(cclass) == 2:
          cclass2 = 'Pedestrian'
            
      
       if int(typeveg) == 0:
          typeveg2 = 'Agri vehicle'
       elif int(typeveg) == 1:
          typeveg2 = 'Bus'
       elif int(typeveg) == 2:
          typeveg2 = 'Car'
       elif int(typeveg) == 3:
          typeveg2 = 'Goods Vehicle'
       elif int(typeveg) == 4:
          typeveg2 = 'Motorcycle'
       elif int(typeveg) == 5:
          typeveg2 = 'Pedal cycle'
       elif int(typeveg) == 6:
          typeveg2 = 'Other vehicle'
          
      
       
       place = "dem"#x["location"]["name"]
      
       #store in db
       con = mysql.connect
       con.autocommit(True)
       cursor = con.cursor(MySQLdb.cursors.DictCursor)
       cursor.execute("INSERT INTO accidentdetails VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s)", (roveg2, roadsurf2, light2, weather2, cclass2,  typeveg2, prediction, userid, place))
       refid = cursor.lastrowid
       mysql.connect.commit()
       
       pred = {"prediction":prediction,
               "curlocation":place,
               "region":1,#x["location"]["region"],
               "temperature":1,#x["current"]["temperature"],
               "localtime": nextdatetime,
               "sroveg":roveg2,
               "basicroadsurf":roadsurf2,
               "light":light2,
               "weather":weather2,
               "scclass":cclass2,
               "stypeveg":typeveg2,
               }
       
    return pred
       
       



@app.route('/getrecords', methods=['GET', 'POST'])
def getrecords():
    if flask.request.method == 'GET':
        if not session.get("userid"):
            return(flask.render_template('login.html'))
        elif session.get("userid") is None:
            return(flask.render_template('login.html'))
        else:
            return(flask.render_template('reporting.html'))
        
    if flask.request.method == 'POST':
        result = {}
        data    = '%'+request.form['searchdata']+'%'
        userid = session.get("userid")
    
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accidentdetails WHERE user = %s AND referencenumber like %s OR roadtype like %s OR roadsurface like %s OR lightcondition like %s OR weather like %s OR casualityclass like %s OR vehicletype like %s OR prediction like %s OR accidentdate like %s OR place like %s', (userid, data, data, data, data, data, data, data, data, data, data))
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/getsingle', methods=['GET', 'POST'])
def getsingle():
    if flask.request.method == 'POST':
        refid = request.form['refid']
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accidentdetails WHERE referencenumber = %s', (refid,))
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/readuserdetails', methods=['GET', 'POST'])
def readuserdetails():
    if flask.request.method == 'GET':
        userid = session.get("userid")
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userdetails WHERE userid = %s', (userid,))
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/getDistrict', methods=['GET', 'POST'])
def getDistrict():
    result = ''
    if flask.request.method == 'POST':
        state = request.form['state']
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM indian_cities_database WHERE state = %s', (state,))
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/getState', methods=['GET', 'POST'])
def getState():
    result = ''
    if flask.request.method == 'POST':
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT DISTINCT state FROM indian_cities_database')
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/getcities', methods=['GET', 'POST'])
def getcities():
    result = ''
    if flask.request.method == 'POST':
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT DISTINCT city FROM indian_cities_database')
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/mapseverity', methods=['GET', 'POST'])
def mapseverity():
    result = ''
    if flask.request.method == 'POST':
        access_key = ""
        base_url = ""
        extractedValues = request.form['extractedValues']
        livevehicle = request.form['livevehicle']
        livecasuality = request.form['livecasuality']
        liveroad = request.form['liveroad']
        curlat  = request.form['curlat']
        curlong = request.form['curlong']
        weather_data = []
        if extractedValues != '[null]':
            coordinates = eval(extractedValues)
            for lon, lat in coordinates:
                response_data = getpred(str(lon), str(lat), liveroad, livevehicle, livecasuality)
                coordinates = [float(lon), float(lat)]
                locname = get_location_name(lat, lon)
                #print(response_data)
                if(response_data["prediction"] == 'Serious Accident'):
                    severity = locname + " - Not Safe For Travel - " + response_data["prediction"] + " zone"
                    formatted_data = {
                        "coordinates": coordinates,
                        "name": severity,
                        "curloc":locname,
                        "curpred":response_data["prediction"]
                    }
                    weather_data.append(formatted_data)
            curlocdetail = current_loc_accid(curlat, curlong, liveroad, livevehicle, livecasuality)
            weather_data.append(curlocdetail)
            
    return jsonify(weather_data)

def current_loc_accid(curlat, curlong, liveroad, livevehicle, livecasuality):
    locname = get_location_name(curlat, curlong)
    response_data = getpred(str(curlong), str(curlat), liveroad, livevehicle, livecasuality)
    response = {"curloc":locname, "curpred":response_data["prediction"]}
    if response_data["prediction"] == 'Serious Accident':
        to_number = session.get("userphone")     
        message = '**Message From Highway authority**\nYour current Location : '+locname+', is deteced as Acciental zone. Please take care while you driving.\nHere are the location weather info for your reference.\n'
        message = message + "The current Temperature is detected as : "+str(response_data["temperature"])+" deg celcius.\n"+"Your driving road surface is : "+response_data["basicroadsurf"]+"\n"+"And the weather looks like : "+response_data["weather"]+"\n"+"The lighting looks like : "+response_data["light"]+"\n\nRegards,\nNHAI."
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
    return response
def get_location_name(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'display_name' in data:
            return data['display_name']
    return "Name Notfound"

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session["userid"]   = None
    return "1"

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
@app.route('/sendmail', methods=['GET', 'POST'])
def sendmail():
    if flask.request.method == 'POST':
        
        refID = flask.request.form['refID']
        recipient_email = flask.request.form['email']
        
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accidentdetails WHERE referencenumber ="'+refID+'" ')
        result = cursor.fetchone()
        
        print (result)
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("abhibytes007@gmail.com", "wvcn prts bauq pmxz")
    
        # Email details
        sender_email_id = "abhibytes007@gmail.com"
        
        #recipient_email = session.get("email")
        
        subject = "Accident Severity Detection"
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if result["prediction"] == 1:
            prediction = "Serious Accident"
        else:
            prediction = "Slight Accident"
        
        place = result["place"]
        ad  = result["accidentdate"]
        name = session["name"]
        # Message content
        body = f"""
        Dear {name},
        
        You are receiving this email from the Accident Severity Detection site.
        
        We inform that an accident zone has been detected with the following details:
        
        - **Location**: {place}
        - **Severity**: {prediction}
        - **Date and Time**: {ad}
        
        ### Accident Details:
        Our system has detected an accident  at {place}. Based on our advanced AI algorithms, the severity of this accident is classified as: **{prediction}**. The incident occurred on {ad}. Our system continuously monitors road conditions and accident reports to provide real-time updates and assistance.
        
        ### Safety Measures:
        1. **Stay Calm**: Ensure your safety and the safety of others around you. Avoid any actions that might escalate the situation.
        2. **Emergency Services**: Contact emergency services immediately if there are any injuries or hazards.
        3. **Documentation**: Take note of the details surrounding the accident, including the time, location, and any involved parties. If possible, take photographs for documentation.
        4. **Follow-up**: Follow the instructions provided by emergency personnel and your insurance provider.
        
        ### Support and Assistance:
        If you need any further assistance or have any questions, please do not hesitate to contact our support team. We are here to help you through this challenging time.
        
        With regards,
        
        **Team AI Accident Severity Detection**
        
        **Contact Information:**
        - Email: support@accidentdetection.com
        - Phone: +1 (123) 456-7890
        - Website: www.accidentdetection.com
        """
        
        # Create a MIMEMultipart object
        msg = MIMEMultipart()
        msg['From'] = sender_email_id
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
    
        
        # Attach text
        text = MIMEText(body, 'plain')
        msg.attach(text)
    
        # Send the email
        s.sendmail(sender_email_id, recipient_email, msg.as_string())
        s.quit()
        
        return "1"

# if __name__ == '__main__':
#     app.run(debug=False)
