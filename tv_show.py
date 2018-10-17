import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request, urllib.parse, urllib.error, datetime
from bs4 import BeautifulSoup
import ssl
import time
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


def db():   
    c.execute("Create database if not exists new_db")
    c.execute("Use new_db")

    
def set_dtetme(date1):   
    arr=['Jan','Feb','Mar','May','Apr','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    a=date1
    dte1=int(a[0:2])
    mon1=a[3:6]
    mont1=0
    for i in range(len(arr)):
        if mon1==arr[i]:
            mont1=i+1
    year1=int(a[-4:])
    dat="%i-%i-%i"%(year1,mont1,dte1)
    return dat


def comp_dtetme(d1,d2):
    dte1=d1.split("-")
    dte2=d2.split("-")
    for i in range(3):
        if int(dte1[i])>int(dte2[i]):
            return d1
        elif int(dte1[i])==int(dte2[i]):
            continue
        elif int(dte1[i])<int(dte2[i]):
            return d2
    
    

conn = MySQLdb.connect("localhost","root","root")
c = conn.cursor()    
    
db()                #Calling the database function to create one
email = input('Enter your Email-Id- ')            #Taking input of email to which results need to be sent
tvsrs=input('Enter the tv-shows- ')               #Taking input details of the series
tvseries=[x for x in tvsrs.split(',')]
air_list = []

sql_create_table = """ CREATE TABLE if not exists pythn_usr (email_id varchar(100),tv_shows varchar(550))  """
sql_insert_query = """ INSERT INTO pythn_usr(email_id,tv_shows) values (%s,%s)  """

c.execute(sql_create_table)
c.execute(sql_insert_query, (email,tvsrs))
conn.commit()
conn.close()


for series in tvseries:
    sr=series.strip()
    srsr=sr.split(" ")
    srs="+".join(str(i) for i in srsr)

    url = "https://www.imdb.com/find?ref_=nv_sr_fn&q="+srs+"&s=all"
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    name = soup.find_all(class_ = "result_text")[0].a.get('href')

    sr='https://www.imdb.com'
    url_nm=sr+name
    
    html1 = urllib.request.urlopen(url_nm).read()
    soup1 = BeautifulSoup(html1, 'html.parser')
    nme1=soup1.find_all(class_ = "seasons-and-year-nav")[0].a.get('href')
    url_nm1=sr+nme1

    
    html2 = urllib.request.urlopen(url_nm1).read()
    soup2 = BeautifulSoup(html2, 'html.parser')
    nme2 = soup2.find_all(class_ = "airdate")
     
    li=[]
    r_li=[]
    for r in nme2:
        r_li.append(r.get_text().strip())
   
    for i in range(len(r_li)):
        if r_li[i]:
            li.append(r_li[i])

    xz = li[0][-4:]
    count=0
    
    air_2 = ""
    for r in range(len(li)):
        z= li[r][-4:]
        
        if len(li[r])>4:
            tht_date=set_dtetme(li[r])
            today=datetime.date.today().strftime('%Y-%m-%d')
            rslt=comp_dtetme(tht_date,today)
            if rslt==tht_date:
                air_2 = "The next episode airs on "+(tht_date)+"."
                break
            elif rslt==today:
                count=count+1
        
            if count==len(li):
                air_2 = "The show has finished streaming all its episodes."
                break

        elif len(li[r])==4:
            if int(xz)>datetime.datetime.today().year:
                air_2="The next season begins in "+xz+"."
                break
            elif int(z)<datetime.datetime.today().year:
                count=count+1
            elif int(z)>datetime.datetime.today().year:
                air_2 = "The next episode airs on "+z+"...."
                break
            
            if count==len(li):
                air_2 = "The show has finished streaming all its episodes...."
                
    air_list.append(air_2)

    
    
result =""
    
for i, j in zip(tvseries, air_list):
    result = result + "<p>Tv series name: " + i + "</p><p> Status: " + j + "</p> <br />"
    

user_email="example@gmail.com"
user_pass="password"
msg = MIMEMultipart()
msg['From'] = user_email
msg['To'] = email
msg['Subject'] = "Episode"
SUBJECT = "Episode"
TO = email
FROM = user_email
msg.attach(MIMEText(result,'html'))

server = smtplib.SMTP('smtp.gmail.com')

server.starttls()

server.login(user_email, user_pass)
server.sendmail(FROM, [TO], msg.as_string())
server.quit()