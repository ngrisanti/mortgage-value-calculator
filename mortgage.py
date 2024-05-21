import numpy as np

def mortgageValue(housePrice:float, interestRateAnnual:float, downPayment:float, 
                  closingCostPercent:float, mortgageTermYears:float, propertyTaxRate:float, 
                  rentCostMonthly:float, houseAppreciationRate:float, marketReturnRate:float) -> float:
    p = housePrice
    I, i = interestRateAnnual, interestRateAnnual/12
    d = downPayment
    c = closingCostPercent
    N, n = mortgageTermYears, mortgageTermYears*12
    t = propertyTaxRate
    R, r = rentCostMonthly*12, rentCostMonthly
    ah = houseAppreciationRate
    ar = marketReturnRate
    l = p - d   # loan amount

    paymentNoTax_monthly = l*(i*(1+i)**n)/((1+i)**n-1)
    paymentNoTax_total = paymentNoTax_monthly * n
    interestPaid_total = paymentNoTax_total - l
    
    taxPayments_annual = np.array([t*p*ah**x for x in range(N)])
    taxPayments_total = taxPayments_annual.sum()
    taxPayments_monthly = np.array([taxPayments_annual[year]/12 \
                                    for _ in range(12) for year in range(N)])
    paymentsWithTax_monthly = taxPayments_monthly + paymentNoTax_monthly

    opportunityCost_monthly = paymentsWithTax_monthly - r

def compoundInterest(time_years:float, interestRate_annual:float, monthlyContributions:float|list[float]|np.array, 
                     principal:float=None, compoundingFrequency:float|str=None):
    if contributionFrequency is None:
        contributionFrequency = 'monthly'
    if principal is None:
        principal = 0
    if compoundingFrequency is None:
        compoundingFrequency = 'monthly'

    compoundingMap = {'daily': 365, 'monthly': 12, 'quarterly': 4, 'semi-annually': 2, 'annually': 1}
    if isinstance(compoundingFrequency, str):
        try:
            numContributions_annual = compoundingMap[contributionFrequency]
        except:
            raise ValueError("`compoundingFrequency` must either be a float or one of the following strings: \
                             'daily', 'monthly', 'quarterly', 'semi-annually', or 'annually'.")
    if not (isinstance(monthlyContributions, list) or isinstance(monthlyContributions, np.array)):
        monthlyContributions = np.array([monthlyContributions for _ in range(12*time_years)])
    if len(monthlyContributions) != 12*time_years:
        raise ValueError("`monthlyContributions` must either be a float or an array of \
                         length 12*`time_years`.")
    
    balance = principal

    if compoundingFrequency == 365:
        pass
    else:
        for i in range(compoundingFrequency*time_years):
            pass
