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

st.set_page_config(page_title="Market Master")

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

credentials={
    "usernames": {
        "esteban": {
            "email":st.secrets['email'],    
            "name":st.secrets['name'],    
            "password":st.secrets['password']
	}	    
    }
}

authenticator = stauth.Authenticate(
    credentials, 
    st.secrets['name_cookies'],
    st.secrets['key'],
    st.secrets['expiry_days'],
    #st.secrets['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')


if authentication_status:
	
    creds=ServiceAccountCredentials.from_json_keyfile_dict(drive_credentials,scopes=scopes)

    file = gspread.authorize(creds)
		
    st.title('Market Master')

    stocks = ('BBVA','IAG')
	
    selected_stock = st.selectbox('Seleccione la compañía para hacer la predicción', stocks)

    if selected_stock=='BBVA':
        search='1COITRN8LVx3Sa2zDQRYn-Igt91bg_mZlYqdeGE5KpAQ'
	
    #workbook=file.open(f'Market Master {selected_stock}')
    workbook=file.open_by_key(search)

    sheet = workbook.worksheet('ONE DAY DATA')
    sheet2= workbook.worksheet('CALC')
    sheet3 = workbook.worksheet('HOUR DATA')
    sheet4 = workbook.worksheet('DAY DATA')
    sheet5 = workbook.worksheet('MINS DATA')
	
    st.subheader('Predicción para el día siguiente')

    today = date.today()
    dia=today.strftime("%d-%m-%Y")

    cell=sheet.find(f"{dia}")
    cell2=sheet2.find(f"{dia}")
	
    if cell is None:
    	st.error('Hoy no hay bolsa 😥', icon="🚨")
    	raise Exception('Hoy no hay bolsa 😥')

	
    if not sheet.cell(cell.row,3).value:
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

            if not sheet5.cell(3,3).value:
                sheet5.update('C3',p_open)	
	    
        values=sheet.range(f'G{cell.row}:J{cell.row}')
        open=values[0].value
        high=values[1].value
        low=values[2].value
        close=values[3].value
	
        values2=sheet2.range(f'G{cell2.row}:K{cell2.row}')
        sub_dia=values2[0].value
        sub_entre_dias=values2[2].value
        anotaciones=values2[4].value

        open=float(open.replace(',','.'))
        high=float(high.replace(',','.'))
        low=float(low.replace(',','.'))
        close=float(close.replace(',','.'))
	    
        st.write('Predicciones para el día')
        
        new_real=[high,low,close]
	
        df=pd.DataFrame([[open,high,low,close]],columns=['Apertura','Máximo','Mínimo','Cierre'])
        st.dataframe(df)
	
        st.write('Estadísticas día')	
	
        df=pd.DataFrame([[sub_dia,sub_entre_dias]],columns=['Subida mismo dia (Open-High)','Subida entre dias'])
        st.dataframe(df)
	
        st.write(" ")
        st.write('**Gráfico aproximado del día (formato en 30 minutos)**')
	
        high=sheet3.range('H3:H10')
        low=sheet3.range('I3:I10')
        
        high_mins=sheet5.range('H3:H18')
        low_mins=sheet5.range('I3:I18')
	    
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

        for _,i in enumerate(high_mins):
            num=i.value
            high_mins[_]=float(num.replace(',','.'))
	
        for _,i in enumerate(low_mins):
            num=i.value
            low_mins[_]=float(num.replace(',','.'))
	
        mean=[]
        mean_mins=[]
        time=[]

        for i,j in zip(high,low):
            mean.append((i+j)/2)

        for i,j in zip(high_mins,low_mins):
            mean_mins.append((i+j)/2)
	    
        for i in range(len(high)):
            time.append(i)

        high=np.array(high)
        low=np.array(low)
        mean=np.array(mean)

        high_mins=np.array(high_mins)
        low_mins=np.array(low_mins)
        mean_mins=np.array(mean_mins)
	    
        time=np.array(time)

        real=[]
	    
        for index,row in data.iterrows():
            real.append(row['Close'])
	    
        #------------------------------------------------------------------------------------
	    
        low_mins=low_mins.tolist()
        high_mins=high_mins.tolist()
        mean_mins=mean_mins.tolist()
	    
        new_low=[]
        new_high=[]
        new_mean=[]
	    
        last_low=0
        last_high=0
        last_mean=0    
	    
        for _,i in enumerate(low_mins):
            if _!=len(low_mins):
                rango=30
            else:
                rango=30
		
            for j in range(rango):
                if j==0:
                    new_low.append(i)
                    last_low=i
                else:			
                    new_low.append(np.nan)

        for _,i in enumerate(high_mins):
            if _!=len(low_mins):
                rango=30
            else:
                rango=30
		
            for j in range(rango):
                if j==0:
                    new_high.append(i)
                    last_high=i
                else:
                    new_high.append(np.nan)

        for _,i in enumerate(mean_mins):
            if _!=len(low_mins):
                rango=30
            else:
                rango=30
		
            for j in range(rango):
                if j==0:
                    new_mean.append(i)
                    last_mean=i
                else:
                    new_mean.append(np.nan)

        low_mins=np.array(new_low)
        high_mins=np.array(new_high)
        mean_mins=np.array(new_mean)
	    
        time=[]

        for i in range(len(high)):
            time.append(i)

        time=np.array(time)

        mask=np.isfinite(low_mins)
        mask2=np.isfinite(high_mins)
        mask3=np.isfinite(mean_mins)
	    
        xs=np.arange(len(low_mins))
        xs2=np.arange(len(high_mins))
        xs3=np.arange(len(mean_mins))
	    
        fig,ax=plt.subplots()

        ax.plot(xs[mask],low_mins[mask],linestyle='-',color='r',label='Mínimo')

        ax.plot(xs[mask3],mean_mins[mask3],linestyle='-',color='gray',alpha=0)

        ax.plot(xs[mask2],high_mins[mask2],linestyle='-',color='g',label='Máximo')    
	    
        ax.plot(real,color='black',label='Real Data',alpha=0.85)

        pos_high,=np.where(high_mins==max(high_mins))
        pos_low,=np.where(low_mins==min(low_mins))
	    
        pos_high=pos_high.flat[0]
        pos_low=pos_low.flat[0]

        pos_high=pos_high.flat[0]
        pos_low=pos_low.flat[0]
        	
        ax.scatter([pos_high,pos_low,len(low_mins)-30],new_real,color='gray',label='Valores predichos')

        ax.fill_between(xs[mask2],high_mins[mask2],mean_mins[mask3], color="green", alpha=0.1)
        ax.fill_between(xs[mask2],mean_mins[mask3],low_mins[mask], color="red", alpha=0.1)
	    
        poss=['^','v']
	
        if pos_low<pos_high:
            ax.scatter(pos_high,max(high_mins)+0.01,marker=poss[1],color='r')
            ax.scatter(pos_low,min(low_mins)-0.01,marker=poss[0],color='g')
	
        dif=round((100-(min(low_mins)*100)/max(high_mins)),2)
	
        ax.axhline(y=max(high_mins), color='g',linestyle='--')
        ax.axhline(y=min(low_mins) , color='r',linestyle='--')
	
        ax.axhline(y=new_real[0], color='gray', linestyle='--',alpha=0.3)
        ax.axhline(y=new_real[1], color='gray', linestyle='--',alpha=0.3)
	
        #if dif>=0:
            #ax.text(20,max(high), f'{dif} %', va='center', ha='center', backgroundcolor='w',color='g')
        #else:
            #ax.text(400, min(low), f'{dif} %', va='center', ha='center', backgroundcolor='w',color='r')
	
        plt.xlabel("Tiempo (h)")
        plt.ylabel("Precio (€)")
	
        new_time=['9','10','11','12','13','14','15','16']
	
        plt.xticks(np.arange(0, len(low_mins), 60),new_time)
	
        ax.legend(loc="best")
	
        st.pyplot(plt.gcf())

        #------------------------------------------------------------------------------------

        st.write(" ")	    
        st.write('**Gráfico aproximado del día (formato en 1 hora)**')
	    
        low=low.tolist()
        high=high.tolist()
        mean=mean.tolist()
	    
        new_low=[]
        new_high=[]
        new_mean=[]
	    
        last_low=0
        last_high=0
        last_mean=0
	
        for _,i in enumerate(low):
            if _!=len(low):
                rango=60
            else:
                rango=60
		
            for j in range(rango):
                if j==0:
                    new_low.append(i)
                    last_low=i
                else:			
                    new_low.append(np.nan)

        for _,i in enumerate(high):
            if _!=len(low):
                rango=60
            else:
                rango=60
		
            for j in range(rango):
                if j==0:
                    new_high.append(i)
                    last_high=i
                else:
                    new_high.append(np.nan)

        for _,i in enumerate(mean):
            if _!=len(low):
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
	    
        fig,ax=plt.subplots()

        ax.plot(xs[mask],low[mask],linestyle='-',color='r',label='Mínimo')

        ax.plot(xs[mask3],mean[mask3],linestyle='-',color='gray',alpha=0)

        ax.plot(xs[mask2],high[mask2],linestyle='-',color='g',label='Máximo')
	
        ax.plot(real,color='black',label='Real Data',alpha=0.85)

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
	
        st.pyplot(plt.gcf())

        #------------------------------------------------------------------------------------
	    
        st.write(" ")	
        st.write('**Gráfico aproximado para 8 días (orgánicos)**')
	
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
		
	
        fig,ax=plt.subplots()
		
        ax.plot(high,'g',label='Máximo')
        ax.legend(loc="upper right")
        ax.plot(mean,'gray',alpha=0)
        ax.plot(low,'r',label='Mínimo')
        ax.legend(loc="upper right")

        if real:	
            ax.scatter([0],real,color='black',label='Día actual')
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
	
        plt.xlabel("Tiempo (d)")
        plt.ylabel("Precio (€)")
	
        st.pyplot(plt.gcf())

        authenticator.logout('Logout', 'main', key='unique_key')

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
