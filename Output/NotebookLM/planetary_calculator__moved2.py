#!/usr/bin/env python3
"""
Planetary Position Calculator for Geocentric Tropical Western Astrology
Grounded in Jean Meeus' "Astronomical Algorithms" and Pierre Standish's orbital elements.
Provides high-precision calculations for any date, time, and planet,
complete with precession, nutation, and retrograde determination.
"""

import numpy as np

# Classical Keplerian Orbital Elements and rates per century from JPL / Standish (valid for 1800 AD - 2050 AD) [11, 27]
# Columns: a (AU), a_dot (AU/Cy), e (dimensionless), e_dot (1/Cy), i (deg), i_dot (deg/Cy),
#          L (deg), L_dot (deg/Cy), long_peri (deg), long_peri_dot (deg/Cy), long_node (deg), long_node_dot (deg/Cy)
STANDISH_ELEMENTS = {
    'Mercury': {
        'a0': 0.38709927, 'a_dot': 0.00000037,
        'e0': 0.20563593, 'e_dot': 0.00001906,
        'i0': 7.00497902, 'i_dot': -0.00594749,
        'L0': 252.25032350, 'L_dot': 149472.67411175,
        'long_peri0': 77.45779628, 'long_peri_dot': 0.16047689,
        'long_node0': 48.33076593, 'long_node_dot': -0.12534081
    },
    'Venus': {
        'a0': 0.72333566, 'a_dot': 0.00000390,
        'e0': 0.00677672, 'e_dot': -0.00004107,
        'i0': 3.39467605, 'i_dot': -0.00078890,
        'L0': 181.97909950, 'L_dot': 58517.81538729,
        'long_peri0': 131.60246718, 'long_peri_dot': 0.00268329,
        'long_node0': 76.67984255, 'long_node_dot': -0.27769418
    },
    'EMB': {  # Earth-Moon Barycenter [27, 35]
        'a0': 1.00000261, 'a_dot': 0.00000003,
        'e0': 0.01671123, 'e_dot': -0.00003661,
        'i0': -0.00001531, 'i_dot': -0.01294668,
        'L0': 100.46457166, 'L_dot': 35999.37244981,
        'long_peri0': 102.93768193, 'long_peri_dot': 0.32327364,
        'long_node0': 0.0, 'long_node_dot': 0.0
    },
    'Mars': {
        'a0': 1.52371034, 'a_dot': 0.00001847,
        'e0': 0.09339410, 'e_dot': 0.00007882,
        'i0': 1.84969142, 'i_dot': -0.00813131,
        'L0': -4.55343205, 'L_dot': 19140.30268499,
        'long_peri0': -23.94362959, 'long_peri_dot': 0.44441088,
        'long_node0': 49.55809321, 'long_node_dot': -0.29257343
    },
    'Jupiter': {
        'a0': 5.20288700, 'a_dot': -0.00011607,
        'e0': 0.04838624, 'e_dot': -0.00013253,
        'i0': 1.30439695, 'i_dot': -0.00183714,
        'L0': 34.39644051, 'L_dot': 3034.74612775,
        'long_peri0': 14.72847983, 'long_peri_dot': 0.21252668,
        'long_node0': 100.47390909, 'long_node_dot': 0.20469106
    },
    'Saturn': {
        'a0': 9.53667594, 'a_dot': -0.00125060,
        'e0': 0.05386179, 'e_dot': -0.00050991,
        'i0': 2.48599187, 'i_dot': 0.00193609,
        'L0': 49.95424423, 'L_dot': 1222.49362201,
        'long_peri0': 92.59887831, 'long_peri_dot': -0.41897216,
        'long_node0': 113.66242448, 'long_node_dot': -0.28867794
    },
    'Uranus': {
        'a0': 19.18916464, 'a_dot': -0.00196176,
        'e0': 0.04725744, 'e_dot': -0.00004397,
        'i0': 0.77263783, 'i_dot': -0.00242939,
        'L0': 313.23810451, 'L_dot': 428.48202785,
        'long_peri0': 170.95427630, 'long_peri_dot': 0.40805281,
        'long_node0': 74.01692503, 'long_node_dot': 0.04240589
    },
    'Neptune': {
        'a0': 30.06992276, 'a_dot': 0.00026291,
        'e0': 0.00859048, 'e_dot': 0.00005105,
        'i0': 1.77004347, 'i_dot': 0.00035372,
        'L0': -55.12002969, 'L_dot': 218.45945325,
        'long_peri0': 44.96476227, 'long_peri_dot': -0.32241464,
        'long_node0': 131.78422574, 'long_node_dot': -0.00508664
    }
}

