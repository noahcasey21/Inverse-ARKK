#simple test of scraper and backtest

from scraper import scrape_table, create_table
from backtest import trade

def test_scape():
    create_table()
    scrape_table()

def test_full():
    test_scape()
    trade()