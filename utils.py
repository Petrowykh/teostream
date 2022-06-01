import pandas as pd
import requests,smtplib
import config_ini
from email.mime.text import MIMEText
from email.header import Header


path = "config.ini"
    # font = get_setting(path, 'Settings', 'font')
    # font_size = get_setting(path, 'Settings', 'font_size')
    
    # update_setting(path, "Settings", "font_size", "12")
    # delete_setting(path, "Settings", "font_style")

SMS_USER = config_ini.get_setting(path, 'sms', 'sms_user')
SMS_PASSWORD = config_ini.get_setting(path, 'sms', 'sms_password')
SMS_URL = config_ini.get_setting(path, 'sms', 'sms_url')

MAIL_SERVER = config_ini.get_setting(path, 'mailserver', 'mail_server')
MAIL_PORT = config_ini.get_setting(path, 'mailserver', 'mail_port')
MAIL_USERNAME = config_ini.get_setting(path, 'mailserver', 'mail_username')
MAIL_PASSWORD = config_ini.get_setting(path, 'mailserver', 'mail_password')


def sms_send(text, phone='+375(29)6908632'):
    param = {'user': SMS_USER, 'password': SMS_PASSWORD, 'recipient': phone, 'message': text, 'sender': 'belbohemia'}
    try:
        answer = requests.get(SMS_URL, params=param)
    except Exception as e:
        return e
    return answer

def send_letter(subject, htmlBody, recipient='a.petrovyh@belbohemia.by'):
    sender = MAIL_USERNAME
    receivers = recipient  
    mail_msg = htmlBody
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = Header("\u2139 Информационная рассылка", 'utf-8')
        
    message['Subject'] = Header(subject, 'utf-8')
    
    try:
        smtpObj = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    except Exception as e:
        smtpObj = smtplib.SMTP_SSL('smtp.belbohemia.by', 465)

    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
    
    try:
        smtpObj.sendmail(sender, receivers, message.as_string())
        
    except smtplib.SMTPException as e:
        return e
    smtpObj.quit()
    
def draw_table(table):
    def define_color(num):
        if not str(num).isdigit():
            return f">{num}"
        elif num == 1:
            return "bgcolor='#8B008B'>"
        elif num == 8 or num == 7 or num == 6:
            return f"bgcolor='#000'>{num}"
        elif num == 4: # trips
            return "bgcolor='#87CEFA'>"
        elif num == 2: # за с/с
            return "bgcolor='#32CD32'>"
        elif num == 3: # болен
            return "bgcolor='#FF1493'>"
        elif num == 5: # отпуск
            return "bgcolor='#D4DE10'>"
        else:
            return "bgcolor='#000'>"




    df_list = table
    len_date = len(table[0])-2
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
            color: #fff;
        }
        
        th, td {
            border-style: solid;
            border-width: 0 1px 1px 0;
            border-color: #61bd5b;
            padding:5px;
            
        }

        tr {
            color: #fff
        }

        th:first-child, td:first-child {
            text-align: left;
            padding-right: 30px;
        }
    </style>
    """
    header = style_table + '<table><tr><th>Фамилия</th>'
    header = header + '<th>Время</th><th>Переработка</th>'
    plus_ = lambda x: str(x) if len(str(x)) > 1 else str(x) + '_'
    for i in range(1,len_date):
        header = header + f'<th>{plus_(i)}</th>'
    header = header + '</tr>'
    for i in range(0, 2):
        header = header + '<tr>'
        for j in range(0, len_date+2):
            header = header + f'<td {define_color(df_list[i][j])}</td>'
            
        header = header + '</tr>'
    header = header + '</table>'
    
    return header
