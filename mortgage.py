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
    paymentNoTax_total = paymentNoTax_monthly * n

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
    sumOfAllPayments_monthly = np.array([sum(totalPayments_monthly[:i]) for i in range(len(totalPayments_monthly))])
    sumOfAllPayments_monthly += p*c + d     # include closing cost and down payment in total 
    mortgageRateOfReturn_monthly = (houseEquity_monthly - sumOfAllPayments_monthly) / sumOfAllPayments_monthly
    
    # For time period after mortgage ends
    if analysisTimePeriodYears > N:
        taxPayments_annual = np.concatenate((taxPayments_annual, [t*max((p-hd), 0)*(1 + aH)**year \
                                                                  for year in range(N, analysisTimePeriodYears)]))
        taxPayments_monthly = np.concatenate((taxPayments_monthly, [taxPayments_annual[year]/12 \
                                    for year in range(N, analysisTimePeriodYears) for _ in range(12)]))
        
        for month in range(n, analysisTimePeriodYears*12):
            loanRemaining_monthly = np.append(loanRemaining_monthly, 0)
            interestPayments_monthly = np.append(interestPayments_monthly, 0)
            principalPayments_monthly = np.append(principalPayments_monthly, 0)

        houseValue_monthly = np.concatenate((houseValue_monthly, [p*(1 + ah/12)**month \
                                                                  for month in range(n, analysisTimePeriodYears*12)]))
        houseEquity_monthly = houseValue_monthly - loanRemaining_monthly[:-1]

        totalPayments_monthly = np.concatenate((totalPayments_monthly, taxPayments_monthly[n:]))
        sumOfAllPayments_monthly = np.array([sum(totalPayments_monthly[:i]) for i in range(len(totalPayments_monthly))])
        sumOfAllPayments_monthly += p*c + d     # include closing cost and down payment in total 
        mortgageRateOfReturn_monthly = (houseEquity_monthly - sumOfAllPayments_monthly) / sumOfAllPayments_monthly

        if showPlot:
            plt.plot(range(len(mortgageRateOfReturn_monthly)), mortgageRateOfReturn_monthly*100)
            plt.xlabel('Months')
            plt.xticks([48*year for year in range(int(analysisTimePeriodYears/4))])
            plt.ylabel('Return on Investment (%)')
            plt.grid()
            plt.show()

    return_df = pd.DataFrame()
    return_df.index.name = 'month'
    return_df['rate_of_return'] = mortgageRateOfReturn_monthly
    return_df['loan_remaining'] = loanRemaining_monthly[:-1]
    return_df['home_value'] = houseValue_monthly
    return_df['home_equity'] = houseEquity_monthly
    return_df['tax_payment_this_month'] = taxPayments_monthly
    return_df['tax_payments_cumulative'] = [sum(taxPayments_monthly[:month]) for month in range(len(taxPayments_monthly))]
    return_df['mortgage_payment_this_month'] = np.concatenate(([paymentNoTax_monthly for _ in range(n)], \
                                                               [0 for _ in range(n, analysisTimePeriodYears*12)]))
    return_df['mortgage_payments_cumulative'] = [sum(return_df['mortgage_payment_this_month'][:month]) \
                                                 for month in range(len(return_df['mortgage_payment_this_month']))]
    # TODO: finish building return_df

    return return_df

mortgageReturnAnalysis(400000, 0.04, 40000, 0.03, 15, 0.02, 0.05, showPlot=True)



# def compoundInterest(time_years:float, interestRate_annual:float, monthlyContributions:float|list[float]|np.array, 
#                      principal:float=None, compoundingFrequency:float|str=None):
#     if contributionFrequency is None:
#         contributionFrequency = 'monthly'
#     if principal is None:
#         principal = 0
#     if compoundingFrequency is None:
#         compoundingFrequency = 'monthly'

#     compoundingMap = {'daily': 365, 'monthly': 12, 'quarterly': 4, 'semi-annually': 2, 'annually': 1}
#     if isinstance(compoundingFrequency, str):
#         try:
#             numContributions_annual = compoundingMap[contributionFrequency]
#         except:
#             raise ValueError("`compoundingFrequency` must either be a float or one of the following strings: \
#                              'daily', 'monthly', 'quarterly', 'semi-annually', or 'annually'.")
#     if not (isinstance(monthlyContributions, list) or isinstance(monthlyContributions, np.array)):
#         monthlyContributions = np.array([monthlyContributions for _ in range(12*time_years)])
#     if len(monthlyContributions) != 12*time_years:
#         raise ValueError("`monthlyContributions` must either be a float or an array of \
#                          length 12*`time_years`.")
    
#     balance = principal

#     if compoundingFrequency == 365:
#         pass
#     else:
#         for i in range(compoundingFrequency*time_years):
#             pass

