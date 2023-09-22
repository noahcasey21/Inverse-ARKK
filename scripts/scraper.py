from bs4 import BeautifulSoup as BS
import pandas as pd
import requests
from datetime import datetime
import sqlite3

def create_table():
    """
        To be executed on first startup or relaunch
    """
    conn = sqlite3.connect("inverse_arkk.db")
    cursor = conn.cursor()

    #remove table 
    cursor.execute('DROP TABLE IF EXISTS TRADES')

    table = """CREATE TABLE TRADES (
                FUND CHAR(4),
                DATE TEXT,
                ACTION VARCHAR(255),
                TICKER VARCHAR(255),
                COMPANY VARCHAR (255),
                SHARES INT,
                PERCENT FLOAT,
            );"""
    
    cursor.execute(table)

    cursor.execute('DROP TABLE IF EXISTS EQUITY')

    table = """ CREATE TABLE EQUITY (
            DATE TEXT,
            AMOUNT FLOAT
            );"""
    
    cursor.execute(table)

    cursor.execute('DROP TABLE IF EXISTS HOLDINGS')

    table = """ CREATE TABLE HOLDINGS (
            TICKER VARCHAR,
            PERCENT FLOAT,
            PRICE FLOAT
            );"""
    
    cursor.execute(table)

    conn.close()


def scrape_table(date=None):
    """
        If date is none, scrape entire table
        If date is present, scrape only rows that match date (should be most recent date)
    """
    if date != None:
        date = str(date.strftime('%d %b %Y')) #same format that appears in table
        date_lock = True

    else:
        create_table() #create database table as reconfiguration needed
        
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

                if date_lock and r[1] != date:
                    condition=False
                    break
                
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
    
    #upload to database
    try:
        # Connect to DB and create a cursor
        conn = sqlite3.connect('inverse_arkk.db')
        
        arkk.to_sql('TRADES', conn, if_exists='append', index=False)

    except sqlite3.Error as error:
        f = open('db_errors.txt', 'a')
        f.write(f'Error with uploading date = {date} data')
        f.close()

    finally:
        if conn:
            conn.close()