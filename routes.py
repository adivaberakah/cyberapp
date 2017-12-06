from flask import Flask, render_template, request, url_for
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import pygeoip
import socket
import urllib.request
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import csv

external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

application = Flask(__name__)
application.config['GOOGLEMAPS_KEY'] = "AIzaSyAYkWl0-rLmFkMvROv2FGBUlVS4OR387yE"
GoogleMaps(application, key="AIzaSyAYkWl0-rLmFkMvROv2FGBUlVS4OR387yE")


@application.route("/")
def home():
    # creating a map in the view
    go = pygeoip.GeoIP('GeoLiteCity.dat')
    record = go.record_by_addr(external_ip)
    lat = record['latitude']
    long = record['longitude']

    sndmap = Map(
        identifier="sndmap",
        lat=lat,
        lng=long,
        style="height:500px;width=300px;margin:0;",
        zoom=8,
        markers=[
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'lat': lat,
                'lng': long,
                'infobox': "<b>Hello World</b>"
            },

        ]
    )

    return render_template('map.html', sndmap=sndmap)


UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/')  ## this is the folder on my machine
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_data():
    type_of_packet = []

    with open('static/ipaddrlist.csv') as in_file:
        csv_reader = csv.reader(in_file)
        for row in csv_reader:
            type_of_packet.append(tuple(row))
    return type_of_packet


def ip_loc_record():
    data = get_data()
    loc = []
    for packet in data:
        ip = packet[0]
        go = pygeoip.GeoIP('GeoLiteCity.dat')
        a = go.record_by_addr(ip)
        if a != None:
            loc.append(a)
        else:
            print('This is a private ip address, the iplocation cannot be found on the map at this time')
    return loc


def icon_descr():
    data = get_data()
    icons = []
    icon_name = []
    for packet in data:
        if packet[1] == 'Normal User':
            icon = "static\img\bluemap_marker.png"
            icons.append(icon)
            icon_name.append(packet[1])
        elif packet[1] == "TCP Dos Flood":
            icon = "static\img\greenmap_marker.png"
            icons.append(icon)
            icon_name.append(packet[1])
    return icons


@application.route('/', methods=['GET', 'POST'])
def map():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))  # saves the file in the machinealgorithm folder
    ip_rec = ip_loc_record()
    lat = []
    long = []
    country = []
    for record in ip_rec:
        lat.append(record['latitude'])

    for record in ip_rec:
        long.append(record['longitude'])

    for record in ip_rec:
        country.append(record['country_name'])

    location = list(zip(lat, long, country))
    sndmap = Map(
        identifier="sndmap",
        lat=lat[0],
        lng=long[0],
        markers=location,
        fit_markers_to_bounds=True,
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "left:0;"
            "position:absolute;"
            "z-index:200;"
        ),)
        #zoom=4)

    return render_template('map.html', sndmap=sndmap)


if __name__ == "__main__":
    application.run(debug=True)
