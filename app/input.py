from datetime import datetime
from os import path

from geoip2.database import Reader
from pytz import timezone, utc


class Input:
    """
    A simple class for collecting and analyzing input

    Input can come from a lot of different sources: query string parameters,
    form input, JSON input, or even IP geolocation data. This class provides a
    simple way to retrieve those values from the best available source.
    """

    MIME_TEXT_PLAIN = 'text/plain'
    MIME_TEXT_HTML = 'text/html'
    MIME_FORM = 'application/x-www-form-urlencoded'
    MIME_JSON = 'application/json'

    # Load the geolocation database
    _reader = reader = Reader(
        path.join(path.dirname(path.abspath(__file__)), 'GeoLite2-City.mmdb'),
    )

    def __init__(self, request):
        """
        Initialize the ordered list of input sources
        """
        self._sources = [request.args, ]
        if request.method == 'POST':
            if request.is_json:
                self._sources.append(request.json)
            elif request.mimetype == self.MIME_FORM:
                self._sources.append(request.form)
        self._sources.append(self._geolocate(request.remote_addr))
        self._timezone = self._get_timezone()
        self._sources.append(self._get_cur_date())
        self._mime = self._get_mime(request)

    def _geolocate(self, ip):
        """
        Attempt to determine the client's location based on their IP address
        """
        try:
            data = self._reader.city(ip)
            city = []
            if data.city.name is not None:
                city.append(data.city.name)
            if len(data.subdivisions):
                city.append(data.subdivisions.most_specific.name)
            city.append(data.country.name)
            return {
                'latitude': data.location.latitude,
                'longitude': data.location.longitude,
                'location': ', '.join(city),
                'timezone': data.location.time_zone,
            }
        except:
            return {}

    def _get_timezone(self):
        try:
            return timezone(self.get('timezone') or 'utc')
        except:
            return utc

    def _get_cur_date(self):
        """
        Calculate the current date in the user's timezone
        """
        now = datetime.now(self._timezone)
        return {
            'year': now.year,
            'month': now.month,
            'day': now.day,
        }

    def _get_mime(self, request):
        """
        Determine the appropriate MIME type for the response
        """

        # If curl is used with the default Accept header, respond with text
        if request.user_agent.string.startswith('curl/') and \
                request.headers.get('accept') == '*/*':
            return self.MIME_TEXT_PLAIN

        # Prefer HTML by default
        mime = self.MIME_TEXT_HTML

        # Prefer a JSON response for POST requests with JSON
        if request.method == 'POST' and request.is_json:
            mime = self.MIME_JSON

        # Find a MIME that is supported
        if mime not in request.accept_mimetypes:
            if request.accept_mimetypes.accept_html:
                mime = self.MIME_TEXT_HTML
            elif request.accept_mimetypes.accept_json:
                mime = self.MIME_JSON
            else:
                mime = self.MIME_TEXT_PLAIN

        return mime

    def get(self, name):
        """
        Search for a value within the list of sources (in order)
        """
        for s in self._sources:
            if name in s:
                return s[name]
        return None

    def get_int(self, name, min, max):
        try:
            v = int(self.get(name))
            assert v >= min and v <= max
            return v
        except:
            return None

    def get_float(self, name, min, max):
        try:
            v = float(self.get(name))
            assert v >= min and v <= max
            return v
        except:
            return None

    def get_timezone(self):
        return self._timezone

    def get_mime(self):
        return self._mime
