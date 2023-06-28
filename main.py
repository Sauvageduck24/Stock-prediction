import streamlit as st
import streamlit_authenticator as stauth
from datetime import date,datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
from PIL import Image

image = Image.open('market-master-logo.png')

st.set_page_config(page_title="Market Master",page_icon="market-master-web-logo.ico",initial_sidebar_state="auto")#,layout='wide')

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
	    
st.markdown(hide_streamlit_style, unsafe_allow_html=True)     # para quitar marca de agua

try:
    warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 
except:
    print('Error')

scopes= [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

drive_credentials= {
    "type":st.secrets['type'],
	"project_id":st.secrets['project_id'],
	"private_key_id":st.secrets['private_key_id'],
	"private_key":st.secrets['private_key'],
	"client_email":st.secrets['client_email'],
	"client_id":st.secrets['client_id'],
	"auth_uri":st.secrets['auth_uri'],
	"token_uri":st.secrets['token_uri'],
	"auth_provider_x509_cert_url":st.secrets['auth_provider_x509_cert_url'],
	"client_x509_cert_url":st.secrets['client_x509_cert_url'],
}

creds=ServiceAccountCredentials.from_json_keyfile_dict(drive_credentials,scopes=scopes)
file = gspread.authorize(creds)

search_db="1VDwSucmsEn0hiTgvGYQGTr9ZBWLpQ0yyXG7sYn0Srw8"
workbook_db=file.open_by_key(search_db)
sheet_db = workbook_db.worksheet('DB')

db_data=sheet_db.get_all_values()

#st.write(db_data)
#st.write(len(db_data))
#st.write(db_data[0])

usernames_f=[];passwords_f=[];end_times_f=[];emails_f=[];roles_f=[];stock_f=[]

for i in range(len(db_data)):
    if i==0:
        continue

    if db_data[i][3]!='':
        usernames_f.append(db_data[i][1])
        passwords_f.append(db_data[i][2])
        emails_f.append(db_data[i][3])
        end_times_f.append(db_data[i][4])
        roles_f.append(db_data[i][5])
        stock_f.append(db_data[i][6])


usernames={}

for i in range(len(usernames_f)):
    usernames[usernames_f[i]]={"email":emails_f[i],"name":usernames_f[i],"password":passwords_f[i]}

credentials={"usernames":usernames}

authenticator = stauth.Authenticate(
    credentials, 
    st.secrets['name_cookies'],
    st.secrets['key'],
    st.secrets['expiry_days'],
)

name, authentication_status, username = authenticator.login('Login', 'main')

today = date.today()
dia=today.strftime("%d-%m-%Y")

if authentication_status:
    pos_username=usernames_f.index(name)

    if end_times_f[pos_username]!="NEVER":
        expire_date=datetime.strptime(end_times_f[pos_username], "%d/%m/%Y").date()    
        dia_actual=datetime.strptime(today.strftime("%d/%m/%Y"),"%d/%m/%Y").date()
        if dia_actual>=expire_date:
            authenticator.cookie_manager.delete(authenticator.cookie_name)
            st.session_state['logout'] = True
            st.session_state['name'] = None
            st.session_state['username'] = None
            st.session_state['authentication_status'] = None
            st.experimental_rerun()
	
    col1,col2=st.columns([1,1])

    with col1:
        st.write(f"Has iniciado sesión como: {name.upper()}")

    with col2:
        authenticator.logout('Logout', 'main', key='unique_key')
	    
    #st.title('Market Master')
    st.image(image)

    stocks = ['BBVA','IAG']

    st.write(stocks_f)
	
    if stocks_f[pos_username] in stocks:
        del stocks[stocks.index(stocks_f[pos_username])]
        stocks.insert(0,stocks_f[pos_username])
	
    selected_stock = st.selectbox('Seleccione la compañía para hacer la predicción', stocks)

    if selected_stock=='BBVA':
        search='1COITRN8LVx3Sa2zDQRYn-Igt91bg_mZlYqdeGE5KpAQ'
	
    workbook=file.open_by_key(search)

    sheet = workbook.worksheet('ONE DAY DATA')
    sheet2= workbook.worksheet('CALC')
    sheet3 = workbook.worksheet('HOUR DATA')
    sheet4 = workbook.worksheet('DAY DATA')

    st.subheader('Predicción para el día siguiente')

    cell=sheet.find(f"{dia}")
    cell2=sheet2.find(f"{dia}")
	
    if cell is None:
    	st.warning('Hoy no hay bolsa 😥', icon="⚠️")
    	raise Exception('Hoy no hay bolsa 😥')

	
    if not sheet.cell(cell.row,3).value and roles_f[pos_username]=='ADMIN':
        p_open = st.text_input('Precio Open: ')
        try:
            p_open = p_open.replace('.',',')
        except:
            pass
    
    else:
        p_open=''

    prediction=st.button('Hacer predicción',key='4')

    if prediction:

        if p_open:
            sheet.update(f'C{cell.row}',p_open)
	
            if not sheet3.cell(3,3).value:
                sheet3.update('C3',p_open)	

            if not sheet4.cell(3,3).value:
                sheet4.update('C3',p_open)	
	    
        values=sheet.range(f'G{cell.row}:J{cell.row}')
        open=values[0].value
        high=values[1].value
        low=values[2].value
        close=values[3].value
	
        values2=sheet2.range(f'G{cell2.row}:K{cell2.row}')
        sub_dia=values2[0].value
        sub_entre_dias=values2[2].value
        anotaciones=values2[4].value
        accuracy=sheet2.range(f"F3:F3")
        accuracy=accuracy[0].value
	    
        open=float(open.replace(',','.'))
        high=float(high.replace(',','.'))
        low=float(low.replace(',','.'))
        close=float(close.replace(',','.'))

        st.write(" ")	    
        st.write(f"Precisión media del código en acciones de {selected_stock}:  {accuracy}")
        st.write(" ")    
        st.write('Predicciones para el día')
        
        new_real=[high,low,close]
	
        df=pd.DataFrame([[open,high,low,close]],columns=['Apertura','Máximo','Mínimo','Cierre'])
	    
        st.dataframe(df)
	
        st.write('Estadísticas día')	
	
        df=pd.DataFrame([[sub_dia,sub_entre_dias]],columns=['Subida mismo dia (Open-High)','Subida entre dias'])
        st.dataframe(df)
	
        high=sheet3.range('H3:H10')
        low=sheet3.range('I3:I10')
	    
        data = yf.download(f'{selected_stock}.MC', period=f'1d',interval=f'1m',progress=False)

        now = datetime.now()
	
        if now.hour+2>9:
            if now.minute>15:
                pass
        else:
            data=data[:-9*60]
	
        for _,i in enumerate(high):
            num=i.value
            high[_]=float(num.replace(',','.'))
	
        for _,i in enumerate(low):
            num=i.value
            low[_]=float(num.replace(',','.'))
	
        mean=[]
        time=[]

        for i,j in zip(high,low):
            mean.append((i+j)/2)
	    
        for i in range(len(high)):
            time.append(i)

        high=np.array(high)
        low=np.array(low)
        mean=np.array(mean)
	    
        time=np.array(time)

        real=[]
	    
        for index,row in data.iterrows():
            real.append(row['Close'])
	    
        #------------------------------------------------------------------------------------
	    
        low_=low.tolist()
        high_=high.tolist()
        mean_=mean.tolist()
	    
        new_low=[]
        new_high=[]
        new_mean=[]
	    
        last_low=0
        last_high=0
        last_mean=0
	
        for _,i in enumerate(low_):
            if _!=len(low_):
                rango=60
            else:
                rango=60
		
            for j in range(rango):
                if j==0:
                    new_low.append(i)
                    last_low=i
                else:			
                    new_low.append(np.nan)

        for _,i in enumerate(high_):
            if _!=len(low_):
                rango=60
            else:
                rango=60
		
            for j in range(rango):
                if j==0:
                    new_high.append(i)
                    last_high=i
                else:
                    new_high.append(np.nan)

        for _,i in enumerate(mean_):
            if _!=len(low_):
                rango=60
            else:
                rango=60
		
            for j in range(rango):
                if j==0:
                    new_mean.append(i)
                    last_mean=i
                else:
                    new_mean.append(np.nan)

        low=np.array(new_low)
        high=np.array(new_high)
        mean=np.array(new_mean)
	    
        time=[]

        for i in range(len(high)):
            time.append(i)

        time=np.array(time)

        mask=np.isfinite(low)
        mask2=np.isfinite(high)
        mask3=np.isfinite(mean)
	    
        xs=np.arange(len(low))
        xs2=np.arange(len(high))
        xs3=np.arange(len(mean))
	    
        fig,ax=plt.subplots() #ancho , alto

        ax.plot(xs[mask],low[mask],linestyle='-',color='r',label='Mínimo')
        ax.plot(xs[mask3],mean[mask3],linestyle='-',color='gray',alpha=0)
        ax.plot(xs[mask2],high[mask2],linestyle='-',color='g',label='Máximo')

        ax.scatter(xs[mask],low_,color='r')
        ax.scatter(xs[mask2],high_,color='g')
	    
        ax.plot(real,color='white',label='Real Data',alpha=0.85)

        pos_high,=np.where(high==max(high))
        pos_low,=np.where(low==min(low))
	    
        pos_high=pos_high.flat[0]
        pos_low=pos_low.flat[0]

        pos_high=pos_high.flat[0]
        pos_low=pos_low.flat[0]
        	
        ax.scatter([pos_high,pos_low,len(low)-60],new_real,color='gray',label='Valores predichos')

        ax.fill_between(xs[mask2],high[mask2],mean[mask3], color="green", alpha=0.1)
        ax.fill_between(xs[mask2],mean[mask3],low[mask], color="red", alpha=0.1)
	    
        poss=['^','v']
	
        if pos_low<pos_high:
            ax.scatter(pos_high,max(high)+0.01,marker=poss[1],color='r')
            ax.scatter(pos_low,min(low)-0.01,marker=poss[0],color='g')
	
        dif=round((100-(min(low)*100)/max(high)),2)
	
        ax.axhline(y=max(high), color='g',linestyle='--')
        ax.axhline(y=min(low) , color='r',linestyle='--')
	
        ax.axhline(y=new_real[0], color='gray', linestyle='--',alpha=0.3)
        ax.axhline(y=new_real[1], color='gray', linestyle='--',alpha=0.3)
	
        #if dif>=0:
            #ax.text(20,max(high), f'{dif} %', va='center', ha='center', backgroundcolor='w',color='g')
        #else:
            #ax.text(400, min(low), f'{dif} %', va='center', ha='center', backgroundcolor='w',color='r')
	
        plt.xlabel("Tiempo (h)")
        plt.ylabel("Precio (€)")
	
        new_time=['9','10','11','12','13','14','15','16']
	
        plt.xticks(np.arange(0, len(low), 60),new_time)
	
        ax.legend(loc="best")

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        ax.tick_params(colors='white')
	    
        ax.set_facecolor((0, 0, 0))
        fig.patch.set_facecolor((0, 0, 0))

        ax.set_title('Gráfico aproximado del día (formato en 1 hora)',color='white')
	    
        plt.grid(axis="x",alpha=0.1)
        plt.grid(axis="y",alpha=0.1)
   
        st.pyplot(plt.gcf())

        #------------------------------------------------------------------------------------
	    
        high=sheet4.range('H3:H10')
        low=sheet4.range('I3:I10')
	
        for _,i in enumerate(high):
            num=i.value
            high[_]=float(num.replace(',','.'))
	
        for _,i in enumerate(low):
            num=i.value
            low[_]=float(num.replace(',','.'))
	
        mean=[]
        time=[]

        data = yf.download(f'{selected_stock}.MC', period=f'1d',interval=f'1d',progress=False)
	
        now = datetime.now()
        #now=now.replace(tzinfo=datetime.timezone.utc)
	
        if now.hour+2>9:
            if now.minute>15:
                pass
        else:
            data=data[:-1]
	
        for i,j in zip(high,low):
            mean.append((i+j)/2)

        for i in range(len(high)):
            time.append(i)

        high=np.array(high)
        low=np.array(low)
        mean=np.array(mean)
        time=np.array(time)	
	
        real=[]

        for index,row in data.iterrows():
            new_data=(row['High']+row['Low']+row['Close'])/3
            real.append(new_data)

        time=[]
        for i in range(len(high)):
            time.append(i)
	
        fig,ax=plt.subplots()
		
        ax.plot(high,'g',label='Máximo')
        ax.legend(loc="upper right")
        ax.plot(mean,'gray',alpha=0)
        ax.plot(low,'r',label='Mínimo')
        ax.legend(loc="upper right")

        ax.scatter(time,high,color="g")
        ax.scatter(time,low,color="r")
	    
        if real:	
            ax.scatter([0],real,color='white',label='Día actual')
            ax.legend(loc="best")
	
        ax.fill_between(time,high,mean, color="green", alpha=0.1)
        ax.fill_between(time,mean,low, color="red", alpha=0.1)
	
        dif=round((100-(min(low)*100)/max(high)),2)
	
        ax.axhline(y=max(high), color='g',linestyle='--')
        ax.axhline(y=min(low) , color='r',linestyle='--')
	
        #if dif>=0:
            #ax.text(1,max(high), f'{dif} %', va='center', ha='center', backgroundcolor='w',color='g')
        #else:
            #ax.text(7, min(low), f'{dif} %', va='center', ha='center', backgroundcolor='w',color='r')

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        ax.tick_params(colors='white')
	    
        ax.set_facecolor((0, 0, 0))
        fig.patch.set_facecolor((0, 0, 0))
	    
        plt.grid(axis="x",alpha=0.1)
        plt.grid(axis="y",alpha=0.1)
	    
        plt.xlabel("Tiempo (d)")
        plt.ylabel("Precio (€)")

        ax.set_title('Gráfico aproximado para 8 días (orgánicos)',color='white')
	    
        plt.grid(axis="x",alpha=0.1)
        plt.grid(axis="y",alpha=0.1)
	    
        st.pyplot(plt.gcf())

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')


#todo: poner pie de pagina
#cambiar el punto de maximo y minimo por una recta en las predicciones por horas
#hacer lo de la primera accion en la lista desde la base de datos
