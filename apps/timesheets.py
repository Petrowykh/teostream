from numpy import choose
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

data = {
    'name': ['Петровых', 'Корнейчик', 'Лепехо', 'Талах'],
    '1' : [1,1,1,8],
    '2' : [1,4,1,1],
    '3' : [1,1,1,1],
    '4' : [2,2,2,2],
    '5' : [2,2,2,2],
    '6' : [1,1,1,1],
    '7' : [1,1,3,1],
    '8' : [1,1,1,1],
    '9' : [1,5,1,1],
    '11' : [0,0,0,0],
    '12' : [0,0,0,0],
    '13' : [0,0,0,0],
    '14' : [0,0,0,0],
    '15' : [0,0,0,0],
    '16' : [0,0,0,0],
    '17' : [0,0,0,0],
    '18' : [0,0,0,0],
    '19' : [0,0,0,0],
    '20' : [0,0,0,0],
    '21' : [0,0,0,0],
    '22' : [0,0,0,0],
    '23' : [0,0,0,0],
    '24' : [0,0,0,0],
    '25' : [0,0,0,0],
    '26' : [0,0,0,0],
    '27' : [0,0,0,0],
    '28' : [0,0,0,0],
    '29' : [0,0,0,0],
    '30' : [0,0,0,0],
    
    

}

def draw_table():
    
    df = pd.DataFrame(data)
    df_list = df.values.tolist()
    #st.table(df)
    header = '<table><tr><th>Фамилия</th>'
    for i in range(1,30):
        header = header + f'<th width="3%">{str(i)}</th>'
    header = header + '</tr>'
    for i in range(0, 4):
        header = header + '<tr>'
        for j in range(0, 30):
            header = header + f'<td width="3%">{str(df_list[i][j])}</td>'
        header = header + '</tr>'
    header = header + '</table>'
    
    return header


def app():
    st.subheader('Табель')
    choose = st.sidebar.selectbox('Выберите отдел ЛУ',
                        ('Логистика', 'Мезонин', 'Транспортный'))
    if st.sidebar.button('Показать') == True:
        components.html(draw_table(), height=300, width=600, scrolling=True)