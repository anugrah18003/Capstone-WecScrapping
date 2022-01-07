from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'table table-striped table-hover table-hover-solid-row table-simple history-data'})
row = table.find_all('td')

row_length = int(len(row)/4)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    # Mengambil data tanggal, dimulai dari index ke 0(kolom 1) dan ditambah setiap lipatan 4 (karena ada 4 kolom)
    tanggal = row[0+(i)*4].text
    #print(tanggal)
    # Mengambil data harga harian, dimulai dari index ke 2(kolom 3) dan ditambah setiap lipatan 4 (karena ada 4 kolom)
    harga_harian = row[2+(i)*4].text[:-4]
    #print(harga_harian)
    # Menyimpan kedalam temp sebagai list
    temp.append((tanggal, harga_harian))    

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Date', 'Daily_Price'))

#insert data wrangling here
df['Daily_Price'] = df['Daily_Price'].str.replace(",","")
df['Daily_Price'] = df['Daily_Price'].astype('float64')
df['Date'] = df['Date'].astype('datetime64')

awal = df['Date'].min()
akhir = df['Date'].max()

df = df.set_index('Date')
kurs = df
index_date = pd.date_range(start=awal, end=akhir)
kurs = kurs.reindex(index_date)

kurs = kurs.fillna(method='ffill')
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{kurs["Daily_Price"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = kurs.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)