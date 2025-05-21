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
                coordinates VARCHAR(50) NOT NULL,
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

with open('airport-codes_json (1).json', 'r') as file:
    data = json.load(file)

    with con:
        for airports in data:
            cur = con.cursor()

            cur.execute(
                '''INSERT INTO airports (municipality, name, type) VALUES(?, ?, ?)''',
                (
                    airports.get('municipality'),
                    airports.get('name'),
                    airports.get('type'),
                )
            )

            airport_id = cur.lastrowid

            cur.execute(
                '''INSERT INTO geolocation (
                        continent, coordinates, elevation_ft, airport_id
                    ) VALUES(?, ?, ?, ?)''',
                (
                    airports.get('continent'),
                    airports.get('coordinates'),
                    airports.get('elevation_ft'),
                    airport_id
                )
            )

            cur.execute(
                '''INSERT INTO code_list (
                        iso_country, iso_region, local_code, gps_code, iata_code, ident, airport_id
                    ) VALUES(?, ?, ?, ?, ?, ?, ?)''',
                (
                    airports.get('iso_country'),
                    airports.get('iso_region'),
                    airports.get('local_code'),
                    airports.get('gps_code'),
                    airports.get('iata_code'),
                    airports.get('ident'),
                    airport_id
                )
            )

        con.commit()
