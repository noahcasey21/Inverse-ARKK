from bs4 import BeautifulSoup as BS
import pandas as pd
import requests
from datetime import datetime

df = pd.DataFrame(columns=["Fund", "Date", "Action", "Ticker", "Company", "Shares", "Percent"])

url_temp = "https://arkinvestdailytrades.com/"
url = "https://arkinvestdailytrades.com/?page=1"

condition = True
while condition:
    tbl = []
    data = requests.get(url).text
    soup = BS(data, 'html.parser')

    table = soup.find('table', class_="tables")

    for row in table.tbody.find_all('tr'):
        columns = row.find_all('td')

        if (columns != []):
            i = 0   
            r = []
            while i < 7:
                r.append(columns[i].text)
                i += 1

            tbl.append(r)

    #concatenate to df
    df = pd.concat([df, pd.DataFrame(tbl, columns=df.columns)], ignore_index=True)
            
    #next url
    pg = soup.find('ul', 'pagination')
    active_pg = pg.find('li', 'page-link disabled')
    try:
        next_url = active_pg.findNextSibling('li').a.get('href')
    except AttributeError:
        condition = False

    #asssign new url

    url = url_temp + next_url

#convert dates to yf format in df
df['Date'] = df["Date"].apply(lambda x : datetime.strptime(x, '%d %b %Y').strftime('%Y-%m-%d'))

#focus just on ARKK
arkk = df[df['Fund']=='ARKK']
arkk.reset_index(drop=True, inplace=True)

tickers = set(arkk['Ticker'].unique())

#fix .US type tickers
problems = [x for x in tickers if "." in x]
for problem in problems:
    new = problem.split(".")[0]
    tickers.remove(problem)
    tickers.add(new)

arkk['Date'] = pd.to_datetime(arkk['Date'])