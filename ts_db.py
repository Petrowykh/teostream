from datetime import timedelta
import sqlite3
import pandas as pd


class Teo_DB:

    def __init__(self, db_file) -> None:
        """
        Connect DB and create cursor
        Args:
            db_file (_type_): Name of DB
        """
        self.connection = sqlite3.connect(database=db_file)
        self.cursor = self.connection.cursor()

    def close(self):
        """
        Close connection
        """
        self.connection.close()


    ############## def for trips pages ###############
    def get_any_q1(self, value, table, param, func):
        with self.connection:
            #print(f"SELECT {value} FROM {table} WHERE {param} = {func}")
            return self.cursor.execute(f"SELECT {value} FROM {table} WHERE {param} = '{func}'").fetchone()[0]
    
    def get_name_by_id(self, id):
        return self.get_any_q1('fullname', 'employees', 'id', id)

    def get_id_employee(self, name):
        return self.get_any_q1('id', 'employees', 'fullname', name)

    def get_id_car(self, number):
        return self.get_any_q1('id', 'cars', 'car_number', number)

    def get_number_car_clear(self, id):
        return self.get_any_q1('car_number', 'cars', 'id', id)
    
    def get_phone(self, id):
        return self.get_any_q1('phone', 'employees', 'id', id)
    
    def get_param(self, number):
        with self.connection:
            return self.cursor.execute(f"SELECT price_km, price_hour FROM cars WHERE id = '{number}'").fetchone()

    def get_firstname(self, id):
        """
        Not using
        """
        with self.connection:
            return self.cursor.execute(f"SELECT fullname FROM employees WHERE id='{id}'").fetchone()[0].split(' ')[0]
    
    def get_FIO(self, id):
        """
        Get first name + IO
        Args:
            id 
        Returns:
            Колесень А.Л.
        """
        fullname = self.get_any_q1('fullname', 'employees', 'id', id).split(' ')
        return f"{fullname[0]} {fullname[1][0]}.{fullname[2][0]}."    

    def get_name(self, our, position, date):
        l = []
        with self.connection:
            for i in self.cursor.execute(f"SELECT fullname FROM employees WHERE employees.position='{position}' AND employees.our={not(our)} AND active EXCEPT SELECT fullname FROM employees e WHERE id in (SELECT t.driver FROM trips t WHERE t.date_route='{date}' OR (t.date_route='{date-timedelta(days=1)}' AND days = 2)) ORDER BY fullname").fetchall():
                l.append(str(i).split("'")[1])
        return l

    def get_number_car(self, our, name):
        l = []
        with self.connection:
            car = self.cursor.execute(f"SELECT car_number FROM cars WHERE owner={int(self.get_id_employee(name))}").fetchone()[0]
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
            trips = self.cursor.execute(f"SELECT trips.route, trips.direction, trips.driver, cars.car_number, trips.forwarder, trips.ready FROM trips, cars WHERE cars.car_number = (SELECT car_number FROM cars WHERE cars.id = trips.car_id) AND trips.date_route = '{date}' AND trips.direction {key_word} 'Минск' ORDER BY trips.route").fetchall()  
        df = pd.DataFrame(trips, columns=['Путевой', 'Направление', 'Водитель', 'Машина', 'Экспедитор', 'sms'])
        df['sms'] = df['sms'].apply(lambda x: '\u2714' if x else '\u274C')
        df['Путевой'] = df['Путевой'].apply(lambda x: x if x != '0' else 'б/н')
        df['Водитель'] = df['Водитель'].apply(lambda x: self.get_FIO(x) if x != 0 else '')
        df['Экспедитор'] = df['Экспедитор'].apply(lambda x: self.get_FIO(x) if x != 0 else '')
        if trips != None:
            return df
        else:
            return 'Рейсов не запланировано'

    def get_status_message(self, date, flag_trip):
        key_word = '=' if flag_trip else '<>'
        with self.connection:
            status = self.cursor.execute(f"SELECT min(trips.ready) FROM trips WHERE trips.date_route = '{date}' AND trips.direction {key_word} 'Минск'").fetchone()[0]
        if status == None:
            status = True
        
        return status

    def get_info_sms(self, date, flag_trip):
        key_word = '=' if flag_trip else '<>'
        info = []
        with self.connection:
            for i in self.cursor.execute(f"SELECT driver, date_route, direction, days, car_id, forwarder, id, route FROM trips WHERE date_route = '{date}' AND trips.direction {key_word} 'Минск' AND not ready").fetchall():
                info.append(list(i))
        return info
    
    def update_status_ready(self, id):
        with self.connection:
            self.cursor.execute(f"UPDATE trips SET ready=True WHERE id={id}")

    ############ def for acts pages ############

    def get_list_organization(self):
        list_org = []
        with self.connection:
            for i in self.cursor.execute("SELECT DISTINCT organization FROM employees WHERE employees.id in (SELECT DISTINCT driver from trips where trips.act_ok=1 and trips.id not in (SELECT acts.id_trip from acts)) ORDER BY organization").fetchall():
                list_org.append(str(i).split("'")[1])
        return list_org
    
    def get_list_driver(self, organization):
        list_driver = []
        with self.connection:
            for i in self.cursor.execute(f"SELECT DISTINCT fullname FROM employees WHERE fullname in (SELECT fullname from employees WHERE organization = '{organization}') AND employees.id in (SELECT DISTINCT driver from trips where trips.act_ok=1 and trips.id not in (SELECT acts.id_trip from acts))").fetchall():
                list_driver.append(str(i).split("'")[1])
        return set(list_driver)

    def get_list_date(self, name):
        l = []
        id = self.get_id_employee(name)
        with self.connection:
            for i in self.cursor.execute(f"SELECT trips.date_route FROM trips where trips.driver ={int(id)} and trips.id not in (SELECT acts.id_trip from acts) ORDER BY trips.date_route").fetchall():
                l.append(str(i).split("'")[1])
            return l
    
    def get_act_of_DD(self, date, driver):
        with self.connection:
            acts = self.cursor.execute(f"SELECT trips.direction, employees.fullname, cars.car_number FROM trips, employees, cars WHERE employees.fullname = (SELECT fullname FROM employees WHERE employees.id = trips.driver) AND cars.car_number = (SELECT car_number FROM cars WHERE cars.id = trips.car_id) AND trips.date_route = '{date}' AND trips.driver = '{self.get_id_employee(driver)}'").fetchall() 
        df = pd.DataFrame(acts, columns=['Направление', 'Водитель', 'Машина'])
        
        return df
        
    def get_id_trip(self, date, car_id):
        with self.connection:
            return self.cursor.execute(f"SELECT id FROM trips WHERE car_id = '{car_id}' AND date_route = '{date}'").fetchone()[0]

    def add_acts(self, id_trip, price, unit, summa):
        with self.connection:
            return self.cursor.execute("INSERT INTO acts (id_trip, price, unit, summa) VALUES (?, ?, ?, ?)", 
            (int(id_trip), price, int(unit), summa))