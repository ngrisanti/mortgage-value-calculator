import numpy as np
from matplotlib import pyplot as plt

def mortgageReturnRate(housePrice:float, interestRateAnnual:float, downPayment:float, 
                  closingCostPercent:float, mortgageTermYears:float, propertyTaxRate:float, 
                  rentCostMonthly:float, houseAppreciationRate:float, marketReturnRate:float,
                  housesteadDeduction:float=100000) -> float:
    p = housePrice
    I, i = interestRateAnnual, interestRateAnnual/12
    d = downPayment
    c = closingCostPercent
    N, n = mortgageTermYears, mortgageTermYears*12
    t = propertyTaxRate
    R, r = rentCostMonthly*12, rentCostMonthly
    aH, ah = 1 + houseAppreciationRate, 1 + 12*((1 + houseAppreciationRate)**(1/12) - 1)
    ar = 1 + marketReturnRate
    hd = housesteadDeduction
    l = p - d   # loan amount

    paymentNoTax_monthly = l*(i*(1+i)**n)/((1+i)**n-1)
    paymentNoTax_total = paymentNoTax_monthly * n
    interestPaid_total = paymentNoTax_total - l

    # print(f'Monthly payment (no tax): {paymentNoTax_monthly}')
    # print(f'Total payment (no tax): {paymentNoTax_total}')
    # print(f'Total interest paid: {interestPaid_total}')

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
    
    plot = False
    if plot:
        plt.plot(range(len(principalPayments_monthly)), principalPayments_monthly)
        plt.plot(range(len(interestPayments_monthly)), interestPayments_monthly)
        plt.show()
    
    taxPayments_annual = np.array([t*max((p-hd), 0)*aH**x for x in range(N)])
    taxPayments_total = taxPayments_annual.sum()
    taxPayments_monthly = np.array([taxPayments_annual[year]/12 \
                                    for year in range(N) for _ in range(12)])
    paymentsWithTax_monthly = taxPayments_monthly + paymentNoTax_monthly

    
    houseValue_monthly = [p*(1 + (ah - 1)/12)**month for month in range(n)]
    houseEquity_monthly = houseValue_monthly - loanRemaining_monthly[:-1]

    plot = False
    if plot:
        plt.plot(range(len(houseValue_monthly)), houseValue_monthly)
        plt.plot(range(len(houseEquity_monthly)), houseEquity_monthly)
        plt.show()

    totalPayments_monthly = np.array([ paymentNoTax_monthly*month + sum(taxPayments_monthly[:month+1]) for month in range(n) ])
    totalReturns_monthly = houseEquity_monthly - totalPayments_monthly
    totalRateOfReturn_monthly = totalReturns_monthly / totalPayments_monthly

    plot = True
    if plot:
        plt.plot(range(len(totalPayments_monthly)), totalPayments_monthly)
        plt.show()

    return totalRateOfReturn_monthly[-1]

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
