from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask.json import JSONEncoder
from pytz import utc
from werkzeug.contrib.fixers import ProxyFix

from input import Input
from sunrise import sunrise_sunset


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)


@app.context_processor
def inject_functions():
    def timestamp_to_pretty(timestamp, tz):
        d = datetime.utcfromtimestamp(timestamp).replace(
            tzinfo=utc).astimezone(tz)
        return '{}:{:02}{}'.format(
            d.hour % 12 or '12',
            d.minute,
            'am' if d.hour <= 12 else 'pm',
        )
    return {
        'timestamp_to_pretty': timestamp_to_pretty,
    }


@app.route("/", methods=['GET', 'POST'])
def index():

    # Load the input for the calculations from the request
    input = Input(request)

    # Load the parameters for the calculation
    data = {
        'latitude': input.get_float('latitude', -90.0, 90.0),
        'longitude': input.get_float('longitude', -180.0, 180.0),
        'year': input.get_int('year', 1900, 2099),
        'month': input.get_int('month', 1, 12),
        'day': input.get_int('day', 1, 31),
    }

    # Perform the calculation - if possible
    if None not in data.values():
        data['sunrise'], data['sunset'] = sunrise_sunset(**data)

    # Inject the location and timezone if available
    location = input.get('location')
    if location is not None:
        data['location'] = location
    timezone = input.get('timezone')
    if timezone is not None:
        data['timezone'] = timezone

    # Add a few extra variables for the template renderers
    extra = dict(data)
    extra.update({
        'is_post': request.method == 'POST',
        'tz': input.get_timezone(),
    })

    # Write the response
    if input.get_mime() == Input.MIME_TEXT_HTML:
        return render_template('index.html', **extra)
    elif input.get_mime() == Input.MIME_JSON:
        return jsonify(data)
    else:
        return render_template('index.txt', **extra)
