import pandas as pd
import yfinance as yf
from datetime import datetime
import sqlite3 
from sqlite3 import connect 

class TradingEngine:
	# may not need to be in a class, this is just a collection of functions 
	# that will be called, new class instance would need to be created every night...

	def __init__(self, df):
		self.df = df
		#setup equity
		self.init_equity()

	def tradeLogic():
		...
		#fucntion to be shared between forward and backward test
		#or combine the functions and generalize

	#will run daily 
	def forwardtest(self, df):
		date = datetime.today().strftime('%Y-%m-%d')
		
		# check database for new entries
		# run similar trading process as below (may want to create function to reduce repetition

	#setup historical prices dataframe that adds row daily for fast lookup in equity 
	def backtest(self, df, inverse=False):
		holdings = {} #{"SPY":{"Pct":x, "Price":y}, ...}
		equity = pd.Series()

		date = None
		base = 1

		for i, data in df.iterrows():
			if date != data['Date']:
				equity[date] = base
				date = data['Date']

				#load day's trades 
			ticker = data['Ticker']

			#recalculate equity
			for holding, info in holdings:
				new = yf.download(ticker, date)['Close']
				change = info['Pct'] * new / info['Price'] if new > info['Price'] else -1 * info['Pct'] * new / info['Price']
				base += change	

			#check new trades
			if data['Buy']:
				if ticker in holdings:
					#calculate average buy
					holdings[ticker]["Price"] = (data['Percent'] * base * yf.download(ticker, date)['Close'] + holdings[ticker]["Pct"] * holdings[ticker]["Price"]) / \
						(holdings[ticker]["Pct"] + data['Percent'] * base)

					holdings[ticker]["Pct"] = holdings[ticker]["Pct"] + data['Percent'] * base
					
				else:
					holdings[ticker] = {"Pct":base * data["Percent"], "Price": yf.download(ticker, date)['Close']}

			elif data['Sell']:
						holdings[ticker]["Pct"] -= (base * data['Percent']) 

			else:
				self.log(f'Buy/Sell issue at row {i}')

	def log(self, string):
		#log data issues to go clean
		f = open('data_issues.txt','a')
		f.write(string)
		f.close()

	def init_equity(self):
		start = self.df['Date'].min()
		end = self.df['Date'].max()

		self.equity = pd.Series(index=pd.date_range(start, end))