from geopy.geocoders import Nominatim
import argparse
import requests
import xml.etree.ElementTree as ET
import geocoder
from prettytable.colortable import ColorTable, Themes
from datetime import datetime


loc = Nominatim(user_agent="GetLoc")

API_KEY = "cab14a5e93d9ea7d3238cff419939d02"

parser = argparse.ArgumentParser(
        prog="Weather",
        description="A simple CLI app that shows current weather and 5-day forecast",
        )

parser.add_argument('--location', help="You may specify a location")
parser.add_argument('--forecast', help="Not current weather, but 5-day forecast")
parser.add_argument('--units', help='Choose metric or imperial system of units', default='metric')
parser.add_argument('--lang', help='Choose language of the output (use a language code)', default='en')

args = parser.parse_args()

getLoc = geocoder.ip('me') if args.location is None else loc.geocode(args.location)
latitude, longitude = (getLoc.latlng if args.location is None else (getLoc.latitude, getLoc.longitude))

response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units={args.units}&lang={args.lang}&mode=xml&appid={API_KEY}")
response = response.text
root = ET.fromstring(response)

def dict_all_data(root):
    dicted_data = {}
    for child in root:
        if list(child):  
            dicted_data[child.tag] = dict_all_data(child)
        else:
            dicted_data[child.tag] = child.text if child.text is not None else child.attrib if child.attrib != {} else ''
    return dicted_data

dicted_data = dict_all_data(root)

def print_table(data, table=None):
    if table is None:
        table = ColorTable(theme=Themes.OCEAN)
        table.field_names = ["Property", "Value"]
        table.hrules = True  

    for key, value in data.items():
        if isinstance(value, dict):
            if key in ['city', 'wind']:
                for subkey, subvalue in value.items():
                    if subkey == 'gusts':
                        continue
                    if isinstance(subvalue, dict):
                        subvalue = ', '.join([f"{k}: {datetime.strptime(str(v), '%Y-%m-%dT%H:%M:%S').strftime('%A, %B %d, %Y %I:%M:%S %p')}" if 'T' in str(v) else str(v) if k == 'value' else f'{k}: {str(v)}' for k, v in subvalue.items()])
                    table.add_row([f"{key}.{subkey}", subvalue])
            else:
                value = ', '.join([f"{k}: {datetime.strptime(str(v), '%Y-%m-%dT%H:%M:%S').strftime('%A, %B %d, %Y %I:%M:%S %p')}" if 'T' in str(v) else str(v) if k == 'value' else f'{k}: {str(v)}' for k, v in value.items()])
                table.add_row([key, value])
        else:
            table.add_row([key, value])

    return table

table = print_table(dicted_data)
print(table)