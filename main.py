import streamlit as st
from datetime import date,datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

    workbook=file.open('Investment 2.0')
    workbook2=file.open('Investment 2.0 (intra day)')
		
    st.title('Stock Prediction')

    stocks = ('BBVA.MC', 'IAG.MC')
	
    selected_stock = st.selectbox('Seleccione la compañía para hacer la predicción', stocks)

    sheet = workbook.worksheet(f'{selected_stock} DATA')
    sheet2= workbook.worksheet(f'{selected_stock} CALC')
    sheet3 = workbook2.worksheet(f'{selected_stock} DATA')
    sheet4 = workbook2.worksheet(f'{selected_stock} DATA DIAS')
	
    st.subheader('Predicción para el día siguiente')

    today = date.today()
    dia=today.strftime("%d-%m-%Y")

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
        	
        df=pd.DataFrame([[open,high,low,close]],columns=['Open','High','Low','Close'])
        st.dataframe(df)
	
        st.write('Estadísticas día')	
	
        df=pd.DataFrame([[sub_dia,sub_entre_dias]],columns=['Subida mismo dia (Open-High)','Subida entre dias'])
        st.dataframe(df)
	
        st.write(" ")
        st.write('**Gráfico aproximado del día (formato en horas)**')
	
        high=sheet3.range('H3:H10')
        low=sheet3.range('I3:I10')
	
        for _,i in enumerate(high):
            num=i.value
            high[_]=float(num.replace(',','.'))
	
        for _,i in enumerate(low):
            num=i.value
            low[_]=float(num.replace(',','.'))
	
        high=np.array(high)
        low=np.array(low)
	
        #st.write(high);st.write(low)
	
        fig,ax=plt.subplots()
	
        ax.plot(high,'g',label='High')
        ax.legend(loc="upper right")
        ax.plot(low,'r',label='Low')
        ax.legend(loc="upper right")

        plt.xlabel("Time (h)")
        plt.ylabel("Price (€)")
	
        #ax.invert_yaxis()

        st.pyplot(plt.gcf())
	
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
	
        high=np.array(high)
        low=np.array(low)

        fig,ax=plt.subplots()
	
        ax.plot(high,'g',label='High')
        ax.legend(loc="upper right")
        ax.plot(low,'r',label='Low')
        ax.legend(loc="upper right")

        plt.xlabel("Time (d)")
        plt.ylabel("Price (€)")
	
        #ax.invert_yaxis()
	
        st.pyplot(plt.gcf())
	

#poner en tabla los resultados
#poner incremento en mismo día y entre días
#poner anotacion
