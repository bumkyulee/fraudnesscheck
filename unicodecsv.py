#-*- coding: utf-8 -*-
import csv
f = open('data1.csv', 'w')
cw = csv.writer(f)
for row in [1,20]:
    s = ['한글','something english']
    cw.writerow(s)
f.close()
