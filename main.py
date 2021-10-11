import requests
import json
from _datetime import datetime
import time

from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast


app = Flask(__name__)
api = Api(app)


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def j_print(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


list_length = []
email = "gsuranga@gmail.com"
password = "vus@ryX4sZLo6VZVHXa9"
apiToken = "APIToken 20b6537b4aaa361dd7b09549711037e77dc438ee"
parameters = {"email": email, "password": password}

page_size = '&page_num=0&page_size=200'
page_hits = '&page_num=0&page_hits=50'


#local_datetime = datetime.datetime.now()
#local_datetime_timestamp = float(local_datetime.strftime("%s"))
#UTC_datetime_converted = datetime.datetime.utcfromtimestamp(local_datetime_timestamp)
#print(UTC_datetime_converted)


start_utc = '&start_utc=2021-03-09T19:43:52'
data_pull = 'https://api.autopi.io/logbook/raw/?device_id='
alert_pull = 'https://api.autopi.io/logbook/diagnostics/?device_id='

bat_type = '&data_type=obd.bat'
fuel_type = '&data_type=obd.fuel_level'
pos_type = '&data_type=track.pos'

authorise = requests.post('https://api.autopi.io/auth/login/', data=parameters)
token = "bearer " + authorise.json()["token"]
authorise = {"Authorization": token}

users = requests.get('https://api.autopi.io/auth/account/users/', headers=authorise)

profile = requests.get('https://api.autopi.io/vehicle/profile/', headers=authorise)

dongle = requests.get('https://api.autopi.io/dongle/devices/', headers=authorise)
device_id = (dongle.json()[0]['id'])
device_name = (dongle.json()[0]['callName'])
car_name = (dongle.json()[0]['vehicle']['display'])
car_year = (dongle.json()[0]['vehicle']['year'])
licence_plate = (dongle.json()[0]['vehicle']['licensePlate'])
vin = (dongle.json()[0]['vehicle']['vin'])
last_com = (dongle.json()[0]['last_communication'])
end_utc = '&end_utc=' + last_com
#local_last_com = datetime_from_utc_to_local(last_com)

fob = 'https://api.autopi.io/dongle/devices/' + device_id + '/execute/'
power_on = {"command": "keyfob.power", "arg": [], "kwarg": {"value": 1}, "returner": "string"}
power_off = {"command": "keyfob.power", "arg": [], "kwarg": {"value": 0}, "returner": "string"}
unlock = {"command": "keyfob.action", "arg": ["unlock"], "kwarg": {}, "returner": "string"}
lock = {"command": "keyfob.action", "arg": ["lock"], "kwarg": {}, "returner": "string"}

type_list = requests.get('https://api.autopi.io/logbook/storage/fields/', headers=authorise)

alerts = requests.get(alert_pull + device_id + page_hits + start_utc + end_utc, headers=authorise)
number_alerts = alerts.json()['count']

battery = requests.get(data_pull + device_id + bat_type + page_size + start_utc + end_utc, headers=authorise)
drilled_battery_data = battery.json()['results']

fuel = requests.get(data_pull + device_id + fuel_type + page_size + start_utc + end_utc, headers=authorise)
drilled_fuel_data = fuel.json()['results']

gps = requests.get(data_pull + device_id + pos_type + page_size + start_utc + end_utc, headers=authorise)
drilled_gps_data = gps.json()['results']


def unlock_car():
    fob_on()
    response = requests.post(fob, headers=authorise, json=unlock)
    jid_number = response.json()['jid']
    fob_off()
    jid_response(jid_number)


def lock_car():
    fob_on()
    response = requests.post(fob, headers=authorise, json=lock)
    jid_number = response.json()['jid']
    fob_off()
    jid_response(jid_number)


def fob_off():
    response = requests.post(fob, headers=authorise, json=power_off)
    jid_number = response.json()['jid']
    jid_power(jid_number)


def fob_on():
    response = requests.post(fob, headers=authorise, json=power_on)
    jid_number = response.json()['jid']
    jid_power(jid_number)


def jid_power(jid_input):
    jid_value = requests.get('https://api.autopi.io/dongle/devices/' + device_id + '/command_result/' + jid_input
                             + '/', headers=authorise)
    power_state = jid_value.json()['value']
    if power_state:
        print("Fob power is ON")
    if not power_state:
        print("Fob power is OFF")


def jid_response(jid_input):
    jid_value = requests.get('https://api.autopi.io/dongle/devices/' + device_id + '/command_result/' + jid_input
                             + '/', headers=authorise)
    if jid_value.json()['_stamp']:
        print("Action completed :", jid_value.json()['_stamp'])
        #print(jid_value.json()['_stamp'])
    else:
        print(jid_value.json())


if len(drilled_gps_data) > 0:
    list_length.append(len(drilled_gps_data))

if len(drilled_fuel_data) > 0:
    list_length.append(len(drilled_fuel_data))

if len(drilled_battery_data) > 0:
    list_length.append(len(drilled_battery_data))

list_length.sort()
length = list_length[0]


def device_info():
    print("Device name: " + str(device_name))
    print("Device id: " + str(device_id))
    print("Car name: " + str(car_name))
    print("Car year: " + str(car_year))
    print("LicencePlate: " + str(licence_plate))
    print("VIN: " + str(vin))
    print("Last communication with device (UTC): " + str(last_com))
    print("Number of active alerts: " + str(number_alerts))
    print()


def list_info():
    i = 0
    while i < length:
        if len(drilled_battery_data) > 0:
            print("Battery V: " + str(drilled_battery_data[i]['data']['voltage']))

        if len(drilled_fuel_data) > 0:
            print("Fuel %: " + str(drilled_fuel_data[i]['data']['value']))

        if len(drilled_gps_data) > 0:
            print("location " + str(drilled_gps_data[i]['data']['loc']))

        print("Time stamp (UTC): " + str(drilled_battery_data[i]['ts']))
        print()
        i = i + 1


# device_info()
# list_info()
class Car(Resource):
    # def get(self):
    #   return {'data': 'Welcome!!!'}, 200
    def post(self):
      parser = reqparse.RequestParser()
      parser.add_argument('option', required=True)
      args = parser.parse_args()
      if args['option'] == 'Lock':
        lock_car()
      if args['option'] == 'Unlock':
        unlock_car()

      return {'data': 'Success: Car is ' + args['option'] + 'ed'}, 200



api.add_resource(Car, '/car')
# api.add_resource(Unlock, '/hello')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
