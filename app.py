import logging
from time import sleep
import streamlit as st
import pandas as pd

from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from datetime import datetime, timedelta, date
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import config_ini, utils
from ts_db import Teo_DB
import ts_excel

from io import BytesIO



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
        
        table_html = tsdb.get_dd(6, 'транспортный')
        components.html(utils.draw_table(table_html), height=400, scrolling=True)

        
        


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
            if trip_check_forwarder:
                tsdb.update_timesheets_df(tsdb.get_id_employee(trip_driver), trip_date.strftime('%Y-%m-%d'), True)
                tsdb.update_timesheets_df(trip_forwarder, trip_date.strftime('%Y-%m-%d'), False)
            else:
                tsdb.update_timesheets_df(tsdb.get_id_employee(trip_driver), trip_date.strftime('%Y-%m-%d'), True)
            st.info('Рейс добавлен')
            st.experimental_rerun()
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
    """
    Global options
    """
    
    email = st.selectbox('Выберите адрес электронной почты',('a.petrovyh@belbohemia.by', 'e.korneychik@belbohemia.by'), index=0)
    email_password = st.text_input('Введите пароль', value=utils.MAIL_PASSWORD, type='password')
    list_money = st.multiselect('Письмо о командирвоочных', ['e.korneychik@belbohemia.by', 'n.kostkova@belbohemia.by', 'd.pyzh@belbohemia.by'])
    
    list_money = " ".join(list_money)
    if st.button('Сохранить'):
        config_ini.update_setting(path, 'mailserver', 'MAIL_USERNAME', email)
        config_ini.update_setting(path, 'mailserver', 'MAIL_PASSWORD', email_password)
        config_ini.update_setting(path, 'email', 'EMAIL_MONEY', list_money)


############## Data ###############

def cars_edit():
    """
    Edit cars table
    """
    gd = GridOptionsBuilder.from_dataframe(tsdb.get_data_cars())
    gd.configure_selection(selection_mode='single', use_checkbox=True)
    gridoption = gd.build()
    cars_table = AgGrid(tsdb.get_data_cars(), gridOptions=gridoption, update_mode=GridUpdateMode.SELECTION_CHANGED, theme='streamlit', reload_data=True, enable_enterprise_modules=True, key=1)
    select_row = cars_table['selected_rows'] 
    edit_flag = False
    #TODO correct check edit_flag
    try:
        edit_flag = True if select_row[0] else False
    except Exception as e:
        print (e)
    if edit_flag:
        form = st.sidebar.form('Edit')
        form.text(f"ID: {select_row[0]['id']}")
        form.text(f"Собственность: {select_row[0]['Собственность']}")
        our_car = True if select_row[0]['Собственность'] == '\u2714' else False
        in_work = True if select_row[0]['В работе'] == '\u2714' else False 
        if not our_car:
            km = form.slider('Цена за километр', 0.4, 1.5, float(select_row[0]['Цена за км']), 0.1)
            hour = form.slider('Цена за час', 15, 100, int(select_row[0]['Цена за час']), 1)
        else:
            km = 0
            hour = 0
        check_work = form.checkbox('В работе', value=in_work)
        
        if form.form_submit_button('Save'):
            tsdb.update_cars(int(select_row[0]['id']), float(km), int(hour), check_work)
            st.experimental_rerun()
    
def report_create():
    list_id = []
    
    #st.table(tsdb.get_trips_of_month('05'))
    st.info('Create xlsx-file')
       
    #print(tsdb.get_list_id_our(d_or_f=False))
    for id in tsdb.get_list_id_our():
        list_trip = []
        list = []
        one1 = 0
        many = 0
        list.append(tsdb.get_FIO(id))
        
        for i in tsdb.get_trips_of_month(id_employees=id):
            print (i)
            list_trip.append([i[0], i[1]])
            if i[1] == 1:
                one1 = one1 + 1
            else:
                many = many + i[1]
        list.append(list_trip)
        list.append([one1, many])
        list.append(id)
        list.append(True)
        list_id.append(list)
        print(list)

    for id in tsdb.get_list_id_our(d_or_f=False):
        list_trip = []
        list = []
        one1 = 0
        many = 0
        list.append(tsdb.get_FIO(id))
        
        for i in tsdb.get_trips_of_month(id_employees=id, d_or_f=False):
            print (i)
            list_trip.append([i[0], i[1]])
            if i[1] == 1:
                one1 = one1 + 1
            else:
                many = many + i[1]
        list.append(list_trip)
        list.append([one1, many])
        list.append(id)
        list.append(False)
        list_id.append(list)
        print(list)
    ts_excel.create_report(list_id)
    st.markdown(f'<a href="excel/new.xlsx" download>Ссылка на локальный файл</a>', unsafe_allow_html=True)
    # output = BytesIO()
    # with open('excel/new.xlsx', 'r') as file:
    #     st.download_button(label='Заггрузить', 
    #                     data=output.getvalue(),
    #                     file_name=file,
    #                     mime="application/vnd.ms-excel")
    
    

def employees_edit():
    pass

def trips_delete():
    """
    Delete trips in Data
    """
    trip_data = st.sidebar.date_input('Выберите дату', datetime.now())
    gd_trips = GridOptionsBuilder.from_dataframe(tsdb.get_trips_of_date_for_delete(trip_data))
    gd_trips.configure_selection(selection_mode='single', use_checkbox=True)
    gridoption = gd_trips.build()
    trip_table = AgGrid(tsdb.get_trips_of_date_for_delete(trip_data), gridOptions=gridoption, update_mode=GridUpdateMode.SELECTION_CHANGED, theme='streamlit', height=300)
    select_row = trip_table['selected_rows'] 
    edit_flag = False
    try:
        edit_flag = True if select_row[0] else False
    except Exception as e:
        print (e)
    if edit_flag:
        if st.button('Удалить'):
            info_ts = tsdb.get_info_trip_ts(select_row[0]['id'])
            tsdb.update_timesheets_df(info_ts[1], info_ts[0], True, False)
            tsdb.delete_trip(select_row[0]['id'])
            
            
            
            if info_ts[2]:
                tsdb.update_timesheets_df(info_ts[2], info_ts[0], True, False)
            

            st.experimental_rerun()


def data_create():
    """
    Data option
    """
    choose_data = st.sidebar.selectbox('Выберите данные',['Машины', 'Сотрудники', 'Командировки'])
    if choose_data == 'Машины':
        cars_edit()
    elif choose_data == 'Сотрудники':
        employees_edit()
    elif choose_data == 'Командировки':
        trips_delete()
        
                
def main():
    st.set_page_config(
        page_title='Информационная система',
        page_icon="🧊",
        layout="wide")
        
    st.title('Информационная система')
    st.text(f'Сегодня {str(date.today())}')

    selected = option_menu(
        menu_title='Главное меню',
        options=['Табель', 'Командировки', 'Акты', 'Настройки', 'Данные', 'Отчеты'],
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
    elif selected == 'Отчеты':
        report_create()


if __name__ == '__main__':
    main()




