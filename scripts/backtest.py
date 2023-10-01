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
		equity = pd.read_sql_query(f"SELECT * FROM EQUITY ORDER BY ROWID ASC LIMIT 1", conn)
		conn.commit()
		holdings = pd.read_sql_query(f"SELECT * FROM HOLDINGS", conn, index_col='TICKER')
		conn.commit()
		conn.close()

		#batch load yf info
		stock_info = yf.download(holdings['TICKER'].tolist(), date)['Close']

	else:
		base = 1

		conn = sqlite3.connect('inverse_arkk.db')
		trades = pd.read_sql_query("SELECT * FROM TRADES ORDER BY ROWID DESC", conn)
		conn.commit()
		equity = pd.read_sql_query("SELECT * FROM EQUITY", conn)
		conn.commit()
		holdings = pd.read_sql_query("SELECT * FROM HOLDINGS", conn, index_col='TICKER')
		conn.commit()
		conn.close()

		date = trades['DATE'][0]

		#batch load yf info
		stock_info = yf.download(holdings['TICKER'].tolist(), start=date)['Close']

	"""
		stock_info: Ticker is column, date is index
	"""

	for i, data in trades.iterrows():
		if date != data['DATE']:
			#recalculate equity on currently held assets
			for _ticker, info in holdings.iterrows():
				pct = info[0]
				idx = stock_info.index.get_loc(date)
				new = stock_info[date, _ticker]
				old = stock_info[idx-1, _ticker]
				change = pct * new / old if new > old else -1 * pct * new / old
				base += change	

			equity[date] = base
			date = data['DATE']

		#load rows's trades 
		ticker = data['TICKER']

		#check new trades
		if ('sell' in data['ACTION'].lower() if inverse else 'buy' in data['ACTION'].lower()):
			if ticker in holdings.index:
				#increase percent holding
				holdings.loc[ticker] = holdings[ticker] + data['Percent'] * base
				
			else:
				holdings.loc[ticker] = base * data["Percent"]

		elif ('buy' in data['ACTION'].lower() if inverse else 'sell' in data['ACTION'].lower()) and ticker in holdings.index:
					holdings.loc[ticker] -= (base * data['Percent']) 

		else:
			log(f'Buy/Sell issue at row {i} (may be sell before buy due to time constraints)')

	#load back into database
	conn = sqlite3.connect('inverse_arkk.db')
	equity.to_sql('EQUITY', conn, if_exists='replace', index=False)

	holdings.to_sql('HOLDINGS', conn, if_exists='replace', index=False)


def log(string):
	#log data issues to go clean
	f = open('data_issues.txt','a')
	f.write(string)
	f.close()