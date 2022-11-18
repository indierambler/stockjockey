"""High level functions to be called from the flask app"""

# Import dependencies
from . import period, simfin


def get_statements(ticker, n_periods=4):
    """Request all the relevant financial statements for a specific ticker"""
    # request meta info and extract the last month of the fiscal year
    fye_month = simfin.get_asset_meta(ticker)['last_fiscal_year_month']

    # get the relevant previous years
    prev_periods = period.last_years(n_years=n_periods-1, include_current=False, fye_month=fye_month)
    previous = [simfin.get_asset_statement(ticker, year=x) for x in prev_periods]

    # get the relevant current and matching last year quarter
    curr_q = period.current_quarter(fye_month=fye_month, completed=True)
    curr_periods = (curr_q, (curr_q[0], curr_q[1] - 1))
    current = [simfin.get_asset_statement(ticker, year=x[1], quarter=x[0]) for x in curr_periods]

    # organize the statements as needed
    statements = {
        'current': current,
        'previous': previous
    }
    return statements


def analyze_revenue(statements):
    """Decide if and how revenue numbers pass test criteria"""
    revs = [statements['current'][0]['Revenue'], statements['current'][1]['Revenue']]
    periods = [statements['current'][0]['Fiscal Period'], statements['current'][1]['Fiscal Period']]
    yrs = [statements['current'][0]['Fiscal Year'], statements['current'][1]['Fiscal Year']]
    score = 0
    if revs[0] > revs[1]:
        score += 1

    last = None
    for s in statements['previous']:
        revs.append(s['Revenue'])
        periods.append(s['Fiscal Period'])
        yrs.append(s['Fiscal Year'])
        if last and last > revs[-1]:
            score += 1
        last = revs[-1]

    max_score = len(revs) - 2
    #if score == max_score:
    #    return True, revs
    #else:
    #    return False, revs
    return score/max_score, tuple((x, y, z) for x, y, z in zip(yrs, periods, revs))
    