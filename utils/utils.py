import pandas as pd
import requests


#SELECT * from trips where data_route=(select max(data_route) from trips WHERE direction<>'Минск') and direction<>'Минск'

data = {
    'name': ['Петровых', 'Корнейчик', 'Лепехо', 'Талах'],
    ' 1' : [1,1,1,8],
    ' 2' : [1,4,1,1],
    ' 3' : [1,1,1,1],
    ' 4' : [2,2,2,2],
    ' 5' : [2,2,2,2],
    ' 6' : [1,1,1,1],
    ' 7' : [1,1,3,1],
    ' 8' : [1,1,1,1],
    ' 9' : [1,5,1,1],
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


SMS_USER = 'Belbogemia'
SMS_PASSWORD = '98k47478'
SMS_URL = 'https://userarea.sms-assistent.by/api/v1/send_sms/plain'


def sms_send(text, phone='+375(29)6908632'):
    param = {'user': SMS_USER, 'password': SMS_PASSWORD, 'recipient': phone, 'message': text, 'sender': 'belbohemia'}
    try:
        answer = requests.get(SMS_URL, params=param)
    except Exception as e:
        return e
    return answer

def draw_table():
    def define_color(num):
        if not str(num).isdigit():
            return f">{num}"
        elif num == 1:
            return "bgcolor='yellow'>"
        elif num == 2:
            return "bgcolor='red'>"
        elif num == 4:
            return "bgcolor='blue'>"
        else:
            return "bgcolor='#000'>"




    df = pd.DataFrame(data)
    df_list = df.values.tolist()
    #st.table(df)
    style_table = """
    <style>
        table {
            font-family: "Source Sans Pro", sans-serif;
            font-size: 12px;
            border-collapse: collapse;
            text-align: center;
            
        }

        th, td:first-child {
            background: #000;
            color: #61bd5b;
        }
        
        th, td {
            border-style: solid;
            border-width: 0 1px 1px 0;
            border-color: #61bd5b;
            padding:5px;
            
        }

        th:first-child, td:first-child {
            text-align: left;
            padding-right: 30px;
        }
    </style>
    """
    header = style_table + '<table><tr><th>Фамилия</th>'
    plus_ = lambda x: str(x) if len(str(x)) > 1 else '_' + str(x)
    for i in range(1,30):
        header = header + f'<th>{plus_(i)}</th>'
    header = header + '</tr>'
    for i in range(0, 4):
        header = header + '<tr>'
        for j in range(0, 30):
            header = header + f'<td {define_color(df_list[i][j])}</td>'
            
        header = header + '</tr>'
    header = header + '</table>'
    
    return header
