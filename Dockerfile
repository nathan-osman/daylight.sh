FROM tiangolo/meinheld-gunicorn-flask:latest

COPY ./app /app

RUN pip install -r /app/requirements.txt

# Download MaxMind's database
RUN \
    curl https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz | \
        tar xf GeoLite2-Country.tar.gz --strip-components -C /app