def calendar_to_jd(year, month, day, hour=0, minute=0, second=0):
    """
    Converts Gregorian calendar date to Julian Date (JD) in UT.
    Meeus Algorithm (Astronomical Algorithms Chapter 7) [1, 2].
    """
    D = day + hour / 24.0 + minute / 1440.0 + second / 86400.0
    Y = year
    M = month
    
    if M == 1 or M == 2:
        Y = Y - 1
        M = M + 12
        
    # Gregorian calendar reform check [2, 5]
    is_gregorian = True
    if Y < 1582:
        is_gregorian = False
    elif Y == 1582:
        if M < 10:
            is_gregorian = False
        elif M == 10:
            if D < 15.0:  # Gregorian started on Oct 15, 1582
                is_gregorian = False
                
    if is_gregorian:
        A = int(Y / 100)
        B = 2 - A + int(A / 4)
    else:
        B = 0
        
    jd = int(365.25 * (Y + 4716)) + int(30.6001 * (M + 1)) + D + B - 1524.5
    return jd

def jd_to_T(jd, delta_t=69.2):
    """
    Converts Julian Date in UTC/UT1 to Terrestrial Time (TT) and computes
    T (Julian centuries since J2000.0 epoch) [7-10].
    """
    jd_tt = jd + delta_t / 86400.0
    T = (jd_tt - 2451545.0) / 36525.0
    return T

def get_heliocentric_j2000_vector(planet_name, T):
    """
    Calculates the 3D heliocentric rectangular position vector of a planet
    in J2000.0 Ecliptic coordinates (in Astronomical Units, AU) [3, 11, 15, 16].
    """
    coefs = STANDISH_ELEMENTS[planet_name]
    
    a = coefs['a0'] + coefs['a_dot'] * T
    e = coefs['e0'] + coefs['e_dot'] * T
    i = coefs['i0'] + coefs['i_dot'] * T
    L = coefs['L0'] + coefs['L_dot'] * T
    long_peri = coefs['long_peri0'] + coefs['long_peri_dot'] * T
    long_node = coefs['long_node0'] + coefs['long_node_dot'] * T
    
    # Radians conversions and normalization
    i = np.radians(i)
    L = np.radians(L % 360.0)
    long_peri = np.radians(long_peri % 360.0)
    long_node = np.radians(long_node % 360.0)
    
    omega = long_peri - long_node
    M = L - long_peri
    
    # Solve Kepler's Transcendental Equation: E - e * sin(E) = M [12, 15, 32]
    # Initial guess E0
    E = M + e * np.sin(M)
    for _ in range(12):
        f = E - e * np.sin(E) - M
        df = 1.0 - e * np.cos(E)
        diff = f / df
        E = E - diff
        if np.abs(diff) < 1e-12:
            break
            
    # Coordinates in orbital plane [3, 11, 15]
    x_prime = a * (np.cos(E) - e)
    y_prime = a * np.sqrt(1.0 - e**2) * np.sin(E)
    
    # Orbit rotation to J2000.0 ecliptic frame [3, 11, 16]
    cos_w = np.cos(omega)
    sin_w = np.sin(omega)
    cos_o = np.cos(long_node)
    sin_o = np.sin(long_node)
    cos_i = np.cos(i)
    sin_i = np.sin(i)
    
    x_h = (cos_w * cos_o - sin_w * sin_o * cos_i) * x_prime + (-sin_w * cos_o - cos_w * sin_o * cos_i) * y_prime
    y_h = (cos_w * sin_o + sin_w * cos_o * cos_i) * x_prime + (-sin_w * sin_o + cos_w * cos_o * cos_i) * y_prime
    z_h = (sin_w * sin_i) * x_prime + (cos_w * sin_i) * y_prime
    
    return np.array([x_h, y_h, z_h])

