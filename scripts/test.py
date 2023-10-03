#simple test of scraper and backtest

from scraper import scrape_table, create_table
from backtest import trade

# print("Testing Scrape")
# create_table()
# scrape_table()
# print("Scrape successful!\n-----------------------")
print("-----------------\nTesting trades")
trade()
print("Success!")