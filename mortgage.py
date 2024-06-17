import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from math import floor


def mortgageReturnAnalysis(housePrice:float, interestRateAnnual:float, downPayment:float, 
                  closingCostPercent:float, mortgageTermYears:float, propertyTaxRate:float, 
                  houseAppreciationRate:float = None, homesteadDeduction:float = None, 
                  analysisTimePeriodYears:float = None, showPlot:bool = None) -> pd.DataFrame:
    
    if homesteadDeduction is None:
        homesteadDeduction = 100000
    if analysisTimePeriodYears is None:
        analysisTimePeriodYears = 40
    if houseAppreciationRate is None:
        houseAppreciationRate = 0.034
    if showPlot is None:
        showPlot = False
    
    p = housePrice
    I, i = interestRateAnnual, interestRateAnnual/12
    d = downPayment
    c = closingCostPercent
    N, n = mortgageTermYears, mortgageTermYears*12
    t = propertyTaxRate
    aH, ah = houseAppreciationRate, 12*((1 + houseAppreciationRate)**(1/12) - 1)
    hd = homesteadDeduction
    l = p - d   # loan amount

    c = 0 if l <= 0 else c

    paymentNoTax_monthly = l*(i*(1+i)**n)/((1+i)**n-1)

    loanRemaining_monthly = np.array([l])
    interestPayments_monthly = np.array([0])

    for month in range(n):
        monthlyInterest = loanRemaining_monthly[month]*i
        interestPayments_monthly = np.append(interestPayments_monthly, monthlyInterest)
        loanRemaining_monthly = np.append(loanRemaining_monthly, \
                                          [loanRemaining_monthly[month]\
                                           -paymentNoTax_monthly+monthlyInterest])

    principalPayments_monthly = np.array([0] + [paymentNoTax_monthly \
                                          - interestPayments_monthly[month] for month in range(n)])

    taxPayments_annual = np.array([t*max((p-hd), 0)*(1 + aH)**year for year in range(N)])
    taxPayments_monthly = np.array([0] + [taxPayments_annual[year]/12 \
                                    for year in range(N) for _ in range(12)])

    houseValue_monthly = [p*(1 + ah/12)**month for month in range(n + 1)]
    houseEquity_monthly = houseValue_monthly - loanRemaining_monthly

    totalPayments_monthly = paymentNoTax_monthly + taxPayments_monthly
    totalPayments_monthly[0] += p*c + d  # include closing cost and down payment in first month's payment
    
    # For time period after mortgage ends
    if analysisTimePeriodYears > N:
        taxPayments_annual = np.concatenate((taxPayments_annual, \
                                             [t*max((p-hd), 0)*(1 + aH)**year \
                                             for year in range(N, analysisTimePeriodYears)]))
        taxPayments_monthly = np.concatenate((taxPayments_monthly, [taxPayments_annual[year]/12 \
                                    for year in range(N, analysisTimePeriodYears) for _ in range(12)]))
        
        for month in range(n, analysisTimePeriodYears*12):
            loanRemaining_monthly = np.append(loanRemaining_monthly, 0)
            interestPayments_monthly = np.append(interestPayments_monthly, 0)
            principalPayments_monthly = np.append(principalPayments_monthly, 0)

        houseValue_monthly = np.concatenate((houseValue_monthly, [p*(1 + ah/12)**(month+1) for month in \
                                                                  range(n, analysisTimePeriodYears*12)]))
        houseEquity_monthly = houseValue_monthly - loanRemaining_monthly

        totalPayments_monthly = np.concatenate((totalPayments_monthly, taxPayments_monthly[(n+1):]))

    return_df = pd.DataFrame()
    return_df.index.name = 'month'
    return_df['loan_remaining'] = loanRemaining_monthly
    return_df['home_value'] = houseValue_monthly
    return_df['home_equity'] = houseEquity_monthly
    return_df['all_payments_this_month'] = totalPayments_monthly
    return_df['all_payments_cumulative'] = [sum(return_df['all_payments_this_month'][:month+1]) \
                                                 for month in range(len(return_df['all_payments_this_month']))]
    return_df['tax_payment_this_month'] = taxPayments_monthly
    return_df['tax_payments_cumulative'] = [sum(taxPayments_monthly[:month+1]) for month in range(len(taxPayments_monthly))]
    return_df['mortgage_payment_this_month'] = np.concatenate(([0] + [paymentNoTax_monthly for _ in range(n)], \
                                                               [0 for _ in range(n, analysisTimePeriodYears*12)]))
    return_df['mortgage_payments_cumulative'] = [sum(return_df['mortgage_payment_this_month'][:month+1]) \
                                                 for month in range(len(return_df['mortgage_payment_this_month']))]
    return_df['interest_payment_this_month'] = interestPayments_monthly
    return_df['interest_payments_cumulative'] = [sum(return_df['interest_payment_this_month'][:month+1]) \
                                                 for month in range(len(return_df['interest_payment_this_month']))]
    return_df['principal_payment_this_month'] = principalPayments_monthly
    return_df['principal_payments_cumulative'] = [sum(return_df['principal_payment_this_month'][:month+1]) \
                                                 for month in range(len(return_df['principal_payment_this_month']))]

    return_df['return_on_investment'] = (return_df['home_equity'] - return_df['all_payments_cumulative']) \
                                    / return_df['all_payments_cumulative']

    if showPlot:
            xVals = list(range(len(return_df)))
            xVals = [x for x in xVals]
            plt.plot(xVals, 100*return_df['return_on_investment'])
            plt.axvline(x=n, color='red')
            plt.xlabel('Months')
            plt.xticks([48*year for year in range(int(analysisTimePeriodYears/4)+1)])
            plt.ylabel('Return on Investment (%)')
            plt.grid()
            plt.show()

    return return_df