def precess_to_date(lon, lat, T):
    """
    Precesses geocentric ecliptic longitude and latitude from J2000.0
    to the mean ecliptic of date using Jean Meeus' formulae [3, 20, 21].
    """
    eta_sec = (47.00290 - 0.03302 * T + 0.000060 * T**2) * T
    Pi_deg = 174.876384 + (3289.474 * T + 0.606 * T**2) / 3600.0
    pa_sec = (5029.0966 + 2.22226 * T - 0.000042 * T**2) * T
    
    eta = np.radians(eta_sec / 3600.0)
    Pi = np.radians(Pi_deg)
    pa = np.radians(pa_sec / 3600.0)
    
    A = np.cos(eta) * np.cos(lat) * np.sin(Pi - lon) - np.sin(eta) * np.sin(lat)
    B = np.cos(lat) * np.cos(Pi - lon)
    C = np.cos(eta) * np.sin(lat) + np.sin(eta) * np.cos(lat) * np.sin(Pi - lon)
    
    lon_mean = pa + Pi - np.arctan2(A, B)
    lat_mean = np.arcsin(C)
    
    return lon_mean % (2.0 * np.pi), lat_mean

def get_nutation_in_longitude(T):
    """
    Computes nutation in longitude (delta_psi) in degrees using primary Delaunay terms [3, 25, 36].
    IAU 1980 / Meeus.
    """
    Omega = np.radians(125.04452 - 1934.136261 * T)
    L_sun = np.radians(280.4665 + 36000.7698 * T)
    L_moon = np.radians(218.3165 + 481267.8813 * T)
    
    delta_psi_arcsec = (
        -17.20 * np.sin(Omega)
        - 1.32 * np.sin(2.0 * L_sun)
        - 0.23 * np.sin(2.0 * L_moon)
        + 0.21 * np.sin(2.0 * Omega)
    )
    return delta_psi_arcsec / 3600.0

