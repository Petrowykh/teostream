import time
import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import config_ini
from ts_db import Teo_DB

from utils import utils

######### Read Config.ini #########
path = "config.ini"
    # font = get_setting(path, 'Settings', 'font')
    # font_size = get_setting(path, 'Settings', 'font_size')
    
    # update_setting(path, "Settings", "font_size", "12")
    # delete_setting(path, "Settings", "font_style")

PATH_DB = config_ini.get_setting(path, 'db_local', 'PATH_DB')
NAME_DB = config_ini.get_setting(path, 'db_local', 'NAME_DB')

try:
    tsdb = Teo_DB(PATH_DB+NAME_DB)
    print ('Connection - Ok')
except Exception as e:
    print (f'Error {e}')


######### TimeSheets #########
def timesheets_create():
    st.subheader('Табель')
    choose = st.sidebar.selectbox('Выберите отдел ЛУ',
                        ('Логистика', 'Мезонин', 'Транспортный'))
    if st.sidebar.button('Показать') == True:
        components.html(utils.draw_table(), height=300, scrolling=True)

######### Acts ##########
def acts_create():
    summa = 0
    st.subheader('Акты наемных водителей')
    
    act_organization = st.sidebar.selectbox('Организация', tsdb.get_list_organization())
    act_driver = st.sidebar.selectbox('Водитель', tsdb.get_list_driver(act_organization))
    act_date = st.sidebar.selectbox('Выберите дату', tsdb.get_list_date(act_driver))
    print(tsdb.get_list_driver(act_organization), tsdb.get_list_date(act_driver))
    act_table = st.empty()
    df_acttable = tsdb.get_act_of_DD(act_date, act_driver)
    act_table.table(df_acttable)
    print (df_acttable)
    act_idcar = tsdb.get_id_car(df_acttable['Машина'][0])
    params = list(tsdb.get_param(act_idcar))
    if df_acttable['Направление'][0] == 'Минск':
        act_hour = st.sidebar.slider('Количетсво часов', 4, 12, 8, 1)
        summa = int(act_hour) * float(params[1])
        
    else:
        if st.sidebar.checkbox('Закрыть часами', False):
        #print(tsdb.get_param(act_idcar))
            act_hour = st.sidebar.slider('Количетсво часов', 4, 12, 8, 1)
            summa = int(act_hour) * float(params[1])
        else:
            act_km = st.sidebar.number_input('Километраж')
            print(int(act_km), list(tsdb.get_param(act_idcar))[0])
            summa = int(act_km) * float(params[0])
    if df_acttable['Направление'][0] == 'Минск' and act_hour != 0:
        price = float(params[1])
        unit = act_hour
    else:
        price = float(params[0])
        unit = act_km
    st.sidebar.text(f'Сумма {summa}')
    if st.sidebar.button('Сохранить'):
        tsdb.add_acts(tsdb.get_id_trip(act_date, act_idcar), price, unit, summa)
        act_table.empty()
        st.info('Акт сохранен')