def compoundInterestCalculator(principal:float, apy:float, monthlyContribution:list[float]|float = None,
                               analysisTimePeriodYears:float = None) -> pd.DataFrame:
    """Note: this function assumes interest compounds monthly, so `apy` is greater than the \
        simple intererest rate"""

    if analysisTimePeriodYears is None:
        analysisTimePeriodYears = 40
    if monthlyContribution is None:
        monthlyContribution = 0
    if (isinstance(monthlyContribution, list) and len(monthlyContribution)==analysisTimePeriodYears*12+1):
        monthlyContribution[0] += principal
    if isinstance(monthlyContribution, float|int):
        monthlyContribution = np.array([principal] + [monthlyContribution for _ in range(analysisTimePeriodYears*12)])
    if len(monthlyContribution) == analysisTimePeriodYears*12:
        monthlyContribution = np.array([principal] + monthlyContribution)
    if not (len(monthlyContribution) == analysisTimePeriodYears*12 + 1):
        raise ValueError("`monthlyContribution` must be of either a float or a list of floats with length `analysisTimePeriodYears`*12")

    monthlyYield = ((1+apy)**(1/12)-1)*12
    totals_monthly = np.array([])

    total = 0
    for month in range(analysisTimePeriodYears*12 + 1):
        total += monthlyContribution[month]
        total *= 1 + (monthlyYield/12)
        totals_monthly = np.append(totals_monthly, total)

    return totals_monthly

def cumulativeOpportunityCost(mortgage_df:pd.DataFrame, rentPrice:float, rentInflationRate:float = None, \
                   marketReturnRate:float = None, showPlot:bool = None) -> pd.DataFrame:

    if rentInflationRate is None:
        rentInflationRate = 0.045
    if marketReturnRate is None:
        marketReturnRate = 0.1
    if showPlot is None:
        showPlot = False

    N, n = floor(len(mortgage_df)/12), len(mortgage_df)

    rentPrices_monthly = np.array([0] + [rentPrice * (1 + rentInflationRate)**years for years in range(N) for _ in range(12)])
    priceDifferential = mortgage_df['all_payments_this_month'] - rentPrices_monthly

    returns = compoundInterestCalculator(0, marketReturnRate, priceDifferential, N)

    if showPlot:
        xVals = list(range(n))
        plt.plot(xVals, returns)
        plt.xlabel('Months')
        plt.xticks([48*year for year in range(int(N/4)+1)])
        plt.ylabel('Portfolio Value ($)')
        plt.grid()
        plt.show()

    return_df = pd.DataFrame({'return_on_investment': returns })
    return_df.index.name = 'month'
    return return_df

def compareReturns(mortgage_df:pd.DataFrame, rent_df:pd.DataFrame, showPlot=False) -> pd.DataFrame:
    return_df = mortgage_df
    return_df.rename(columns={'return_on_investment': 'return_on_investment_mortgage'})
    return_df['rent_returns_raw'] = rent_df
    return_df['return_on_investment_rent'] = (return_df['rent_returns_raw'] - return_df['all_payments_cumulative']) / return_df['all_payments_cumulative']

    if showPlot:
        xVals = list(range(len(return_df)))
        plt.plot(xVals, 100*return_df['return_on_investment_mortgage'], color='blue')
        plt.plot(xVals, 100*return_df['return_on_investment_rent'], color='purple')
        plt.xlabel('Months')
        plt.xticks([48*year for year in range(len(return_df)/12+1)])
        plt.ylabel('Portfolio Value ($)')
        plt.grid()
        plt.show()

mortgage_df = mortgageReturnAnalysis(400000, 0.07, 20000, 0.03, 20, 0.02, 0.034, showPlot=True)
rent_df = cumulativeOpportunityCost(mortgage_df, 1600, showPlot=False)
returns = compareReturns(mortgage_df, rent_df)