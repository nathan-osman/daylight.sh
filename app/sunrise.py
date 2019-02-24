from datetime import datetime, timezone
from math import acos, asin, cos, pi, remainder, sin


_DEGREE = pi / 180
_J2000 = 2451545
_UNIX_EPOCH_JULIAN_DAY = 2440587.5


def _julian_to_unix(j):
    return int((j - _UNIX_EPOCH_JULIAN_DAY) * 86400)


def sunrise_sunset(latitude, longitude, year, month, day):
    """
    Calculate the sunrise and sunset times for the given location and date
    """
    noon = datetime(year, month, day, 12, 0, 0,
                    tzinfo=timezone.utc).timestamp()
    mean_solar_noon = (noon / 86400 + _UNIX_EPOCH_JULIAN_DAY) - longitude / 360
    solar_mean_anomaly = remainder(
        357.5291 + 0.98560028 * (mean_solar_noon - _J2000), 360)
    if solar_mean_anomaly < 0:
        solar_mean_anomaly += 360
    anomaly_in_rad = solar_mean_anomaly * _DEGREE
    anomaly_sin = sin(anomaly_in_rad)
    anomaly2_sin = sin(2 * anomaly_in_rad)
    anomaly3_sin = sin(3 * anomaly_in_rad)
    equation_of_center = 1.9148 * anomaly_sin + \
        0.02 * anomaly2_sin + 0.0003 * anomaly3_sin
    argument_of_perihelion = 102.93005 + 0.3179526 * \
        (mean_solar_noon - _J2000) / 36525
    ecliptic_longitude = (
        solar_mean_anomaly + equation_of_center + 180 + argument_of_perihelion) % 360
    solar_transit = mean_solar_noon + \
        (0.0053 * sin(solar_mean_anomaly * _DEGREE) -
         0.0069 * sin(2 * ecliptic_longitude * _DEGREE))
    declination = asin(sin(ecliptic_longitude * _DEGREE) * 0.39779) / _DEGREE
    latitude_rad = latitude * _DEGREE
    declination_rad = declination * _DEGREE
    hour_angle = acos((-0.01449 - sin(latitude_rad) * sin(declination_rad)
                       ) / (cos(latitude_rad) * cos(declination_rad))) / _DEGREE
    frac = hour_angle / 360
    sunrise = solar_transit - frac
    sunset = solar_transit + frac
    return _julian_to_unix(sunrise), _julian_to_unix(sunset)
