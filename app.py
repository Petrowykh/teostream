
import streamlit as st
#from multipage import MultiPage
import datetime
from streamlit_option_menu import option_menu

from apps import timesheets, acts, trips

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



