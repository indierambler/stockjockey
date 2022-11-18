# Import dependencies
import os


# Create endpoint building block snippets
base = 'https://simfin.com/api/v2/'
key = f'?api-key={os.environ["SIMFIN_KEY"]}'


def get_all_assets():
    """Request a list of all existing SimFin IDs and ticker combinations"""
    endpoint = base+'companies/list?'+key
    response = requests.get(endpoint)
    return [tuple(x) for x in response.json()['data']]


def get_asset_meta(ticker, *args, **kwargs):
    """Request general information on a specific ticker"""
    endpoint = base+'companies/general?'+f'ticker={ticker.upper()}&'+key
    response = requests.get(endpoint).json()[0]
    meta = {
        'id': response['data'][response['columns'].index('SimFinId')],
        'ticker': response['data'][response['columns'].index('Ticker')],
        'name': response['data'][response['columns'].index('Company Name')],
        'exchange': response['data'][response['columns'].index('Ticker')],
        'sector': response['data'][response['columns'].index('IndustryId')],
        'description': response['data'][response['columns'].index('Business Summary')],
        'last_fiscal_year_month': response['data'][response['columns'].index('Month FY End')]
    }
    return meta


def get_asset_statement(ticker, year, quarter=None, statement='pl', *args, **kwargs):
    """Request financial statement
    PARAMS
    ------
    ticker (str): unique ticker of a publicly traded stock
    year (int): requested fiscal year
    quarter (int): requested fiscal quarter
    statement (str): type of statement to return pl=profit+loss, bs=balance sheet, cf=cash flow, derived=derived figures and ratios
    """
    period = f'q{quarter}' if quarter else 'fy'  # if no quarter requested get full year
    endpoint = base+'companies/statements?'+f'ticker={ticker.upper()}&'+f'statement={statement}&'+f'period={period}&'+f'fyear={year}&'+key
    response = requests.get(endpoint).json()[0]
    return {x: y for x,y in zip(response['columns'], response['data'][0])}  # assume only one report returned (free simfin)