from datetime import timedelta, datetime
import xlwings as xw
from pathlib import Path

def create_report(list_trips):
    wb = xw.Book(Path('excel/ts_temp.xlsx'))
    sheet = wb.sheets[0]
    sh_ready = sheet.copy()
    
    sh_ready.name = list_trips[0]
    sh_ready['C11'].value = list_trips[0]
    sh_ready['C12'].value = 'водитель'
    sh_ready['C2'].value = "9/05"
    sh_ready['D19'].value = list_trips[2][0]
    sh_ready['D20'].value = list_trips[2][1]
    sh_ready['G22'].value = list_trips[0]
    for num, d_trips in enumerate(list_trips[1]):
        row_ins = 17+num
        sh_ready[f"A{row_ins}:G{row_ins}"].insert(shift='down')
        sh_ready[f"A{row_ins}"].value = num + 1
        if d_trips[1] == 1:
            sh_ready[f"B{row_ins}"].value = d_trips[0]
        else:
            end_d=(datetime.strptime(d_trips[0], '%Y-%m-%d')+timedelta(days=int(d_trips[1])-1)).strftime('%d.%m.%Y')
            sh_ready[f"B{row_ins}"].value = d_trips[0].split('-')[2] + '-' + end_d
        sh_ready[f"C{row_ins}"].value = 'Доставка ТМЦ'
        sh_ready[f"D{row_ins}"].value = d_trips[1]
    sheet.delete()
    wb.save(Path('excel/new.xlsx'))
    wb.close()

    