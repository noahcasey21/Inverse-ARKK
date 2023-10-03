import matplotlib.pyplot as plt
from scripts.scraper import create_tables, scrape_tables
from scripts.backtest import trade

def dual_plot():
    """
        Plots side-by-side comparison of normal ARKK trades vs inverse ARKK trades.
    """
    
