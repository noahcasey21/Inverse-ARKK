import pandas as pd
import yfinance as yf
from datetime import datetime
import sqlite3 

"""
	Logic toDo: 
		- deal with sells that were bought before earliest date
		- account for splits and dividends
"""

def trade(inverse=False, forward=False):
	"""
		Mass trading to be initialized on launch. Calculates all historical equity or current

		inverse : False is normal ARKK trades, True is Inverse ARKK trades
		forward : False is daily trades, True will run full backtest on all data. Should only
				be run on startup
	"""

	#initializations
	if forward:
		#confirmed that date styles should match where needed
		date = datetime.today().strftime('%Y-%m-%d')
		base = equity['AMOUNT'][0]

		#only pull todays date trades
		conn = sqlite3.connect('inverse_arkk.db')
		trades = pd.read_sql_query(f"SELECT * FROM TRADES WHERE DATE = {date}", conn)
		conn.commit()
		equity = pd.read_sql_query(f"SELECT * FROM EQUITY WHERE DATE = {date}", conn)
		conn.commit()
		holdings = pd.read_sql_query(f"SELECT * FROM HOLDINGS WHERE DATE = {date}", conn)
		conn.commit()
		conn.close()

	else:
		base = 1

		conn = sqlite3.connect('inverse_arkk.db')
		trades = pd.read_sql_query("SELECT * FROM TRADES", conn)
		conn.commit()
		equity = pd.read_sql_query("SELECT * FROM EQUITY", conn)
		conn.commit()
		holdings = pd.read_sql_query("SELECT * FROM HOLDINGS", conn)
		conn.commit()
		conn.close()

	for i, data in trades.iterrows():
		if date != data['DATE']:
			equity[date] = base
			date = data['DATE']

			#load day's trades 
		ticker = data['TICKER']

		#recalculate equity
		for _, info in holdings.iterrows():
			ticker = info["TICKER"]
			new = yf.download(ticker, date)['Close']
			change = info['PERCENT'] * new / info['Price'] if new > info['Price'] else -1 * info['PERCENT'] * new / info['Price']
			base += change	

		#check new trades
		if data['Buy']:
			if ticker in holdings:
				#calculate average buy
				holdings[ticker]["Price"] = (data['Percent'] * base * yf.download(ticker, date)['Close'] + holdings[ticker]["PERCENT"] * holdings[ticker]["Price"]) / \
					(holdings[ticker]["PERCENT"] + data['Percent'] * base)

				holdings[ticker]["PERCENT"] = holdings[ticker]["PERCENT"] + data['Percent'] * base
				
			else:
				holdings[ticker] = {"PERCENT":base * data["Percent"], "Price": yf.download(ticker, date)['Close']}

		elif data['Sell']:
					holdings[ticker]["PERCENT"] -= (base * data['Percent']) 

		else:
			log(f'Buy/Sell issue at row {i}')

def log(string):
	#log data issues to go clean
	f = open('data_issues.txt','a')
	f.write(string)
	f.close()