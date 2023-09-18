from flask import Flask
#from scripts.backtest import sometihng
from scripts.scraper import create_table, scrape_table
import atexit 
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

def run_scripts():
    scrape_table(date=datetime.today)
    #run backtest

@app.route('/')
def home():
    return "Hello world"

#setup script scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_scripts, 'interval', days=1)
scheduler.start()

# Shutdown cron thread if the web process is stopped
atexit.register(lambda: scheduler.shutdown(wait=False))

if __name__ == "__main__":
    # initial startup scrape
    scrape_table()
    app.run(debug=True)