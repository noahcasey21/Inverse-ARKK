#setup historical prices dataframe that adds row daily for fast lookup in equity 

holdings = {} #{"SPY":{"Pct":x, "Price":y}, ...}

date = None
base = 1

for i, data in arkk.iterrows():
	if date != data['Date']:
		date = data['Date']
		base = equity[date - 1]

		#load day's trades 

    ticker = data['Ticker']

    #recalculate equity
    for holding, info in holdings:
        #not correct: math needs to be fixed to account for daily price change as well as average price
        dif = yf.download(ticker, date)['Close']
        change = info['Pct'] * dif / info['Price']
        base += change
        

	#check new trades
	if data['Buy']:
		if ticker in holdings:
			#calculate average buy
			holdings[ticker]["Price"] = (data['Percent'] * base * yf.download(ticker, date)['Close'] + holdings[ticker]["Pct"] * holdings[ticker]["Price"]) / 
				(holdings[ticker]["Pct"] + data['Percent'] * equity)

			holdings[ticker]["Pct"] = holdings[ticker]["Pct"] + data['Percent'] * base
			
			
		else:
			holdings[ticker] = {"Pct":base * data["Percent"], 
							"Price" = yf.download(ticker, date)['Close']}

	elif data['Sell']:
				holdings[ticker]["Pct"] -= (base * data['Percent']) #all that is needed here?

	else:
		log(f'Buy/Sell issue at row {i}')


def log(string):
	#log data issues to go clean
	f = open('data_issues.txt','a')
	f.write(string)
	f.close()
