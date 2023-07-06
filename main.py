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
from matplotlib import font_manager

#font_dir=['Dense-Regular.otf']
#font_files = font_manager.findSystemFonts(fontpaths=font_dir,fontext='otf')

#for font_file in font_files:
    #font_manager.fontManager.addfont(font_file)

#plt.rcParams['font.family'] = 'Dense'

image = Image.open('market-master-logo.png')

st.set_page_config(page_title="Market Master",page_icon="market-master-web-logo.ico",initial_sidebar_state="auto")#,layout='wide')

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
	    
st.markdown(hide_streamlit_style, unsafe_allow_html=True)     # para quitar marca de agua

import streamlit as st

footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: black;
color: white;
text-align: center;
}

</style>
<div class="footer">
<p>Market Master ©</p>
</div>
"""

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

st.markdown(footer,unsafe_allow_html=True)

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
        st.write(f"You are logged in as: {name.upper()}")

    with col2:
        authenticator.logout('Logout', 'main', key='unique_key')
	    
    st.image(image)

    stocks = ['BBVA','IAG']
	
    if stock_f[pos_username] in stocks:
        del stocks[stocks.index(stock_f[pos_username])]
        stocks.insert(0,stock_f[pos_username])
	
    selected_stock = st.selectbox('Select stock name', stocks)

    if selected_stock=='BBVA':
        search='1COITRN8LVx3Sa2zDQRYn-Igt91bg_mZlYqdeGE5KpAQ'
	
    workbook=file.open_by_key(search)

    sheet = workbook.worksheet('ONE DAY DATA')
    sheet2= workbook.worksheet('CALC')
    sheet3 = workbook.worksheet('HOUR DATA')
    sheet4 = workbook.worksheet('DAY DATA')

    st.subheader('Prediction for the day')

    cell=sheet.find(f"{dia}")
    cell2=sheet2.find(f"{dia}")
	
    if cell is None:
    	st.warning('No Market Today 😥', icon="⚠️")
    	raise Exception('No Market Today 😥')

	
    if not sheet.cell(cell.row,3).value and roles_f[pos_username]=='ADMIN':
        p_open = st.text_input('Precio Open: ')
        try:
            p_open = p_open.replace('.',',')
        except:
            pass
    
    else:
        p_open=''

    prediction=st.button('Make Prediction',key='4')

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
	
        values2=sheet2.range(f'F{cell2.row}:H{cell2.row}')
        high_accuracy=values2[0].value
        low_accuracy=values2[1].value
        close_accuracy=values2[2].value
	    
        open=float(open.replace(',','.'))
        high=float(high.replace(',','.'))
        low=float(low.replace(',','.'))
        close=float(close.replace(',','.'))

        st.write(" ")	    
        st.write('Prediction for the day')
        
        new_real=[high,low,close]
	
        df_=pd.DataFrame([[open,high,low,close]],columns=['Open','High','Low','Close'])
	    
        st.dataframe(df_)
	
        st.write('Mean Accuracies')	
	
        df=pd.DataFrame([[high_accuracy,low_accuracy,close_accuracy]],columns=['High Mean Accuracy','Low Mean Accuracy','Close Mean Accuracy'])
        st.dataframe(df)

        high_low=sheet3.range("H3:I10")	    
        high=[];low=[]

        for _,i in enumerate(high_low):
            if	_%2==0:	
                high.append(i)
		    
            else:
                low.append(i)
	    
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

        ax.plot(xs[mask],low[mask],linestyle='-',marker='o',color='r',label='Low')
        ax.plot(xs[mask3],mean[mask3],linestyle='-',color='gray',alpha=0)
        ax.plot(xs[mask2],high[mask2],linestyle='-',marker='o',color='g',label='High')

        z_h=[]
        z_l=[]

        for _,i in enumerate(high[mask2]):
            if _==0:
                z_h.append("")
            else:
                dif=((i*100)/high[mask2][_-1])-100
                z_h.append(f"{round(dif,2)} %")    

        for _,i in enumerate(low[mask]):
            if _==0:
                z_l.append("")
            else:
                dif=((i*100)/low[mask][_-1])-100
                z_l.append(f"{round(dif,2)} %")    
	    
        #for X, Y, Z in zip(xs[mask], high[mask], z_h):
            #ax.annotate('{}'.format(Z), xy=(X,Y), xytext=(-5,10), ha='right',textcoords='offset points',color='#66fcf0')

        #for X, Y, Z in zip(xs[mask], low[mask], z_l):
            #ax.annotate('{}'.format(Z), xy=(X,Y), xytext=(-5,-16), ha='right',textcoords='offset points',color='#66fcf0')
	    
        ax.plot(real,color='white',label='Real Data',alpha=0.9)

        pos_high,=np.where(high==max(high))
        pos_low,=np.where(low==min(low))
	    
        pos_high=pos_high.flat[0]
        pos_low=pos_low.flat[0]

        pos_high=pos_high.flat[0]
        pos_low=pos_low.flat[0]
        	
        ax.scatter([pos_high,pos_low,len(low)-60],new_real,color='gray',label='Predicted Values')

        ax.fill_between(xs[mask2],high[mask2],mean[mask3], color="green", alpha=0.1)
        ax.fill_between(xs[mask2],mean[mask3],low[mask], color="red", alpha=0.1)
	    
        poss=['^','v']
	
        if pos_low<pos_high:
            ax.scatter(pos_high,max(high)+0.01,marker=poss[1],color='r')
            ax.scatter(pos_low,min(low)-0.01,marker=poss[0],color='g')
	
        dif=round((100-(min(low)*100)/max(high)),2)
	
        ax.axhline(y=max(high), color='g',linestyle='--')
        ax.axhline(y=min(low) , color='r',linestyle='--')
	
        ax.axhline(y=new_real[0], color='gray', linestyle='--',alpha=0.5)
        ax.axhline(y=new_real[1], color='gray', linestyle='--',alpha=0.5)
	
        plt.xlabel("Time (h)")
        plt.ylabel("Price")
	
        new_time=['9','10','11','12','13','14','15','16']
	
        plt.xticks(np.arange(0, len(low), 60),new_time)
	
        ax.legend(loc="best")

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        ax.tick_params(colors='white')
	    
        ax.set_facecolor((0, 0, 0))
        fig.patch.set_facecolor((0, 0, 0))

        ax.set_title('Approximate chart of the day (1 hour format)',color='white')
	    
        plt.grid(axis="x",alpha=0.2)
        plt.grid(axis="y",alpha=0.2)
   
        st.pyplot(plt.gcf())

        #------------------------------------------------------------------------------------

        data = yf.download(f'{selected_stock}.MC', period=f'16d',interval=f'1d',progress=False)

        now = datetime.now()
	
        if now.hour+2>9:
            if now.minute>15:
                pass
        else:
            data=data[:-1]
	    
        time=[]

        for i in range(len(data)+1):
            time.append(i)
	    
        real_h=[]
        real_l=[]
	    
        for index,row in data.iterrows():
            real_h.append(row['High'])
            real_l.append(row['Low'])
	    
        fig,ax=plt.subplots() #ancho , alto

        ax.set_facecolor((0, 0, 0))
        fig.patch.set_facecolor((0, 0, 0))

        real_h_=real_h.copy()
        real_l_=real_l.copy()
	    
        real_h_.append(df_.iloc[0]['High'])
        real_l_.append(df_.iloc[0]['Low'])
	    
        ax.set_title('Prediction of the current day in relation to the previous real ones',color='white')

        ax.plot(real_h_,color='g',linestyle='-',marker='o',label='Predicted Data High',alpha=0.9)
        ax.plot(real_l_,color='r',linestyle='-',marker='o',label='Predicted Data Low',alpha=0.9)	    
	    
        ax.plot(real_h,color='white',label='Real Data',alpha=0.9)
        ax.plot(real_l,color='white',alpha=0.9)

        z_h=[]
        z_l=[]

        for _,i in enumerate(real_h_):
            if _==0:
                z_h.append("")
            else:
                dif=((i*100)/real_h_[_-1])-100
                z_h.append(f"{round(dif,2)} %")    

        for _,i in enumerate(real_l_):
            if _==0:
                z_l.append("")
            else:
                dif=((i*100)/real_l_[_-1])-100
                z_l.append(f"{round(dif,2)} %")    
	    
        #for X, Y, Z in zip(time, real_h_, z_h):
            #ax.annotate('{}'.format(Z), xy=(X,Y), xytext=(-5,10), ha='right',textcoords='offset points',color='#66fcf0')

        #for X, Y, Z in zip(time, real_l_, z_l):
            #ax.annotate('{}'.format(Z), xy=(X,Y), xytext=(-5,-16), ha='right',textcoords='offset points',color='#66fcf0')
	    
        plt.grid(axis="x",alpha=0.2)
        plt.grid(axis="y",alpha=0.2)

        ax.legend(loc="best")

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        ax.tick_params(colors='white')

        plt.ylabel("Price")	    
        plt.xlabel("Time (1 day)")

        new_time=[]

        for i in range(len(data)):
            new_time.append(i+1)	

        new_time.append("Today")
	    
        plt.xticks(np.arange(0, len(real_l_), 1),new_time)
	    
        st.pyplot(plt.gcf())

        #------------------------------------------------------------------------------------
        #32 Day Forecast # titulo de grafico
	    
        #high_low=sheet4.range("H3:I34")	    
        #high=[];low=[]

        #for _,i in enumerate(high_low):
            #if _%2 ==0:	
                #high.append(i)
		    
            #else:
                #low.append(i)

        #------------------------------------------------------------------------------------
        #Past Days Accuracy Demo Predictions # poner esto como titulo de grafico

        real_predicted_high_low=sheet.range("D3:I1000")
        high=[];low=[];predicted_high=[];predicted_low=[]

        for _,i in enumerate(real_predicted_high_low):
            if i.value != "0,000":
                if (_+1)%6 == 0:
                    predicted_low.append(i.value)
                    predicted_high.append(real_predicted_high_low[_-1].value)
                    low.append(real_predicted_high_low[_-4].value)
                    high.append(real_predicted_high_low[_-5].value)


        st.write(predicted_low)        

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
