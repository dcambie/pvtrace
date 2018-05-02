# from datetime import datetime
# day_of_year = datetime.now().timetuple().tm_yday
# print(day_of_year)
from datetime import datetime
import numpy as np
import math

class Solar_angle(object):
    def __init__(self, year, month, day, standard_time, standard_longitude, local_longitude, local_latitude):
        super(Solar_angle, self).__init__()
        self.year = year
        self.month = month
        self.day = day
        self.stand_time = standard_time
        self.stand_long = standard_longitude
        self.local_long = local_longitude
        self.local_lati = local_latitude

    def run_solar(self):
        self.day_angle()
        self.hour_angle()
        self.distance_calcul()
        self.solar_declination()
        self.local_apparent_time()
        self.zenith_angle()
        self.azimuth_angle()
        self.sunrise_angle()
        self.day_length()

    def day_angle(self):
        date = str(self.day) + "-" + str(self.month) + "-" + str(self.year)  ## format is 02-02-2016
        adate = datetime.strptime(date, "%d-%m-%Y")
        day_of_year = adate.timetuple().tm_yday
        self.day_angle_rad = 2 * np.pi * (day_of_year - 1) / 365  # in radians
        return self.day_angle_rad

    def hour_angle(self):
        LAT = self.local_apparent_time()
        self.hour_angle_deg = (12-LAT)*15
        return self.hour_angle_deg

    def distance_calcul(self):
        angle = self.day_angle()
        correction_factor = 1.000110 + 0.034221*np.cos(angle) + 0.001280 * np.sin(angle) + \
                            0.000719*np.cos(2 * angle) + 0.000077 * np.sin(2 * angle)
        self.dis_r = 1/np.sqrt(correction_factor) # unit AU: 1 AU equals 1.496x10**8 km
        return self.dis_r

    def solar_declination(self):
        angle = self.day_angle()
        self.declination_deg = (0.006918 - 0.399912*np.cos(angle) + 0.070257*np.sin(angle) - 0.006758*np.cos(2*angle) +
                       0.000907*np.sin(2*angle) - 0.002697*np.cos(3*angle) + 0.00148*np.sin(3*angle))*(180/np.pi) # in degrees
        return self.declination_deg

    def local_apparent_time(self):
        angle = self.day_angle()
        self.equation_of_time = (0.000075 + 0.001868*np.cos(angle) - 0.032077*np.sin(angle) - 0.014615*np.cos(2*angle)
                            - 0.04089*np.sin(2*angle))*229.18 # minutes
        self.apparent_time = self.stand_time + 4*(self.local_long - self.stand_long)/60 + self.equation_of_time/60 # unit hour
        return self.apparent_time

    def zenith_angle(self):
        declination_angle = math.radians(self.solar_declination())
        hour_angle_cal = math.radians(self.hour_angle())
        local_lati_rad = math.radians(self.local_lati)
        zenith_angle_cal = np.arccos(np.sin(declination_angle) * np.sin(local_lati_rad) + \
                           np.cos(declination_angle) * np.cos(local_lati_rad) * np.cos(hour_angle_cal))
        self.zenith_angle_deg = math.degrees(zenith_angle_cal)
        return self.zenith_angle_deg

    def azimuth_angle(self):
        zenith_angle = self.zenith_angle()
        solar_altitude = 90 - zenith_angle
        solar_alti_rad = math.radians(solar_altitude)
        local_lati_rad = math.radians(self.local_lati)
        declination_angle = math.radians(self.solar_declination())
        azimuth_angle = np.arccos((np.sin(solar_alti_rad) * np.sin(local_lati_rad) - np.sin(declination_angle))/
                                  (np.cos(solar_alti_rad)*np.cos(local_lati_rad)))
        self.azimuth_angle_deg = math.degrees(azimuth_angle)
        return self.azimuth_angle_deg

    def sunrise_angle(self):
        local_lati_rad = math.radians(self.local_lati)
        dec_angle_rad = math.radians(self.solar_declination())
        # this equation is derived from the zenith angle equation while zenith angle equals 90 degrees
        sunrise_angle = np.arccos(-np.tan(local_lati_rad)*np.tan(dec_angle_rad))
        self.sunrise_angle_deg = math.degrees(sunrise_angle)
        return self.sunrise_angle_deg # noon zero, morning positive

    def day_length(self):
        sunrise_angle = self.sunrise_angle()
        self.day_length_hour = 2*sunrise_angle/15
        return self.day_length_hour #unit hours

class Tilt_solar_angle(Solar_angle):
    def __init__(self, year, month, day, standard_time, standard_longitude, local_longitude, local_latitude, tilt_angle):
        super(Solar_angle, self).__init__()
        self.year = year
        self.month = month
        self.day = day
        self.stand_time = standard_time
        self.stand_long = standard_longitude
        self.local_long = local_longitude
        self.tilt_angle = tilt_angle
        self.local_lati = local_latitude - tilt_angle # changing the tilt angle means that the horizontal surface putting on the different latitude

    def sunrise_angle(self):
        tilt_lati_rad = math.radians(self.local_lati)
        hori_lati_rad = math.radians(self.local_lati+self.tilt_angle)

        dec_angle_rad = math.radians(self.solar_declination())
        # this equation is derived from the zenith angle equation while zenith angle equals 90 degrees
        sunrise_angle_tilt = math.degrees(np.arccos(-np.tan(tilt_lati_rad) * np.tan(dec_angle_rad)))
        sunrise_angle_hori = math.degrees(np.arccos(-np.tan(hori_lati_rad) * np.tan(dec_angle_rad)))
        # the sunrise angle for a tilted surface could never be greater than that for horizontal surface
        if sunrise_angle_tilt >= sunrise_angle_hori:
            sunrise_angle_tilt = sunrise_angle_hori
        self.sunrise_angle_deg = sunrise_angle_tilt
        return self.sunrise_angle_deg

    def return_vector(self):
        if self.zenith_angle_deg<=90:
            vector_x = -np.tan(math.radians(self.zenith_angle_deg)) * np.sin(math.radians(self.azimuth_angle_deg))
            vector_y = np.tan(math.radians(self.zenith_angle_deg)) * np.cos(math.radians(self.azimuth_angle_deg))
            vector_z = -1
            return vector_x, vector_y, vector_z
        else:
            raise Exception, "warning, it's dark already"


if __name__ == "__main__":
    a = Tilt_solar_angle(year=2017, month=6, day=30, standard_time=5, standard_longitude=15, local_longitude=5.49, local_latitude=51.44, tilt_angle=51.44)
    b = Solar_angle(year=2017, month=6, day=15, standard_time=6, standard_longitude=15, local_longitude=5.49, local_latitude=51.44)
    a.run_solar()
    b.run_solar()
    print(a.return_vector())
