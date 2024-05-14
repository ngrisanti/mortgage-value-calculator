def mortgageValue(housePrice:float, interestRateAnnual:float, downPayment:float, 
                  closingCostPercent:float, mortgageTermYears:int, propertyTaxRate:float, 
                  rentCostMonthly:float, houseAppreciationRate:float, marketReturnRate:float):
    p = housePrice
    I, i = interestRateAnnual, interestRateAnnual/12
    d = downPayment
    c = closingCostPercent
    N, n = mortgageTermYears, mortgageTermYears*12
    t = propertyTaxRate
    R, r = rentCostMonthly*12, rentCostMonthly
    ah = houseAppreciationRate
    ar = marketReturnRate
    l = p - d

    paymentNoTax_monthly = l*(i*(1+i)^n)/((1+i)^n-1)
    interestPaid_total = paymentNoTax_monthly*n - l
    
    taxPayments_annual = [t*p*ah^x for x in range(N)]
    taxPayments_monthly = []
    month_count = 0
    for _ in range(n):
        if month_count == 11:
            month_count = 0
