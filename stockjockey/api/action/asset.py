from bs4 import BeautifulSoup
from flask import app
import requests
from sqlalchemy import exists, select
from stockjockey import api
from stockjockey.api.core import query_db
from . import BaseCRUD, get_db
from . import utcnow
from . import Asset, AssetMetric


class AssetHandler(BaseCRUD):
    def __init__(self):
        super().__init__(Asset)

    def record_exists(self, ticker: str):
        table_name = "asset"
        sql = (
            f"SELECT EXISTS (SELECT 1 FROM {table_name}"
            f"WHERE ticker = {ticker});"
        )
        response = query_db(sql)
        return response

    def add_record(self, ticker):
        """Create an asset record"""
        # check if ticker in asset table already
        if self.asset_exists(ticker):
            return

        # retrieve metadata
        app.simfin.get_metadata(ticker)
        metadata = app.simfin.parse_metadata(ticker)

        # insert into asset table
        return self.create(metadata)
    
    def fetch_record(self):
        """Call from frontend to retrieve record info"""
        # check if record exists
        # retrieve record if so
        # create record if not
        # return full record
        pass

    

class AssetMetricHandler(BaseCRUD):
    def __init__(self):
        super().__init__(AssetMetric)

    def record_exists(self, id: str, metric: str, year: int, quarter: str):
        table_name = "asset_metric"
        sql = (
            f"SELECT EXISTS (SELECT 1 FROM {table_name}"
            f"WHERE id = {id});"
        )
        response = query_db(sql)
        return response
            

    def add_records(self, ticker):
        """Create records"""
        # check if ticker in asset table already
        if self.recird_exists(ticker):
            return

        # retrieve metadata
        app.simfin.get_metadata(ticker)
        metadata = app.simfin.parse_metadata(ticker)

        # insert into asset table
        return self.create(metadata)
    

class AssetScraper():
    """Scrape nasdaq.com for asset data
    - this solution is deprecated in favor of simfin data requests
    - this may be of further use for scraping other websites for n12 info
    """
    def __init__(self, ticker):
        self.record = {"ticker": ticker.upper()}
        self.nasdaq_base_url = f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}"
        self.nasdaq_reveps_url = f"{self.nasdaq_base_url}/revenue-eps"

        # define scraping parameters
        self.scrape_params = {
            "meta": {
                "url": self.nasdaq_reveps_url,
                "name": ("div", {"class":"nsdq-quote-header__asset-information-name"}),
                "exchange": ("a", {"class":"topcard__org-name-link"}),
                "sector": ("a", {"class":"topcard__org-name-link"})
            }
        }

    def get_html(self, url):
        """Make request for full html of page and parse to text"""
        resp = requests.get(url)
        soup=BeautifulSoup(resp.text,'html.parser')
        return soup

    def scrape_asset_meta(self):
        """Get asset metadata"""
        if not hasattr(self, "nasdaq_reveps_soup"):
            self.nasdaq_reveps_soup = self.get_html(self.nasdaq_reveps_url)
        
        # scrape asset name
        try:
            self.record["name"] = self.nasdaq_reveps_soup.find("a",{"class":"topcard__org-name-link"}).text.strip()
        except:
            self.record["name"] = None
        
        


def add(ticker):
    # check if ticker refers to a real-life asset?
    # conflict should potentially be handled using try except
    if not conflict_test(ticker=ticker):
        obj = Asset(ticker=ticker)
        get_db().session.add(obj)
        return obj
    return get(ticker=ticker)[0]


def remove(email=None, username=None):
    db = get_db()
    if email:
        obj = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()
    elif username:
        obj = db.session.execute(db.select(User).filter_by(username=username).scalar_one())
        # User.update().where(User.email.data == email).values(deleted=utcnow())
    obj.deleted = utcnow()
    return obj


def update(search={}, value={}):
    db = get_db()
    obj = db.session.execute(db.update(User).filter_by(search)).values(value)


def conflict_test(*args, **kwargs):
    if get(*args, **kwargs):
        return True
    return False
