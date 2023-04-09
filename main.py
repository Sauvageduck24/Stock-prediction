import streamlit as st
from datetime import date


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
	password = st.text_input('Password:')

	submit=st.button('Submit')

	if submit:

		credentials = {
			'admin': '2022'
		}


		if username in credentials and credentials[username] == password:
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
	st.title('Stock Prediction')

	stocks = ('BBVA.MC', 'IAG.MC')
	selected_stock = st.selectbox('Seleccione la compañía para hacer la predicción', stocks)

	targets=['Open','High','Low','Close']

	st.subheader('Predicción para el día siguiente')

	prediction=st.button('Hacer predicción',key='4')

	if prediction:
		st.text(f'{selected_stock}')



	hide_streamlit_style = """
				<style>
				#MainMenu {visibility: hidden;}
				footer {visibility: hidden;}
				</style>
				"""

	st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
	st.write('')
	st.markdown('Última actualización (10-04-2023)')
	
	
	
#TODO: conectar a google sheets
#comprobar si esta el precio de open puesto
#mostrar resultados
