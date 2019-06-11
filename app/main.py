from datetime import datetime
from os import path

from geoip2.database import Reader
from flask import Flask, jsonify, render_template, request
from pytz import timezone, utc
from werkzeug.contrib.fixers import ProxyFix

from sunrise import sunrise_sunset


_MIME_TEXT_PLAIN = 'text/plain'
_MIME_TEXT_HTML = 'text/html'
_MIME_FORM = 'application/x-www-form-urlencoded'
_MIME_JSON = 'application/json'


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

# Load the MaxMind database
reader = Reader(
    path.join(path.dirname(path.abspath(__file__)), 'GeoLite2-City.mmdb')
)


def _geolocate(ip):
    """
    Attempt to geolocate the provided IP address

    If the coordinates were found, they are returned along with a string
    representation of the location used and its timezone. If an error occurs,
    the response is an empty map
    """
    try:
        d = reader.city(ip)
        l = []
        if d.city.name is not None:
            l.append(d.city.name)
        if len(d.subdivisions):
            l.append(d.subdivisions.most_specific.name)
        l.append(d.country.name)
        return {
            'latitude': d.location.latitude,
            'longitude': d.location.longitude,
            'location': ', '.join(l),
            'timezone': d.location.time_zone,
        }
    except:
        return {}


def _get_data(request):
    """
    Obtain the data for the calculations
    """
    data = {}

    # For POST requests, JSON and x-www-form-urlencoded are supported
    if request.method == 'POST':
        if request.is_json:
            data.update(request.json)
        elif request.mimetype == _MIME_FORM:
            data.update(request.form)

    # Add query string parameters if supplied
    data.update(request.args)

    # Geolocate the client in order to determine timezone information
    g = _geolocate(request.remote_addr)

    # If the client did not provide coordinates, use the geo ones
    if 'latitude' not in data or 'longitude' not in data:
        data.update(g)
        data['auto_location'] = True

    # Attempt to determine an appropriate timezone to use
    try:
        tz = timezone(data.get('timezone', g['timezone']))
    except:
        tz = utc
    data['tz'] = tz

    # If a date was not provided, use the current one
    if 'year' not in data or 'month' not in data or 'day' not in data:
        n = datetime.now(tz)
        data.update({
            'year': n.year,
            'month': n.month,
            'day': n.day,
            'auto_date': True,
        })

    return data


def _get_mime(request):
    """
    Determine the mime type for the response
    """

    # If curl is used with the default Accept header (*/*), respond with text
    if request.user_agent.string.startswith('curl/') and \
            request.headers.get('accept') == '*/*':
        return _MIME_TEXT_PLAIN

    # Prefer HTML by default
    mime = _MIME_TEXT_HTML

    # Prefer a JSON response for POST requests
    if request.method == 'POST' and request.is_json:
        mime = _MIME_JSON

    # Find a MIME that is supported
    if mime not in request.accept_mimetypes:
        if request.accept_mimetypes.accept_html:
            mime = _MIME_TEXT_HTML
        elif request.accept_mimetypes.accept_json:
            mime = _MIME_JSON
        else:
            mime = _MIME_TEXT_PLAIN

    return mime


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Render the homepage based on the provided request headers
    """

    # Get the data and mimetype
    data, mime = _get_data(request), _get_mime(request)

    # Perform the calculation if the data is available
    if 'longitude' in data and 'latitude' in data:
        sunrise, sunset = sunrise_sunset(
            float(data['latitude']),
            float(data['longitude']),
            int(data['year']),
            int(data['month']),
            int(data['day']),
        )
        data.update({
            'sunrise': sunrise,
            'sunset': sunset,
            'sunrise_datetime': datetime.utcfromtimestamp(sunrise),
            'sunset_datetime': datetime.utcfromtimestamp(sunset),
        })

    # Write the response
    if mime == _MIME_TEXT_HTML:
        return render_template('index.html', method=request.method, **data)
    elif mime == _MIME_JSON:
        return jsonify(data)
    else:
        return render_template('index.txt', **data)
