import streamlit as st
from datetime import date,datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings

st.set_page_config(page_title="Market Master")

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


app_state = st.experimental_get_query_params()
# Display saved result if it exist

if 'session' in app_state:
    logged_in=True
	#saved_result = app_state["my_saved_result"][0]
    #st.write("Here is your result", saved_result)
else:
    #st.write("No result to display, compute a value first.")
    logged_in=False


if not logged_in:

    username = st.text_input('Usuario:')
    password = st.text_input('Contraseña:',type='password')

    submit=st.button('Entrar')

    if submit:        
        
        credentials = st.secrets["credentials"]


        #if username in credentials and credentials[username] == credentials[password]:
        if credentials[0]==username and credentials[1]==password:
            st.experimental_set_query_params(session='session')
            logged_in = True

        if not logged_in:
			# If credentials are invalid show a message and stop rendering the webapp
            st.warning('Invalid credentials')
            st.stop()

		#available_views = ['report']
		#if view not in available_views:
			# I don't know which view do you want. Beat it.
			#st.warning('404 Error')
			#st.stop()


if logged_in:
	
    creds=ServiceAccountCredentials.from_json_keyfile_dict(drive_credentials,scopes=scopes)

    file = gspread.authorize(creds)

    #workbook=file.open('Investment 2.0')
    #workbook2=file.open('Investment 2.0 (intra day)')
		
    st.title('Market Master')

    stocks = ('BBVA','IAG')
	
    selected_stock = st.selectbox('Seleccione la compañía para hacer la predicción', stocks)

    workbook=file.open(f'Market Master {selected_stock}')

    sheet = workbook.worksheet('ONE DAY DATA')
    sheet2= workbook.worksheet('CALC')
    sheet3 = workbook.worksheet('HOUR DATA')
    sheet4 = workbook.worksheet('DAY DATA')
	
    st.subheader('Predicción para el día siguiente')

    today = date.today()
    dia=today.strftime("%d-%m-%Y")
    dia="05-06-2023"
    #dia="02-06-2023"
    #dia="01-06-2023"
    #dia="31-05-2023"

    cell=sheet.find(f"{dia}")
    cell2=sheet2.find(f"{dia}")

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


        values=sheet.range(f'G{cell.row}:J{cell.row}')
        open=values[0].value
        high=values[1].value
        low=values[2].value
        close=values[3].value
	
        values2=sheet2.range(f'G{cell2.row}:K{cell2.row}')
        sub_dia=values2[0].value
        sub_entre_dias=values2[2].value
        anotaciones=values2[4].value
	
	
        st.write('Predicciones para el día')
        
        new_real=[high,low,close]
	
        df=pd.DataFrame([[open,high,low,close]],columns=['Apertura','Máximo','Mínimo','Cierre'])
        st.dataframe(df)
	
        st.write('Estadísticas día')	
	
        df=pd.DataFrame([[sub_dia,sub_entre_dias]],columns=['Subida mismo dia (Open-High)','Subida entre dias'])
        st.dataframe(df)
	
        st.write(" ")
        st.write('**Gráfico aproximado del día (formato en horas)**')
	
        high=sheet3.range('H3:H10')
        low=sheet3.range('I3:I10')
	
        data = yf.download(f'{selected_stock}.MC', period=f'2d',interval=f'1m',progress=False)

        now = datetime.now()
        #now=now.replace(tzinfo=datetime.timezone.utc)	
	
        if now.hour+2>9:
            if now.minute>15:
                pass
                data=data[:-7*60]
        else:
            data=data[:-9*60]
	
	
        #if len(data)>7*60:
            #data=data[:-30]
	
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
	
        #---------------------------------------------
	
        #high=[6.603,6.646,6.683,6.680,6.671,6.663,6.655,6.653]
        #low=[6.548,6.591,6.630,6.626,6.616,6.608,6.605,6.603]
        #mean=[]
        #time=[]

        #for i,j in zip(high,low):
            #mean.append((i+j)/2)

        #for i in range(len(high)*60):
            #time.append(i)

        #high=np.array(high)
        #low=np.array(low)
        #mean=np.array(mean)
        #time=np.array(time)

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
            for j in range(60):
                if j==0:
                    new_low.append(i)
                    last_low=i
                else:
                    new_low.append(last_low)

        for _,i in enumerate(high):
            for j in range(60):
                if j==0:
                    new_high.append(i)
                    last_high=i
                else:
                    new_high.append(last_high)

        for _,i in enumerate(mean):
            for j in range(60):
                if j==0:
                    new_mean.append(i)
                    last_mean=i
                else:
                    new_mean.append(last_mean)

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
        #ax.legend(loc="best")

        ax.plot(xs[mask3],mean[mask3],linestyle='-',color='gray',alpha=0)

        ax.plot(xs[mask2],high[mask2],linestyle='-',color='g',label='Máximo')
        #ax.legend(loc="best")
	
        ax.plot(real,color='black',label='Real Data',alpha=0.85)
        #ax.legend(loc="best")
	

        pos_high,=np.where(high==max(high))
        pos_low,=np.where(low==min(low))
	
        pos_high=pos_high.flat[29]
        pos_low=pos_low.flat[29]
	
        for _,i in enumerate(new_real):
            new_real[_]=float(i.replace(',','.'))	
        	
        ax.scatter([pos_high,pos_low,len(low)-60],new_real,color='gray',label='Valores predichos')
        #ax.legend(loc="best")

        ax.fill_between(xs[mask2],high[mask2],mean[mask3], color="green", alpha=0.1)
        ax.fill_between(xs[mask2],mean[mask3],low[mask], color="red", alpha=0.1)
	
        poss=['^','v']
	
        if pos_low<pos_high:
            ax.scatter(pos_high,max(high)+0.01,marker=poss[1],color='r')
            ax.scatter(pos_low,min(low)-0.01,marker=poss[0],color='g')
	
        dif=round((100-(min(low)*100)/max(high)),2)
	
        ax.axhline(y=max(high), color='g',linestyle='--')
        ax.axhline(y=min(low) , color='r',linestyle='--')
	
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
	
        #---------------------------------------------
	
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
	

#poner en tabla los resultados
#poner incremento en mismo día y entre días
#poner anotacion
