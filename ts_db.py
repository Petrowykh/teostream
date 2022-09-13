from datetime import timedelta, datetime
from multiprocessing import connection
import sqlite3, json
from debugpy import connect
import pandas as pd

MONTH_TIMESHEETS = {1:'jan', 2:'feb', 3:'mar', 4:'apr', 5:'may', 6:'jun', 7:'jul', 8:'aug', 9:'sep', 10:'oct', 11:'nov', 12:'dec'}

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

    def commit(self):
        self.connection.commit()

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
    
    def check_our(self, id):
        with self.connection:
            if self.cursor.execute(f"SELECT our FROM employees WHERE id='{id}'").fetchone()[0]:
                return True
            else:
                return False

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

    def get_organization(self, id):
        """
        Get first name + IO
        Args:
            id 
        Returns:
            Колесень А.Л.
        """
        return self.get_any_q1('organization', 'employees', 'id', id)
           

    def get_name(self, our, position, date):
        l = []
        with self.connection:
            for i in self.cursor.execute(f"SELECT fullname FROM employees WHERE employees.position='{position}' AND employees.our={not(our)} AND active EXCEPT SELECT fullname FROM employees e WHERE id in (SELECT t.driver FROM trips t WHERE t.date_route='{date}' OR (t.date_route='{date-timedelta(days=1)}' AND days = 2)) ORDER BY fullname").fetchall():
                l.append(str(i).split("'")[1])
        return l

    def get_number_car(self, our, name):
        l = []
        with self.connection:
            car = self.cursor.execute(f"SELECT car_number FROM cars WHERE owner={int(self.get_id_employee(name))} AND active").fetchone()[0]
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

    ############## def for data #############
    def get_data_cars(self):
        cars = self.cursor.execute("SELECT * FROM cars").fetchall()
        df = pd.DataFrame(cars, columns=['id', 'Название', 'Госномер', 'Собственность', 'Цена за км', 'Цена за час', 'В работе', 'Владелец']).fillna(0)
        df['Владелец'] = df['Владелец'].apply(lambda x: self.get_organization(x) if x != 0 else '')
        df['Собственность'] = df['Собственность'].apply(lambda x: '\u2714' if x else '\u274C')
        df['В работе'] = df['В работе'].apply(lambda x: '\u2714' if x else '\u274C')
        return df
    
    def delete_trip(self, id):
        with self.connection:
            self.cursor.execute(f"DELETE FROM trips WHERE id = '{id}'")
            self.commit()
    
    def update_cars(self, id, price_km, price_hour, active):
        with self.connection:
            self.cursor.execute(f"UPDATE cars SET price_km={price_km}, price_hour = {price_hour}, active={active} WHERE id = {id}")

    def get_trips_of_date_for_delete(self, date):
        with self.connection:
            trips = self.cursor.execute(f"SELECT id, route, direction, driver, forwarder FROM trips WHERE date_route = '{date}' ORDER BY direction").fetchall()  
        df = pd.DataFrame(trips, columns=['id', 'Путевой', 'Направление', 'Водитель', 'Экспедитор'])
        df['Путевой'] = df['Путевой'].apply(lambda x: x if x != '0' else 'б/н')
        df['Водитель'] = df['Водитель'].apply(lambda x: self.get_FIO(x) if x != 0 else '')
        df['Экспедитор'] = df['Экспедитор'].apply(lambda x: self.get_FIO(x) if x != 0 else '')
        if trips != None:
            return df
        else:
            return 'Рейсов не запланировано'     
    
    ########### Report ##############
    def get_trips_of_month(self, id_employees, month, d_or_f=True):
        list_dd = []
        if d_or_f:
            with self.connection:
                for i in self.cursor.execute(f"SELECT date_route, days FROM trips WHERE strftime('%m', date_route) = '{month}' AND direction<>'Минск' AND driver={id_employees} ORDER BY date_route").fetchall():
                    list_dd.append(i)
        else:
            with self.connection:
                for i in self.cursor.execute(f"SELECT date_route, days FROM trips WHERE strftime('%m', date_route) = '{month}' AND direction<>'Минск' AND forwarder={id_employees} ORDER BY date_route").fetchall():
                    list_dd.append(i)

        return list_dd
    
    def get_list_id_our(self, month, d_or_f=True):
        l = []
        if d_or_f:
            with self.connection:
                for i in self.cursor.execute(f"SELECT DISTINCT driver FROM trips WHERE strftime('%m', date_route) = '{month}' AND driver in (SELECT id FROM employees WHERE our) AND direction<>'Минск'").fetchall():
                    l.append(i[0])
        else:
            with self.connection:
                for i in self.cursor.execute(f"SELECT DISTINCT forwarder FROM trips WHERE strftime('%m', date_route) = '{month}' AND forwarder AND direction<>'Минск'").fetchall():
                    l.append(i[0])
        print(l)
        return l
    
    ########### Timesheets ##############
    def get_dd(self, month, div):
        
        l = []
        name_month = MONTH_TIMESHEETS[month]
        with self.connection:
            for i in self.cursor.execute(f"SELECT employee, {name_month} FROM timesheets WHERE employee in (SELECT id FROM employees WHERE division='{div}')").fetchall():
                dop = [self.get_FIO(i[0]), *json.loads(i[1])]
                
                l.append(dop)
                l = sorted(l, key=lambda x:x[0])
        return l
    
    def get_info_trip_ts(self, id):
        with self.connection:
            return self.cursor.execute(f"SELECT date_route, driver, forwarder FROM trips WHERE id={id}").fetchone()

    def update_timesheets_df(self, id_employee, date_trips, d_or_f, option=True):
        #date_trips =date_trips.strftime('%Y-%m-%d')
        if option:
            hour = 8.0
            sym = 8
            dop_sym = 4
        else:
            hour = -8.0
            sym = 0
            dop_sym = 0
        with self.connection:
            if d_or_f:
                in_trips = self.cursor.execute(f"SELECT direction, days FROM trips WHERE driver={id_employee} and date_route='{date_trips}'").fetchone()
            else:
                in_trips = self.cursor.execute(f"SELECT direction, days FROM trips WHERE forwarder={id_employee} and date_route='{date_trips}'").fetchone()
            #print(in_trips)
            days_sheet = int(date_trips.split('-')[2])
            month_sheet = int(date_trips.split('-')[1])
            try:
                ts_data = json.loads(self.cursor.execute(f"SELECT {MONTH_TIMESHEETS[month_sheet]} from timesheets WHERE employee={id_employee}").fetchone()[0])
            except Exception as E:
                print(E)
                if ts_data == None:
                    print("Сделать месяц")
            
            if in_trips[0] == "Минск":
                ts_data[0] = float(ts_data[0]) + hour # add 8 hours
                ts_data[days_sheet+1] = sym
            elif in_trips[1] < 2:
                ts_data[0] = ts_data[0] + 8 # add 8 hours
                ts_data[days_sheet+1] = int(dop_sym/2)
            else:
                ts_data[0] = float(ts_data[0]) + hour*2 # add 8 hours
                ts_data[days_sheet+1] = int(dop_sym*2.25)
                ts_data[days_sheet+2] = int(dop_sym*2.25)
            #print (json.dumps(ts_data))
            self.cursor.execute(f"UPDATE timesheets SET {MONTH_TIMESHEETS[month_sheet]}='{json.dumps(ts_data)}' WHERE employee={id_employee}")


                       

        

