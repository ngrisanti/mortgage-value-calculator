import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def mortgageReturnAnalysis(housePrice:float, interestRateAnnual:float, downPayment:float, 
                  closingCostPercent:float, mortgageTermYears:float, propertyTaxRate:float, 
                  houseAppreciationRate:float, homesteadDeduction:float = None, 
                  analysisTimePeriodYears:float = None, showPlot:bool = None) -> pd.DataFrame:

    if homesteadDeduction is None:
        homesteadDeduction = 100000
    if analysisTimePeriodYears is None:
        analysisTimePeriodYears = 40
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
    interestPayments_monthly = np.array([])

    for month in range(n):
        monthlyInterest = loanRemaining_monthly[month]*i
        interestPayments_monthly = np.append(interestPayments_monthly, monthlyInterest)
        loanRemaining_monthly = np.append(loanRemaining_monthly, \
                                          [loanRemaining_monthly[month]\
                                           -paymentNoTax_monthly+monthlyInterest])
    interestPayments_monthly = np.append(interestPayments_monthly, 0)
    principalPayments_monthly = np.array([paymentNoTax_monthly \
                                          - interestPayments_monthly[month] for month in range(n)])
    
    taxPayments_annual = np.array([t*max((p-hd), 0)*(1 + aH)**year for year in range(N)])
    taxPayments_monthly = np.array([taxPayments_annual[year]/12 \
                                    for year in range(N) for _ in range(12)])

    houseValue_monthly = [p*(1 + ah/12)**month for month in range(n)]
    houseEquity_monthly = houseValue_monthly - loanRemaining_monthly[:-1]

    totalPayments_monthly = paymentNoTax_monthly + taxPayments_monthly
    sumOfAllPayments_monthly = np.array([sum(totalPayments_monthly[:i]) \
                                         for i in range(len(totalPayments_monthly))])
    sumOfAllPayments_monthly += p*c + d     # include closing cost and down payment in total 
    mortgageRateOfReturn_monthly = (houseEquity_monthly - sumOfAllPayments_monthly) \
                                    / sumOfAllPayments_monthly
    
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

        houseValue_monthly = np.concatenate((houseValue_monthly, [p*(1 + ah/12)**month for month in \
                                                                  range(n, analysisTimePeriodYears*12)]))
        houseEquity_monthly = houseValue_monthly - loanRemaining_monthly[:-1]

        totalPayments_monthly = np.concatenate((totalPayments_monthly, taxPayments_monthly[n:]))
        sumOfAllPayments_monthly = np.array([sum(totalPayments_monthly[:i]) \
                                             for i in range(len(totalPayments_monthly))])
        sumOfAllPayments_monthly += p*c + d     # include closing cost and down payment in total 
        mortgageRateOfReturn_monthly = (houseEquity_monthly - sumOfAllPayments_monthly) \
                                        / sumOfAllPayments_monthly

    return_df = pd.DataFrame()
    return_df.index.name = 'month'
    return_df['rate_of_return'] = mortgageRateOfReturn_monthly
    return_df['loan_remaining'] = loanRemaining_monthly[:-1]
    return_df['home_value'] = houseValue_monthly
    return_df['home_equity'] = houseEquity_monthly
    return_df['all_payments_this_month'] = totalPayments_monthly
    return_df['all_payments_previous'] = [sum(return_df['all_payments_this_month'][:month]) \
                                                 for month in range(len(return_df['all_payments_this_month']))]
    return_df['tax_payment_this_month'] = taxPayments_monthly
    return_df['tax_payments_previous'] = [sum(taxPayments_monthly[:month]) for month in range(len(taxPayments_monthly))]
    return_df['mortgage_payment_this_month'] = np.concatenate(([paymentNoTax_monthly for _ in range(n)], \
                                                               [0 for _ in range(n, analysisTimePeriodYears*12)]))
    return_df['mortgage_payments_previous'] = [sum(return_df['mortgage_payment_this_month'][:month]) \
                                                 for month in range(len(return_df['mortgage_payment_this_month']))]
    return_df['interest_payment_this_month'] = interestPayments_monthly[:-1]
    return_df['interest_payments_previous'] = [sum(return_df['interest_payment_this_month'][:month]) \
                                                 for month in range(len(return_df['interest_payment_this_month']))]
    return_df['principal_payment_this_month'] = principalPayments_monthly
    return_df['principal_payments_previous'] = [sum(return_df['principal_payment_this_month'][:month]) \
                                                 for month in range(len(return_df['principal_payment_this_month']))]
    
    # Replace {}_previous columns with {}_cumulative columns (to include current month)
    for col in return_df.columns:
        col_basis = col[:-9]
        if col[-9:] == '_previous':
            if col_basis == 'all_payments':
                return_df[f'{col_basis}_cumulative'] = return_df[f'{col_basis}_this_month'] \
                    + return_df[f'{col_basis}_previous']
                return_df = return_df.drop(f'{col_basis}_previous', axis=1)
            else:
                col_basis = col_basis[:-1]
                return_df[f'{col_basis}s_cumulative'] = return_df[f'{col_basis}_this_month'] \
                    + return_df[f'{col_basis}s_previous']
                return_df = return_df.drop(f'{col_basis}s_previous', axis=1)

    return_df.index += 1

    if showPlot:
            xVals = list(range(len(mortgageRateOfReturn_monthly)))
            xVals = [1 + x for x in xVals]
            plt.plot(xVals, mortgageRateOfReturn_monthly*100)
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
        monthlyContribution = np.array([0 for _ in range(analysisTimePeriodYears*12)])
    elif isinstance(monthlyContribution, float|int):
        monthlyContribution = np.array([monthlyContribution for _ in range(analysisTimePeriodYears*12)])
    elif len(monthlyContribution) == analysisTimePeriodYears*12 - 1:
        monthlyContribution = [0] + monthlyContribution
    if not (len(monthlyContribution) == analysisTimePeriodYears*12):
        raise ValueError("`monthlyContribution` must be of either a float or \
                         a list of floats with length `analysisTimePeriodYears`*12")

    monthlyYield = ((1+apy)**(1/12)-1)*12
    print(monthlyYield)

    total = principal
    for month in range(analysisTimePeriodYears*12):
        total += monthlyContribution[month]
        total *= 1 + (monthlyYield/12)

    return total

