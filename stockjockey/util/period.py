# Import dependencies
import datetime
import numpy as np


def current_quarter(fye_month=12, completed=True):
    """Get current quarter number along with year relative to the fiscal year end month"""
    now = datetime.datetime.now()

    # get current quarter relative to fiscal year
    fiscal_q_diff = np.floor((fye_month - now.month) / 3)
    if fiscal_q_diff >= 0:  # current fisc year = current cal year
        q = int(4 - fiscal_q_diff)
        y = int(now.year)
    else:  # current fisc year = next cal year
        q = int(abs(fiscal_q_diff))
        y = int(now.year + 1)

    # convert to last quarter if required
    if completed:
        q -= 1
        if q < 1:
            q = 4
            y -= 1

    return (q, y)


def last_quarters(n_quarters=4, include_current=False, fye_month=12):
    """Get n previous quarter numbers along with years relative the fiscal year end month"""
    q, y = current_quarter(fye_month=fye_month, completed=not include_current)
    quarters = [q]
    years = [y]

    # get previous quarters
    while len(quarters) < n_quarters:
        if quarters[-1] <= 1:
            quarters.append(4)
            years.append(years[-1]-1)
        else:
            quarters.append(quarters[-1]-1)
            years.append(years[-1])
    return tuple(zip(quarters, years))


def last_years(n_years=4, include_current=False, fye_month=12):
    """Get n previous years taking into account the fiscal year end month"""
    now = datetime.datetime.now()
    years = [int(now.year)]  # get this year
    if now.month > fye_month:
        years[0] += 1  # fiscal year is next calendar year

    # convert to last year if required
    if not include_current:
        years[0] -= 1

    # get previous years
    while len(years) < n_years:
        years.append(years[-1]-1)
    return tuple(years)
    