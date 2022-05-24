import logging
import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import config_ini, utils
from ts_db import Teo_DB



######### Read Config.ini #########
path = "config.ini"

PATH_DB = config_ini.get_setting(path, 'db_local', 'path_db')
NAME_DB = config_ini.get_setting(path, 'db_local', 'name_db')
TOWN50 = config_ini.get_setting(path, 'town', 'town50').split(',')
logger = logging.basicConfig(filename='ts_log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


try:
    tsdb = Teo_DB(PATH_DB+NAME_DB)
except Exception as e:
    logger.warning(f'No connect DB {e}')


######### TimeSheets #########
def timesheets_create():
    """
    TimeSheet page
    """
    st.subheader('Табель')
    choose = st.sidebar.selectbox('Выберите отдел ЛУ',
                        ('Логистика', 'Мезонин', 'Транспортный'))
    if st.sidebar.button('Показать') == True:
        components.html(utils.draw_table(), height=300, scrolling=True)

######### Acts ##########
def acts_create():
    """
    Acts page
    """
    summa = 0 # defaul value summa
    st.subheader('Акты наемных водителей')
    act_organization = st.sidebar.selectbox('Организация', tsdb.get_list_organization())
    act_driver = st.sidebar.selectbox('Водитель', tsdb.get_list_driver(act_organization))
    act_date = st.sidebar.selectbox('Выберите дату', tsdb.get_list_date(act_driver))
    act_table = st.empty()
    df_acttable = tsdb.get_act_of_DD(act_date, act_driver)
    act_table.table(df_acttable)
    act_idcar = tsdb.get_id_car(df_acttable['Машина'][0])
    params = list(tsdb.get_param(act_idcar)) # price for cars
    if df_acttable['Направление'][0] == 'Минск':
        act_hour = st.sidebar.slider('Количество часов', 4, 12, 8, 1)
        st.sidebar.metric('Цена за 1 час', float(params[1]), delta_color="inverse")
        summa = int(act_hour) * float(params[1])
    else:
        if st.sidebar.checkbox('Закрыть часами', False):
            act_hour = st.sidebar.slider('Количество часов', 4, 12, 8, 1)
            st.sidebar.metric('Цена за 1 час', float(params[1]), delta_color="inverse")
            summa = int(act_hour) * float(params[1])
        else:
            act_km = st.sidebar.number_input('Километраж')
            act_hour = 0
            st.sidebar.metric('Цена за 1 км', float(params[0]), delta_color="inverse")
            summa = int(act_km) * float(params[0])
    if df_acttable['Направление'][0] == 'Минск' or act_hour != 0:
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
    """
    Trips page
    """
    st.subheader('Рейсы')
    trip_date = st.sidebar.date_input('Дата рейса', datetime.now()+timedelta(days=1))

    trip_check_town = st.sidebar.checkbox('Командировка')
    trip_town = 'Минск'
    if trip_check_town:
        trip_town = st.sidebar.text_input('Маршрут', placeholder='Введите города через пробел')
        trip_days = st.sidebar.slider('Количество дней командировки',
            1, 3, (1))
    else:
        trip_town = 'Минск'
        trip_days = 1
    trip_check_our = st.sidebar.checkbox('Наемный', value=True)
    list_driver = tsdb.get_name(trip_check_our, 'водитель', trip_date)
    if list_driver != []:
        trip_driver = st.sidebar.selectbox('Выберите водителя', tsdb.get_name(trip_check_our, 'водитель', trip_date))
        trip_car = st.sidebar.selectbox('Выберите машину', tsdb.get_number_car(trip_check_our, trip_driver)[0], index=tsdb.get_number_car(trip_check_our, trip_driver)[1])
        trip_route = 0
        trip_forwarder = 0
        if not(trip_check_our):
            trip_route = st.sidebar.number_input('Номер путевого', format="%d", value=int(tsdb.get_last_route())+1, disabled=trip_check_our)
            trip_check_forwarder = st.sidebar.checkbox('Экспедитор', disabled=trip_check_our)
        else:
            trip_check_forwarder = False
        if trip_check_forwarder:
            trip_forwarder_name = st.sidebar.selectbox('Выберите экспедитора', tsdb.get_name(trip_check_our, 'экспедитор', trip_date))
            trip_forwarder = tsdb.get_id_employee(trip_forwarder_name)
        if st.sidebar.button('Добавить'):
            tsdb.add_trips(trip_route, trip_date, tsdb.get_id_employee(trip_driver), trip_days, trip_town, tsdb.get_id_car(trip_car), trip_check_our, trip_forwarder)
            st.info('Рейс добавлен')
    else:
        st.sidebar.warning('Машин нет')
        
        
    st.text(f'Командировки на : {trip_date}')
    table_trips = st.empty()
    table_trips.table(tsdb.get_trips_of_date(trip_date, False))
    html_letter = '<font size="3" face="Tahoma">'
    html_letter = html_letter + 'Добрый день<BR>' + '<OL>'
    html_money = '<font size="3" face="Tahoma">'
    html_money = html_money + 'Добрый день!<BR>'
    if st.button('Уведомление', disabled=tsdb.get_status_message(trip_date, False)):
        progress_send = table_trips.progress(0)
        percent_complite = 0
        len_complite = len(tsdb.get_info_sms(trip_date, False))
        flag_money = False
        for sm in tsdb.get_info_sms(trip_date, False):
            percent_complite = percent_complite+int(100/len_complite)
            progress_send.progress(percent_complite)
            flag50 = False
            for i in sm[2].split(' '):
                if i in TOWN50:
                    flag50 = True
                    break    
                 
            if sm[5]:
                sms_driver = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_FIO(sm[5])}'
                phone_driver = tsdb.get_phone(sm[0])
                utils.sms_send(sms_driver, phone_driver)
                sms_forwarder = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_FIO(sm[0])}'
                phone_forwarder = tsdb.get_phone(sm[5])
                utils.sms_send(sms_forwarder, phone_forwarder)
                if sm[3] > 1:
                    flag_money = True
                    html_money = html_money + f"Командировка на {sm[3]} дня: <B>{sm[2]}</B><BR>Водитель : <B>{tsdb.get_name_by_id(sm[0])}</B><BR>Экспедитор : <B>{tsdb.get_name_by_id(sm[5])}</B><BR>Сумма по: <B>{'50' if flag50 else '25'} BYN</B> {'(есть областной город)' if flag50 else '(нет областных городов)'} <BR><BR>"
            else:
                sms_driver = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} без экспедитора'
                phone_driver = tsdb.get_phone(sm[0])
                if sm[3] > 1:
                    flag_money = True
                    html_money = html_money + f"Командировка на {sm[3]} дня: <B>{sm[2]}</B><BR>Водитель : <B>{tsdb.get_name_by_id(sm[0])}</B><BR>Сумма : <B>{'50' if flag50 else '25'} BYN</B><BR><BR>"
                utils.sms_send(sms_driver, phone_driver)
                
            html_letter = html_letter + '<LI>' + f"Путевой: <B>{sm[7]}</B> водитель <B>{tsdb.get_FIO(sm[0])}</B> {sm[2]} машина <B>{tsdb.get_number_car_clear(sm[4])}</B> дней: <B>{sm[3]}</B> экспедитор: <B>{tsdb.get_FIO(sm[5]) if sm[5] else ''}</B></LI>"
            tsdb.update_status_ready(sm[6])
        html_letter = html_letter + '</OL>' + '</font>'
        html_money = html_money + '<BR> Спасибо!</font>'
        if flag_money:
            utils.send_letter(f"Командировочные на {trip_date}", html_money, ['e.korneychik@belbohemia.by', 'n.kostkova@belbohemia.by', 'd.pyzh@belbohemia.by'])
        utils.send_letter(f'Командировки на {trip_date}', html_letter, ['e.korneychik@belbohemia.by', 't.firago@belbohemia.by', 't.drozd@belbohemia.by', 'guards@belbohemia.by', 'rampa@belbohemia.by'])
        table_trips.table(tsdb.get_trips_of_date(trip_date, False))
        utils.sms_send('Командировки готовы')
        
    st.text(f'Минск на : {trip_date}')
    table_trips = st.empty()
    table_trips.table(tsdb.get_trips_of_date(trip_date, True))
    html_letter = '<font size="3" face="Tahoma">'
    html_letter = html_letter + 'Добрый день<BR>' + '<OL>'
    if st.button('Уведомение по Минску', disabled=tsdb.get_status_message(trip_date, True)):
        progress_send = table_trips.progress(0)
        percent_complite = 0
        len_complite = len(tsdb.get_info_sms(trip_date, True))
        for sm in tsdb.get_info_sms(trip_date, True):
            percent_complite = percent_complite+int(100/len_complite)
            progress_send.progress(percent_complite)
            
            if sm[5]:
                sms_driver = f'{sm[1]} {sm[2]} Минск {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_FIO(sm[5])}'
                phone_driver = tsdb.get_phone(sm[0])
                utils.sms_send(sms_driver, phone_driver)
                sms_forwarder = f'{sm[1]} {sm[2]} Минск {tsdb.get_number_car_clear(sm[4])} c {tsdb.get_FIO(sm[0])}'
                phone_forwarder = tsdb.get_phone(sm[5])
                utils.sms_send(sms_forwarder, phone_forwarder)
            else:
                sms_driver = f'{sm[1]} {sm[2]} дни:{sm[3]} {tsdb.get_number_car_clear(sm[4])} без экспедитора'
                phone_driver = tsdb.get_phone(sm[0])
                utils.sms_send(sms_driver, phone_driver)
            html_letter = html_letter + '<LI>' + f"Путевой: <B>{sm[7]}</B> водитель <B>{tsdb.get_FIO(sm[0])}</B> Минск машина <B>{tsdb.get_number_car_clear(sm[4])}</B> экспедитор: <B>{tsdb.get_FIO(sm[5]) if sm[5] else ''}</B></LI>"
            tsdb.update_status_ready(sm[6])
            tsdb.update_status_ready(sm[6])
        html_letter = html_letter + '</OL>' + '</font>'
        utils.send_letter(f'Минск на {trip_date}', html_letter, ['e.korneychik@belbohemia.by', 't.firago@belbohemia.by', 't.drozd@belbohemia.by', 'guards@belbohemia.by', 'rampa@belbohemia.by'])
        table_trips.table(tsdb.get_trips_of_date(trip_date, True))
        utils.sms_send('Город готов')

