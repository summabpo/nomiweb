import datetime

def last_business_day_of_march(year):
    # Last day of March
    last_day_of_march = datetime.date(int(year), 3, 31)
    
    # Day of the week (Monday=0, Sunday=6)
    day_of_week = last_day_of_march.weekday()
    
    # If the last day of March is Saturday (5) or Sunday (6)
    if day_of_week == 5:  # Saturday
        last_business_day = last_day_of_march - datetime.timedelta(days=1)
    elif day_of_week == 6:  # Sunday
        last_business_day = last_day_of_march - datetime.timedelta(days=2)
    else:
        last_business_day = last_day_of_march
    
    return last_business_day.year, last_business_day.month, last_business_day.day





def diangenerate():
    
    contexto = {
        'data':'data'
        
    }
    
    return contexto 