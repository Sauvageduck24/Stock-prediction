import streamlit as st
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

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



        values=sheet.range(f'G{cell.row}:J{cell.row}')
        open=values[0].value
        high=values[1].value
        low=values[2].value
        close=values[3].value
	
        values2=sheet2.range(f'G{cell2.row}:K{cell2.row}')
        sub_dia=values2[0].value
        sub_entre_dias=values2[2].value
        anotaciones=values2[4].value
	
        values3=sheet3.range('G3:J3')
        high2=values3[1].value
        low2=values3[2].value
	
        st.write('Predicciones para el día')
        	
        df=pd.DataFrame([[open,high,low,close]],columns=['Open','High','Low','Close'])
        st.dataframe(df)
	
        st.write('Estadísticas día')	
	
        df=pd.DataFrame([[sub_dia,sub_entre_dias]],columns=['Subida mismo dia (Open-High)','Subida entre dias'])
        st.dataframe(df)
	
        st.write('Predicciones para 9:01 - 10:01')

        df=pd.DataFrame([[high2,low2]],columns=['Máximo','Mínimo'])
        st.dataframe(df)
	

#poner en tabla los resultados
#poner incremento en mismo día y entre días
#poner anotacion
