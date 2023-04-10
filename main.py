import streamlit as st
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

    username = st.text_input('Username:')
    password = st.text_input('Password:',type='password')

    submit=st.button('Submit')

    if submit:        
        
        credentials = st.secrets["credentials"]


        #if username in credentials and credentials[username] == credentials[password]:
        if username in credentials and credentials[1]==password:
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
		
    st.title('Stock Prediction')

    stocks = ('BBVA.MC', 'IAG.MC')
	
    selected_stock = st.selectbox('Seleccione la compañía para hacer la predicción', stocks)

    sheet = workbook.worksheet(f'{selected_stock} DATA')

    st.subheader('Predicción para el día siguiente')

    today = date.today()
    dia=today.strftime("%d/%m/%Y")

    cell=sheet.find(f"{dia}")

    if not sheet.cell(cell.row,3).value:
        p_open = st.text_input('Precio Open: ')
    
    else:
        p_open=''

    prediction=st.button('Hacer predicción',key='4')

    if prediction:

        if p_open:
            sheet.update(f'C{cell.row}',p_open)


        st.text(sheet.range(f'G{cell.row}:J{cell.row}').value)




    
    hide_streamlit_style = """
				<style>
				#MainMenu {visibility: hidden;}
				footer {visibility: hidden;}
				</style>
				"""

    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    st.write('')
    st.markdown('Última actualización (10-04-2023)')
