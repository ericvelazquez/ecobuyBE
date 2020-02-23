def convertionToIS(amount, unit):
    amount=float(amount)
    conversion=None
    if unit=='ft':
        conversion=amount/3.281
    if unit=='pounds' or unit=='lbs':
        conversion=amount/2.205
    if unit=='inches' or unit=='in.' or unit=="\'\'" or unit==' in':
        conversion=amount/39.37
    if unit=='ounces':
        conversion=amount/35.274
    if unit=='miles':
        conversion=amount/1.609
    if conversion:
        conversion=round(conversion,2)
    return conversion