############# Settings #############
def settings_create():
    #col1, col2 = st.columns(2)
    
    email = st.selectbox('Выберите адрес электронной почты',('a.petrovyh@belbohemia.by', 'e.korneychik@belbohemia.by'), index=0)
    email_password = st.text_input('Введите пароль', value=utils.MAIL_PASSWORD, type='password')
    list_money = st.multiselect('Письмо о командирвоочных', ['e.korneychik@belbohemia.by', 'n.kostkova@belbohemia.by', 'd.pyzh@belbohemia.by'])
    
    list_money = " ".join(list_money)
    if st.button('Сохранить'):
        config_ini.update_setting(path, 'mailserver', 'MAIL_USERNAME', email)
        config_ini.update_setting(path, 'mailserver', 'MAIL_PASSWORD', email_password)
        config_ini.update_setting(path, 'email', 'EMAIL_MONEY', list_money)


############## Data ###############

def data_create():
    pass

st.set_page_config(
    page_title='Информационная система',
    page_icon="🧊",
    layout="wide")
     
st.title('Информационная система')
st.text(f'Сегодня {str(datetime.now())}')

selected = option_menu(
    menu_title='Главное меню',
    options=['Табель', 'Командировки', 'Акты', 'Настройки', 'Данные'],
    icons=['calendar-range', 'alarm', 'card-checklist', 'tools'],
    orientation='horizontal',
    default_index=0,
    )

if selected == 'Табель':
    timesheets_create()
elif selected == 'Командировки':
    trips_create()
elif selected == 'Акты':
    acts_create()
elif selected == 'Настройки':
    settings_create()
elif selected == 'Данные':
    data_create()




