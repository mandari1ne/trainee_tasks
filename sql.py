import sqlite3 as sl
import json

con = sl.connect('airport.db')

with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            municipality VARCHAR(50),
            name VARCHAR(50) NOT NULL,
            type VARCHAR(50) NOT NULL
        );
    """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS geolocation (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                continent VARCHAR(50) NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                elevation_ft VARCHAR(50),
                airport_id INTEGER NOT NULL,
                FOREIGN KEY (airport_id) REFERENCES airports(id) ON DELETE CASCADE 
            );
        """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS code_list (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                iso_country VARCHAR(25),
                iso_region VARCHAR(25),
                local_code VARCHAR(25),
                gps_code VARCHAR(25),
                iata_code VARCHAR(25),
                ident VARCHAR(25),
                airport_id INTEGER NOT NULL,
                FOREIGN KEY (airport_id) REFERENCES airports(id) ON DELETE CASCADE
            );
        """)

    con.commit()

# with open('airport-codes_json (1).json', 'r') as file:
#     data = json.load(file)
#
#     with con:
#         for airports in data:
#             cur = con.cursor()
#
#             cur.execute(
#                 '''INSERT INTO airports (municipality, name, type) VALUES(?, ?, ?)''',
#                 (
#                     airports.get('municipality'),
#                     airports.get('name'),
#                     airports.get('type'),
#                 )
#             )
#
#             airport_id = cur.lastrowid
#
#             coords = airports.get('coordinates', '').split(',')
#             if len(coords) == 2:
#                 longitude = float(coords[0].strip())
#                 latitude = float(coords[1].strip())
#             else:
#                 longitude = latitude = 0.0
#
#             cur.execute(
#                 '''INSERT INTO geolocation (
#                         continent, latitude, longitude, elevation_ft, airport_id
#                     ) VALUES(?, ?, ?, ?, ?)''',
#                 (
#                     airports.get('continent'),
#                     latitude,
#                     longitude,
#                     airports.get('elevation_ft'),
#                     airport_id
#                 )
#             )
#
#             cur.execute(
#                 '''INSERT INTO code_list (
#                         iso_country, iso_region, local_code, gps_code, iata_code, ident, airport_id
#                     ) VALUES(?, ?, ?, ?, ?, ?, ?)''',
#                 (
#                     airports.get('iso_country'),
#                     airports.get('iso_region'),
#                     airports.get('local_code'),
#                     airports.get('gps_code'),
#                     airports.get('iata_code'),
#                     airports.get('ident'),
#                     airport_id
#                 )
#             )
#
#         con.commit()

def get_heliport():
    with con:
        cur = con.cursor()

        cur.execute('''
            SELECT municipality, name FROM airports WHERE type = 'heliport'
        ''')

        print('Вертолетные аэропорты:')
        count = 0
        for row in cur.fetchall():
            print(row[0], ' - ', row[1])
            count += 1

        if count == 0:
            print('Информация не найдена')

# get_heliport()

def get_airport_by_geolocation(x1, y1, x2, y2, type=None):
    with con:
        cur = con.cursor()

        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)

        if type:
            cur.execute('''
                SELECT a.municipality, a.name 
                FROM airports a
                JOIN geolocation g 
                ON a.id = g.airport_id
                WHERE g.longitude BETWEEN ? AND ?
                  AND g.latitude BETWEEN ? AND ?
                  AND a.type = ?
            ''',
            (min_x, max_x, min_y, max_y, type))
        else:
            cur.execute('''
                SELECT a.municipality, a.name 
                FROM airports a
                JOIN geolocation g ON a.id = g.airport_id
                WHERE g.longitude BETWEEN ? AND ?
                  AND g.latitude BETWEEN ? AND ?
            ''',
            (min_x, max_x, min_y, max_y))

        print(f'Аэропорты в диапазоне ({x1, y1}) - ({x2, y2}):')
        airports = cur.fetchall()

        if airports:
            for municipality, name in airports:
                print(f"{municipality} - {name}")
        else:
            print('Информация не найдена')


# get_airport_by_geolocation(-74.93360137939453, 40.07080078125, -101.473911, 38.704022, 'heliport')

def insert_new_data(data):
    required_fields = ['name', 'type', 'iso_country', 'iso_region', 'coordinates']

    if isinstance(data, dict):
        data = [data]

    with con:
        cur = con.cursor()

        for airport in data:
            if not all(field in airport and airport[field] for field in required_fields):
                print('Информация не записана')
                continue

            longitude, latitude = map(float, airport['coordinates'].split(','))

            cur.execute('''
                INSERT INTO airports (municipality, name, type)
                VALUES (?, ?, ?)
            ''',
            (airport.get('municipality'), airport['name'], airport['type'])
            )
            airport_id = cur.lastrowid

            cur.execute('''
                INSERT INTO geolocation (continent, longitude, latitude, elevation_ft, airport_id)
                VALUES (?, ?, ?, ?, ?)
            ''',
            (airport.get('continent'), longitude, latitude, airport.get('elevation_ft'), airport_id)
            )

            cur.execute('''
                INSERT INTO code_list (
                iso_country, iso_region, local_code, gps_code, iata_code, ident, airport_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                airport['iso_country'],
                airport['iso_region'],
                airport.get('local_code'),
                airport.get('gps_code'),
                airport.get('iata_code'),
                airport.get('ident'),
                airport_id
            ))

# insert_new_data({'municipality': 'CHECK', 'name': 'CHECK', 'type': 'CHECK',
#                  'continent': 'CHECK', 'coordinates': '0.0, 0.0', 'elevation_ft': 'CHECK',
#                  'iso_country': 'CHECK', 'iso_region': 'CHECK',
#                  'local_code': 'CHECK', 'gps_code': 'CHECK', 'iata_code': 'CHECK',
#                  'ident': 'CHECK'})

def insert_new_data_with_printing(data):
    required_fields = ['name', 'type', 'iso_country', 'iso_region', 'coordinates']

    if isinstance(data, dict):
        data = [data]

    with con:
        cur = con.cursor()

        for airport in data:
            if not all(field in airport and airport[field] for field in required_fields):
                print('Информация не записана')
                continue

            longitude, latitude = map(float, airport['coordinates'].split(','))

            cur.execute('''
                INSERT INTO airports (municipality, name, type)
                VALUES (?, ?, ?)
            ''',
            (airport.get('municipality'), airport['name'], airport['type'])
            )
            airport_id = cur.lastrowid

            cur.execute('''
                INSERT INTO geolocation (continent, longitude, latitude, elevation_ft, airport_id)
                VALUES (?, ?, ?, ?, ?)
            ''',
            (airport.get('continent'), longitude, latitude, airport.get('elevation_ft'), airport_id)
            )

            cur.execute('''
                INSERT INTO code_list (
                iso_country, iso_region, local_code, gps_code, iata_code, ident, airport_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                airport['iso_country'],
                airport['iso_region'],
                airport.get('local_code'),
                airport.get('gps_code'),
                airport.get('iata_code'),
                airport.get('ident'),
                airport_id
            ))

            print(airport['municipality'], ' - ' ,airport['name'], ' - ' , airport['type'], ' - ' ,
                  airport['continent'], ' - ' , longitude, latitude, ' - ' , airport['elevation_ft'],
                  ' - ' , airport['iso_country'], ' - ' , airport['iso_region'], ' - ' ,
                  airport.get('local_code'), ' - ' ,
                  airport.get('gps_code'), ' - ' , airport.get('iata_code'), ' - ' ,
                  airport.get('ident'),
                  )

# insert_new_data_with_printing({'municipality': 'CHECK1', 'name': 'CHECK1', 'type': 'CHECK1',
#                  'continent': 'CHECK1', 'coordinates': '0.0, 0.0', 'elevation_ft': 'CHECK1',
#                  'iso_country': 'CHECK1', 'iso_region': 'CHECK1',
#                  'local_code': 'CHECK1', 'gps_code': 'CHECK1', 'iata_code': 'CHECK1',
#                  'ident': 'CHECK1'})

def get_airports_by_params(params):
    with con:
        cur = con.cursor()

        query = '''
                    SELECT a.municipality, a.name, a.type, 
                           g.longitude, g.latitude, 
                           c.iso_country, c.iso_region
                    FROM airports a
                    JOIN geolocation g ON a.id = g.airport_id
                    JOIN code_list c ON a.id = c.airport_id
                    WHERE 1=1
                '''

        param = []

        field_mapping = {
            'type': ('a.type', '='),
            'iso_country': ('c.iso_country', '='),
            'iso_region': ('c.iso_region', '='),
            'local_code': ('c.local_code', '='),
            'gps_code': ('c.gps_code', '='),
            'iata_code': ('c.iata_code', '='),
            'ident': ('c.ident', '='),
            'name': ('a.name', 'LIKE'),
            'municipality': ('a.municipality', 'LIKE')
        }

        for field, value in params.items():
            if field in field_mapping:
                column, operator = field_mapping[field]

                if operator == 'LIKE':
                    query += f' AND {column} LIKE ?'
                    param.append(f"%{value}%")
                else:
                    query += f' AND {column} {operator} ?'
                    param.append(value)

        while True:
            print('Хочешь ввести диапазаон коодинат? (y/n)')
            res = input().lower()

            if res == 'y':
                x1 = float(input('x1: '))
                y1 = float(input('y1: '))
                x2 = float(input('x2: '))
                y2 = float(input('y2: '))

                min_x = min(x1, x2)
                max_x = max(x1, x2)
                min_y = min(y1, y2)
                max_y = max(y1, y2)

                query += ' AND g.longitude BETWEEN ? AND ? AND g.latitude BETWEEN ? AND ?'
                param.append(min_x)
                param.append(max_x)
                param.append(min_y)
                param.append(max_y)

                break

            elif res == 'n':
                break

            else:
                print('Неверный ввод!')

        cur.execute(query, param)
        airports = cur.fetchall()

        if not airports:
            print("\nАэропорты не найдены")
        else:
            for airport in airports:
                print(airport)

# get_airports_by_params({'name': 'Total Rf Heliport', 'iso_country': 'US'})
# get_airports_by_params({'ident': '00A', 'iso_country': 'US', 'gps_code': '00A'})
