from datetime import datetime, timedelta
import streamlit as st

def app():
    st.subheader('Командировки')
    trip_data = st.sidebar.date_input('Дата командирвоки', datetime.now()+timedelta(days=1))
    trip_number = st.sidebar.number_input('Insert a number', format="%d", value=27999)
    trip_check_town = st.sidebar.checkbox('Командировка')
    if trip_check_town:
        trip_town = st.sidebar.text_input('Маршрут', placeholder='Введите города через пробел')
        trip_days = st.sidebar.slider(
            'Количество дней командировки',
            1, 3, (1))
    trip_driver = st.sidebar.selectbox('Выберите водителя',
     ('Колесень Александр', 'Дудорга Роостислав', 'Костицкий Денис'))
    trip_car = st.sidebar.selectbox('Выберите машину',
    ('ГАЗ', 'Атега', 'Рено'))
    trip_check_boy = st.sidebar.checkbox('Экспедитор')
    if trip_check_boy:
        trip_boy = st.sidebar.selectbox('Выберите экспедитора',
        ('Можейко Андрей', 'Ивановский Александр', 'Клюев Сергей'))