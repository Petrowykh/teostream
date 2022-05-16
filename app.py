
import streamlit as st
import datetime, configparser
from streamlit_option_menu import option_menu

from apps import timesheets, acts, trips
import config_ini
from ts_db import Teo_DB



######### Read Config.ini #########
path = "config.ini"
    # font = get_setting(path, 'Settings', 'font')
    # font_size = get_setting(path, 'Settings', 'font_size')
    
    # update_setting(path, "Settings", "font_size", "12")
    # delete_setting(path, "Settings", "font_style")

PATH_DB = config_ini.get_setting(path, 'db_local', 'PATH_DB')
NAME_DB = config_ini.get_setting(path, 'db_local', 'NAME_DB')




######### Connect DB #########
try:
    tsdb = Teo_DB(PATH_DB+NAME_DB)
    print ('Connection - Ok')
except Exception as e:
    print (f'Error {e}')



st.set_page_config(
     page_title='Инофрмационная система ЛУ',
     page_icon="🧊",
     layout="wide")
     
st.title('Инофрмационная система ЛУ')
st.text(f'Сегодня {str(datetime.datetime.now())}')

selected = option_menu(
    menu_title='Главное меню',
    options=['Табель', 'Командировки', 'Акты', 'Настройки'],
    icons=['calendar-range', 'alarm', 'card-checklist', 'tools'],
    orientation='horizontal',
    default_index=0,
    )

if selected == 'Табель':
    timesheets.app()
if selected == 'Командировки':
    trips.app()
if selected == 'Акты':
    acts.app()



