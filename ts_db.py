import sqlite3


class Teo_DB:

    def __init__(self, db_file) -> None:
        self.connection = sqlite3.connect(database=db_file)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def get_ten(self):
        # first 50 records
        with self.connection:
            return self.cursor.execute("SELECT * FROM trip LIMIT 10").fetchall()
    
    def get_id_emplyee(self, name):
        with self.connection:
            return self.cursor.execute(f"SELECT id FROM employees WHERE fullname='{name}'").fetchone()[0]

    def get_id_car(self, number):
        with self.connection:
            return self.cursor.execute(f"SELECT id FROM cars WHERE car_number='{number}'").fetchone()[0]

    def get_name(self, our, position):
        l = []
        with self.connection:
            for i in self.cursor.execute(f"SELECT fullname FROM employees WHERE position='{position}' AND our={not(our)}").fetchall():
                #print(i)
                l.append(str(i).split("'")[1])
            return l
    
    def get_number_car(self, our, name):
        l = []
        with self.connection:
            car = self.cursor.execute(f"SELECT car_number FROM cars WHERE owner={int(self.get_id_emplyee(name))}").fetchone()[0]
            for i in self.cursor.execute(f"SELECT car_number FROM cars WHERE our={not(our)}").fetchall():
                l.append(str(i).split("'")[1])
            try:
                index_car = l.index(car)
            except:
                index_car = 0
            return l, index_car

    def get_last_route(self):
        with self.connection:
            return self.cursor.execute("SELECT max(route) FROM trips WHERE NOT act_ok").fetchone()[0]

    def add_trips(self, route, date_route, driver, days, direction, car_id, act_ok, forwarder):
        with self.connection:
            return self.cursor.execute("INSERT INTO trips (route, date_route, driver, days, direction, car_id, act_ok, forwarder) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
            (route, date_route, driver, days, direction, car_id, act_ok, forwarder))

    def get_trips_of_date(self, date, flag_trip):
        key_word = '=' if flag_trip else '<>'
        with self.connection:
            trips = self.cursor.execute(f"SELECT trips.direction, employees.fullname, cars.car_number     FROM trips, employees, cars WHERE employees.fullname = (SELECT fullname FROM employees WHERE employees.id = trips.driver) AND cars.car_number = (SELECT car_number FROM cars WHERE cars.id = trips.car_id) AND trips.date_route = '{date}' AND trips.direction {key_word} 'Минск'").fetchall() 
        if trips != None:
            return trips
        else:
            return 'Рейсов не запланировано'

    def get_status_message(self, date, flag_trip):
        key_word = '=' if flag_trip else '<>'
        with self.connection:
            status = self.cursor.execute(f"SELECT min(trips.ready) FROM trips WHERE trips.date_route = '{date}' AND trips.direction {key_word} 'Минск'").fetchone()[0]
        if status == None:
            status = True
        return status