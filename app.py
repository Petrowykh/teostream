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
    st.subheader('Акты наемных водителей')
    placeholder = st.empty()
    time.sleep(5)
    # Replace the placeholder with some text:
    placeholder.text("Hello")
    time.sleep(5)
    # Replace the text with a chart:
    placeholder.line_chart({"data": [1, 5, 2, 6]})
    time.sleep(5)
    # Replace the chart with several elements:
    with placeholder.container():
        st.write("This is one element")
        st.write("This is another")
    time.sleep(5)
    # Clear all those elements:
    placeholder.empty()

######### Trips ############
def trips_create():

    
    route_flag = False
    route_flag_Minsk = False
    
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
    trip_check_our = st.sidebar.checkbox('Наемный')
    
    trip_driver = st.sidebar.selectbox('Выберите водителя', tsdb.get_name(trip_check_our, 'водитель'))
    trip_car = st.sidebar.selectbox('Выберите машину', tsdb.get_number_car(trip_check_our, trip_driver)[0], index=tsdb.get_number_car(trip_check_our, trip_driver)[1])
    trip_route = 0
    trip_forwarder = 0
    trip_route = st.sidebar.number_input('Номер путевого', format="%d", value=int(tsdb.get_last_route())+1, disabled=trip_check_our)
    trip_check_forwarder = st.sidebar.checkbox('Экспедитор', disabled=trip_check_our)
    if trip_check_forwarder:
        trip_forwarder = st.sidebar.selectbox('Выберите экспедитора', tsdb.get_name(trip_check_our, 'экспедитор'))
        trip_forwarder = tsdb.get_id_emplyee(trip_forwarder)
    
    if st.sidebar.button('Добавить'):
        tsdb.add_trips(trip_route, trip_date, tsdb.get_id_emplyee(trip_driver), trip_days, trip_town, tsdb.get_id_car(trip_car), trip_check_our, trip_forwarder)
        if trip_town == 'Минск':
            route_flag_Minsk = True
        else:
            route_flag = True
    st.text(f'Командировки на : {trip_date}')
    table_trips = st.empty()
    table_trips.table(tsdb.get_trips_of_date(trip_date, False))

    if st.button('Уведомение', disabled=tsdb.get_status_message(trip_date, False)):
        st.text('Send')

    st.text(f'Минск на : {trip_date}')
    table_trips = st.empty()
    table_trips.table(tsdb.get_trips_of_date(trip_date, True))
    
    if st.button('Уведомение по Минску', disabled=tsdb.get_status_message(trip_date, True)):
        st.text('Send')

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



