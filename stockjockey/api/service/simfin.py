# Import dependencies
import os
import threading
import time
from typing import Any, Dict
import requests

from stockjockey.util.period import last_quarters, last_years


class SimfinApiHandler():
    def __init__(self, api_key):
        self.api_key = api_key
        self.url_base = "https://backend.simfin.com/api/v3/"
        self.urls = {
            "metadata": f"{self.url_base}companies/general/verbose",
            "statements": f"{self.url_base}companies/statements/verbose"
        }
        self.defaults = {
            "statements": "pl,derived",
            "period": "q1,q2,q3,q4,fy",
            "fyear": ",".join(list(map(str, last_years(n_years=5, include_current=True))))
        }
        self.data = {}
        self.threads = []
    
    def _queue_one_request(self, data_key: str, endpoint: str, params: Dict[str, Any]):
        """Add one SimFin request to the outgoing queue"""
        rq = (data_key, endpoint, params)
        if hasattr(self, "request_queue") and isinstance(self.request_queue, list):
            self.request_queue.append(rq)
        else:
            self.request_queue = [rq]
    
    def _dispatch_one_request(self):
        """Dispatch the first request to SimFin in the request queue"""
        if hasattr(self, "request_queue") and self.request_queue:
            data_key, endpoint, params = self.request_queue.pop(0)
            self.data[data_key] = self._get_request(endpoint, params)
            return self.data[data_key]
        
    def _dispatch_all_requests(self):
        """
        Launches each request in a separate thread, spaced 0.5 seconds apart.
        """
        for rq in self.request_queue:
            thread = threading.Thread(target=self._get_request, args=(rq[1], rq[2], rq[0]))
            thread.start()
            self.threads.append(thread)
            time.sleep(0.5)  # throttle: one request every 0.5 sec

        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
    
    def _get_request(self, endpoint: str, params: Dict[str, Any], data_key: str | None = None):
        """Generic SimFin Web API GET Request"""
        headers = {"Authorization": self.api_key}

        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()

        if data_key:
            self.data[data_key] = response.json()

        return response.json()
    
    def get_data(self, ticker: str | None = None):
        """Request all data for a ticker"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set
        
        self.get_metadata()  # queues a request
        self.get_statements()  # queues a request
        self._dispatch_all_requests()  # unqueues all requests
        self.parse_metadata()  # parses result
        self.parse_statements()  # parses result
    
    def get_metadata(self, ticker: str | None = None):
        """Request metadata for an asset"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set
        params = {"ticker": self.data["ticker"]}

        # async request
        self._queue_one_request("raw_metadata", self.urls["metadata"], params)

        # synchronous request and return
        # self.data["raw_metadata"] = self._get_request(self.urls["metadata"], params=params)
        # return self.data["raw_metadata"]
    
    def get_statements(self, ticker: str | None = None, statements: list[str] = [], period: list[str] = [], fyear: list[str] = []):
        """Request statements for an asset"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set

        params = {
            "ticker": self.data["ticker"],
            "statements": ",".join(statements) or self.defaults["statements"],
            "period": ",".join(period) or self.defaults["period"],
            "fyear": ",".join(fyear) or self.defaults["fyear"]
        }

        # async request
        self._queue_one_request("raw_statements", self.urls["statements"], params)

        # synchronous request and return
        # self.data["raw_statements"] = self._get_request(self.urls["statements"], params=params)
        # return self.data["raw_statements"]
    
    def parse_metadata(self, ticker: str | None = None):
        """Parse the raw metadata to fit as a stockjockey asset record"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set

        if not self.data.get("raw_metadata"):
            self.get_metadata()
        
        self.data["metadata"] = {
            "name": self.data["raw_metadata"][0]["name"],
            "ticker": self.data["raw_metadata"][0]["ticker"],
            "exchange": None,
            "market": self.data["raw_metadata"][0]["market"],
            "industry": self.data["raw_metadata"][0]["industryName"],
            "sector": self.data["raw_metadata"][0]["sectorName"],
            "fye_month": self.data["raw_metadata"][0]["endFy"],
            "description": self.data["raw_metadata"][0]["companyDescription"]
        }
        return self.data["metadata"]
    
    def parse_statements(self, ticker: str | None = None):
        """Parse the raw statements to fit as a stockjockey asset metric records"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set

        if not self.data.get("raw_statements"):
            self.get_statements()
        
        # sort statement objects
        self.data["statements"] = []
        for a in self.data["raw_statements"]:
            for b in a["statements"]:
                if b["statement"] == "PL":
                    for c in b["data"]:
                        self.data["statements"].extend(self.parse_profit_loss_statement(c))
                elif b["statement"] == "DERIVED":
                    for c in b["data"]:
                        self.data["statements"].extend(self.parse_derived_statement(c))

        return self.data["statements"]
    
    def parse_profit_loss_statement(self, statement: Dict[str, Any]):
        """Parse a raw profit and loss statement from Simfin to a list of asset metric records"""
        # determine time periods for records
        if statement["Fiscal Period"][0].lower() == "q":
            fp = statement["Fiscal Period"][1]
        else:
            fp = "fy"
        fy = int(statement["Fiscal Year"])

        # set metrics that can be extracted from the report
        metrics = {
            "revenue": "Revenue",
        }

        # crawl the report and create metric records
        records = []
        for k,v in metrics.items():
            record = {
                "metric": k,
                "year": fy,
                "quarter": str(fp),
                "value": statement[v]
            }
            records.append(record)
        return records
    
    def parse_derived_statement(self, statement: Dict[str, Any]):
        """Parse a raw derived statement from Simfin to a list of asset metric records"""
        # determine time periods for records
        if statement["Fiscal Period"][0].lower() == "q":
            fp = statement["Fiscal Period"][1]
        else:
            fp = "fy"
        fy = int(statement["Fiscal Year"])

        # set metrics that can be extracted from the report
        metrics = {
            "return_on_equity": "Return on Equity",
            "earnings_per_share": "Earnings Per Share, Basic"
        }

        # crawl the report and create metric records
        records = []
        for k,v in metrics.items():
            record = {
                "metric": k,
                "year": fy,
                "quarter": str(fp),
                "value": statement[v]
            }
            records.append(record)
        return records

# # Create endpoint building block snippets
# base = 'https://simfin.com/api/v2/'
# key = f'?api-key={os.environ["SIMFIN_KEY"]}'


# def get_all_assets():
#     """Request a list of all existing SimFin IDs and ticker combinations"""
#     endpoint = base + 'companies/list?' + key
#     response = requests.get(endpoint)
#     return [tuple(x) for x in response.json()['data']]


# def get_asset_meta(ticker, *args, **kwargs):
#     """Request general information on a specific ticker"""
#     endpoint = base + 'companies/general?' + f'ticker={ticker.upper()}&' + key
#     response = requests.get(endpoint).json()[0]
#     meta = {
#         'id': response['data'][response['columns'].index('SimFinId')],
#         'ticker': response['data'][response['columns'].index('Ticker')],
#         'name': response['data'][response['columns'].index('Company Name')],
#         'exchange': response['data'][response['columns'].index('Ticker')],
#         'sector': response['data'][response['columns'].index('IndustryId')],
#         'description': response['data'][response['columns'].index('Business Summary')],
#         'last_fiscal_year_month': response['data'][response['columns'].index('Month FY End')]
#     }
#     return meta


# def get_asset_statement(ticker, year, quarter=None, statement='pl', *args, **kwargs):
#     """Request financial statement
#     PARAMS
#     ------
#     ticker (str): unique ticker of a publicly traded stock
#     year (int): requested fiscal year
#     quarter (int): requested fiscal quarter
#     statement (str): type of statement to return pl=profit+loss, bs=balance sheet, cf=cash flow, derived=derived figures and ratios
#     """
#     period = f'q{quarter}' if quarter else 'fy'  # if no quarter requested get full year
#     endpoint = base + 'companies/statements?' + f'ticker={ticker.upper()}&' + f'statement={statement}&' + f'period={period}&' + f'fyear={year}&' + key
#     response = requests.get(endpoint).json()[0]
#     return {x: y for x, y in zip(response['columns'], response['data'][0])}  # assume only one report returned (free simfin)
