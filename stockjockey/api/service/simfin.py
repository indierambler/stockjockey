# Import dependencies
import os
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
        self.data = {}
    
    def _get_request(self, endpoint: str, params: Dict[str, Any]):
        """Generic SimFin Web API GET Request"""
        headers = {"Authorization": self.api_key}

        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_metadata(self, ticker: str | None = None):
        """Request metadata for an asset"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set
        params = {"ticker": self.data["ticker"]}
        self.data["raw_metadata"] = self._get_request(self.urls["metadata"], params=params)
        return self.data["raw_metadata"]
    
    def get_statements(self, ticker: str | None = None, statements: list[str] = [], period: list[str] = [], fyear: list[str] = []):
        """Request statements for an asset"""
        if ticker:
            self.data["ticker"] = ticker
        # TODO: error if self.data["ticker"] is still not set
        
        if self.data.get("metadata") and self.data["metadata"].get("fye_month"):
            fye_month = self.data["metadata"]["fye_month"]
        else:
            self.parse_metadata(ticker)
            fye_month = self.data["metadata"]["fye_month"]

        params = {
            "ticker": self.data["ticker"],
            "statements": ",".join(statements) or "pl,derived",
            "period": ",".join(period) or last_quarters(fye_month=fye_month),
            "fyear": ",".join(fyear) or last_years(fye_month=fye_month)
        }
        self.data["raw_statements"] = self._get_request(self.urls["statements"], params=params)
        return self.data["raw_statements"]
    
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
        
        self.data["statements"] = {
            "asldkjf": ""
        }
        return self.data["statements"]

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
