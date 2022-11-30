import time

from openpyxl import load_workbook
wb = load_workbook(filename='result.xlsx')
sheet = wb.active

snipping_double = set()
for row in sheet.rows:
    val = row[1].value
    if val in snipping_double:
        print(f'exist -> {val}')
        time.sleep(60)
    else:
        print('ok')
        snipping_double.add(val)
print(len(snipping_double))