def format_zodiac(lon_deg):
    """
    Formats a decimal ecliptic longitude (0-360) into zodiac sign, degrees,
    minutes, and seconds of arc [27-31].
    """
    lon_deg = lon_deg % 360.0
    sign_idx = int(lon_deg // 30.0)
    sign_names = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_name = sign_names[sign_idx]
    deg_in_sign = lon_deg % 30.0
    
    D = int(deg_in_sign)
    dec_min = (deg_in_sign - D) * 60.0
    M = int(dec_min)
    S = int(round((dec_min - M) * 60.0))
    
    # Carry overs
    if S >= 60:
        S = 0
        M += 1
    if M >= 60:
        M = 0
        D += 1
    if D >= 30:
        D = 0
        sign_idx = (sign_idx + 1) % 12
        sign_name = sign_names[sign_idx]
        
    return {
        "sign_index": sign_idx,
        "sign_name": sign_name,
        "degrees": D,
        "minutes": M,
        "seconds": S,
        "string": f"{D:02d}° {sign_name:11s} {M:02d}' {S:02d}\""
    }

def calculate_geocentric_position(planet_name, T):
    """
    Returns true tropical geocentric longitude (degrees), latitude (degrees), and distance (AU) [3, 13, 18].
    """
    # 1. Heliocentric vectors in J2000.0 [3]
    vec_planet = get_heliocentric_j2000_vector(planet_name, T)
    vec_earth = get_heliocentric_j2000_vector('EMB', T)
    
    # 2. Translate to geocenter via subtraction [3, 13, 18]
    vec_geocentric = vec_planet - vec_earth
    x_g, y_g, z_g = vec_geocentric
    
    # 3. Spherical conversion (J2000.0 geocentric longitude/latitude) [3, 18]
    dist = np.linalg.norm(vec_geocentric)
    lon_j2000 = np.arctan2(y_g, x_g) % (2.0 * np.pi)
    lat_j2000 = np.arcsin(z_g / dist)
    
    # 4. Apply general precession from J2000 to Date [3, 21]
    lon_mean, lat_mean = precess_to_date(lon_j2000, lat_j2000, T)
    
    # 5. Apply lunisolar nutation in longitude to true equinox of date [3, 26]
    delta_psi = get_nutation_in_longitude(T)
    lon_true_deg = np.degrees(lon_mean) + delta_psi
    lat_true_deg = np.degrees(lat_mean)
    
    return lon_true_deg % 360.0, lat_true_deg, dist

def get_retrograde_status(planet_name, T, h_offset=1.0):
    """
    Determines if a planet is direct or retrograde by taking the coordinate
    velocity over a small time window (h_offset hours) [27, 32, 34].
    """
    lon1, _, _ = calculate_geocentric_position(planet_name, T)
    
    # T offset in Julian centuries
    dT = h_offset / (24.0 * 36525.0)
    lon2, _, _ = calculate_geocentric_position(planet_name, T + dT)
    
    diff = (lon2 - lon1) % 360.0
    if diff > 180.0:
        diff -= 360.0
        
    return "Retrograde" if diff < 0 else "Direct"

def get_chart(year, month, day, hour=0, minute=0, second=0, delta_t=69.2):
    """
    Calculates geocentric tropical zodiac positions for all standard bodies [3].
    """
    jd = calendar_to_jd(year, month, day, hour, minute, second)
    T = jd_to_T(jd, delta_t)
    
    results = {}
    for body in STANDISH_ELEMENTS.keys():
        if body == 'EMB':
            continue  # EMB is Earth, the geocentric observation point [35]
            
        lon, lat, dist = calculate_geocentric_position(body, T)
        motion = get_retrograde_status(body, T)
        zodiac_fmt = format_zodiac(lon)
        
        results[body] = {
            "longitude": lon,
            "latitude": lat,
            "distance": dist,
            "retrograde": motion,
            "zodiac": zodiac_fmt
        }
    return jd, T, results

if __name__ == "__main__":
    print("=" * 75)
    print("        ASTRONOMICAL COORDINATE CALCULATOR - WESTERN HOROSCOPE ENGINE")
    print("=" * 75)
    
    # Worked verification: Mars, October 15, 2024 at 00:00 UTC [3]
    year, month, day, hour = 2024, 10, 15, 0
    delta_t = 69.2  # standard delta T for 2024 [3]
    
    print(f"Calculating for Epoch: {year}-{month:02d}-{day:02d} {hour:02d}:00:00 UTC")
    jd = calendar_to_jd(year, month, day, hour)
    T = jd_to_T(jd, delta_t)
    print(f"Computed Julian Date (UTC) : {jd:.4f}")
    print(f"Computed Terrestrial Time T: {T:.9f} Julian centuries since J2000.0")
    print("-" * 75)
    
    # Verify Earth (EMB) J2000 coordinates (heliocentric, J2000 ecliptic)
    emb_vec = get_heliocentric_j2000_vector('EMB', T)
    print("EM Barycenter Heliocentric Vector J2000 (AU):")
    print(f"  X: {emb_vec[0]:.7f}")
    print(f"  Y: {emb_vec[1]:.7f}")
    print(f"  Z: {emb_vec[2]:.7f}")
    
    # Verify Mars J2000 coordinates
    mars_vec = get_heliocentric_j2000_vector('Mars', T)
    print("\nMars Heliocentric Vector J2000 (AU):")
    print(f"  X: {mars_vec[0]:.7f}")
    print(f"  Y: {mars_vec[1]:.7f}")
    print(f"  Z: {mars_vec[2]:.7f}")
    
    # Geocentric vectors
    geocentric_vec = mars_vec - emb_vec
    print("\nMars Geocentric Vector J2000 (AU):")
    print(f"  X: {geocentric_vec[0]:.7f}")
    print(f"  Y: {geocentric_vec[1]:.7f}")
    print(f"  Z: {geocentric_vec[2]:.7f}")
    
    # Final Mars results [41, 42]
    lon, lat, dist = calculate_geocentric_position('Mars', T)
    zod = format_zodiac(lon)
    motion = get_retrograde_status('Mars', T)
    
    print("\nMars Final Spherical Tropical Coordinates:")
    print(f"  Tropical Longitude: {lon:.6f}° (Expected Mean: 111.794261°, True: 111.793551°)")
    print(f"  Ecliptic Latitude : {lat:.6f}° (Expected: 1.209581°)")
    print(f"  Distance to Earth : {dist:.6f} AU")
    print(f"  Astrological Ingress: {zod['string']} ({motion})")
    print("-" * 75)
    
    # Generate complete planetary positions
    print("\nGENERATING FULL ASTROLOGICAL CHART (TROPICAL ECLIPTIC OF DATE):")
    print(f"{'Planet':<12} {'Tropical Zodiac Position':<25} {'Motion':<12} {'Distance (AU)':<12}")
    print("-" * 75)
    
    jd, T, chart = get_chart(year, month, day, hour, delta_t=delta_t)
    for planet, info in chart.items():
        print(f"{planet:<12} {info['zodiac']['string']:<25} {info['retrograde']:<12} {info['distance']:>10.4f} AU")
    print("=" * 75)

