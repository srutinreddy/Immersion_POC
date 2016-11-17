#!c:/python27/python.exe -u
# -*- coding: utf-8 -*-

import psycopg2
import cgi
import sys
import json

print "Content-type: text/html\n\n"
con = None
dyna_array=[]

form = cgi.FieldStorage()
api_mode=form.getvalue('mode')
useremail=form.getvalue('useremail')
category=form.getvalue('category')
json_final=""
try:
    con = psycopg2.connect(database='postgres', user='postgres')
    cur = con.cursor()

except psycopg2.DatabaseError, e:
    data=[{'Error':'%s' %(e)}]
    print json.dumps(data)
    sys.exit(1)

if api_mode == 'add':
   for x in range(1,12,1):
     fetchkey='q%s' %(x)
     try:
       fetchval = form.getvalue(fetchkey)
       dyna_array.append(fetchval)
     except:
       pass

   json_array=[]
   scoreval=0.0
   counts=0.0
   rawscore=0.0

   for x in range(len(dyna_array)):
      if dyna_array[x] not in (None,):
         fetchkey='q%s' %(x+1)
         if dyna_array[x] in ('yes','y'):
            rawscore+=1
         elif dyna_array[x] in ('no','n'):
            rawscore+=0
         json_array.append("%s:'%s'" %(fetchkey,dyna_array[x]))
         counts+= 1
   # end loop
   scoreval = (rawscore / counts) * 100

   json_str=','.join(json_array)
   json_final='{%s}' %(json_str)

   # write row to the table
   try:
      cur.execute("insert into questionaire(user_name,category,response,score) values(%s,%s,%s,%s);",
          (useremail, category, json_final, scoreval))
   except psycopg2.DatabaseError, e:
      data=[{'Error':'%s' %(e)}]
      print json.dumps(data)
      sys.exit(1)

   con.commit()
   data=[{'score':'%.2f' %(scoreval)}]
   fin_data=json.dumps(data)

   print fin_data
   if con:
       con.close()
   sys.exit(0)
# mode = 'add'

elif api_mode == 'summary':
   select_query='''
          select user_name, category, count(2), sum(score)/count(2) from questionaire
           where user_name='%s'
           group by user_name, category;
        ''' %(useremail)
   try:
       cur.execute(select_query)
       res_set=cur.fetchall()
   except psycopg2.DatabaseError, e:
       data=[{'Error':'%s' %(e)}]
       print json.dumps(data)
       sys.exit(1)

   if len(res_set) == 0:
      data=[{'Error':'No stats available'}]
      print json.dumps(data)
      con.close()
      sys.exit(0)
   else:
      data=[]
      sub_lines=[]
      lev1={}
      for lines in res_set:
           (user_name,cat,num_submitted,avg)=lines
           lev2={'cat':cat, 'num_submitted':'%d'%(num_submitted), 'stat_avg':'%.3f'%(avg)}
           try:
              lev1['sub_data'].append(lev2)
           except:
              sub_lines.append(lev2)
              lev1={'user_name': user_name, 'sub_data': sub_lines}
      #end loop
      data.append(lev1)
      print json.dumps(data)
      if con:
         con.close()
      sys.exit(0)
# end else case