######### Trips ############
def trips_create():
    st.subheader('Рейсы')
    trip_date = st.sidebar.date_input('Дата рейса', datetime.now()+timedelta(days=1))

    trip_check_town = st.sidebar.checkbox('Командировка')
    trip_town = 'Минск'
    if trip_check_town:
        trip_town = st.sidebar.text_input('Маршрут', placeholder='Введите города через пробел')
        trip_days = st.sidebar.slider(
            'Количество дней командировки',
            1, 3, (1))
    else:
        trip_town = 'Минск'
        trip_days = 1
    trip_check_our = st.sidebar.checkbox('Наемный', value=True)
    trip_driver = st.sidebar.selectbox('Выберите водителя', tsdb.get_name(trip_check_our, 'водитель', trip_date))
    trip_car = st.sidebar.selectbox('Выберите машину', tsdb.get_number_car(trip_check_our, trip_driver)[0], index=tsdb.get_number_car(trip_check_our, trip_driver)[1])
    trip_route = 0
    trip_forwarder = 0
    if not(trip_check_our):
        trip_route = st.sidebar.number_input('Номер путевого', format="%d", value=int(tsdb.get_last_route())+1, disabled=trip_check_our)
    trip_check_forwarder = st.sidebar.checkbox('Экспедитор', disabled=trip_check_our)
    if trip_check_forwarder:
        
        trip_forwarder_name = st.sidebar.selectbox('Выберите экспедитора', tsdb.get_name(trip_check_our, 'экспедитор'))
        trip_forwarder = tsdb.get_id_emplyee(trip_forwarder_name)
    
    if st.sidebar.button('Добавить'):
        tsdb.add_trips(trip_route, trip_date, tsdb.get_id_emplyee(trip_driver), trip_days, trip_town, tsdb.get_id_car(trip_car), trip_check_our, trip_forwarder)
        st.info('Рейс добавлен')
        
    st.text(f'Командировки на : {trip_date}')
    table_trips = st.empty()
    table_trips.table(tsdb.get_trips_of_date(trip_date, False))

    if st.button('Уведомение', disabled=tsdb.get_status_message(trip_date, False)):
        table_trips.info('Sending...')
        progress_send = table_trips.progress(0)
        percent_complite = 0
        len_complite = len(tsdb.get_info_sms(trip_date, False))
        for sm in tsdb.get_info_sms(trip_date, False):
            percent_complite = percent_complite+int(100/len_complite)
            progress_send.progress(percent_complite)
            
            if sm[5]:
                sms_driver = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_firstname(sm[5])}'
                phone_driver = tsdb.get_phone(sm[0])
                #send sms
                print(f'Driver Number {phone_driver} text {sms_driver}')
                sms_forwarder = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_firstname(sm[0])}'
                phone_forwarder = tsdb.get_phone(sm[5])
                print(f'Forwarder Number {phone_forwarder} text {sms_forwarder}')
            else:
                sms_driver = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} без экспедитора'
                phone_driver = tsdb.get_phone(sm[0])
                #send sms
                print(f'Driver Number {phone_driver} text {sms_driver}')
            tsdb.update_status_ready(sm[6])
        table_trips.table(tsdb.get_trips_of_date(trip_date, False))
            
        
    st.text(f'Минск на : {trip_date}')
    table_trips = st.empty()
    table_trips.table(tsdb.get_trips_of_date(trip_date, True))
    
    if st.button('Уведомение по Минску', disabled=tsdb.get_status_message(trip_date, True)):
        table_trips.info('Sending...')
        progress_send = table_trips.progress(0)
        percent_complite = 0
        len_complite = len(tsdb.get_info_sms(trip_date, True))
        for sm in tsdb.get_info_sms(trip_date, True):
            percent_complite = percent_complite+int(100/len_complite)
            progress_send.progress(percent_complite)
            
            if sm[5]:
                sms_driver = f'{sm[1]} {sm[2]} Минск {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_firstname(sm[5])}'
                phone_driver = tsdb.get_phone(sm[0])
                #send sms
                print(f'Driver Number {phone_driver} text {sms_driver}')
                sms_forwarder = f'{sm[1]} {sm[2]} Минск {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_firstname(sm[0])}'
                phone_forwarder = tsdb.get_phone(sm[5])
                print(f'Forwarder Number {phone_forwarder} text {sms_forwarder}')
            else:
                sms_driver = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} без экспедитора'
                phone_driver = tsdb.get_phone(sm[0])
                #send sms
                print(f'Driver Number {phone_driver} text {sms_driver}')
            tsdb.update_status_ready(sm[6])
        table_trips.table(tsdb.get_trips_of_date(trip_date, True))

st.set_page_config(
    page_title='Информационная система',
    page_icon="🧊",
    layout="wide")
     
st.title('Информационная система')
st.text(f'Сегодня {str(datetime.now())}')

selected = option_menu(
    menu_title='Главное меню',
    options=['Табель', 'Командировки', 'Акты', 'Настройки'],
    icons=['calendar-range', 'alarm', 'card-checklist', 'tools'],
    orientation='horizontal',
    default_index=0,
    )

if selected == 'Табель':
    timesheets_create()
if selected == 'Командировки':
    trips_create()
if selected == 'Акты':
    acts_create()



