first_month = '2023-10'
last_month = '2024-01'


def fill_missing_months():
    min_year,min_month = [int(x) for x in first_month.split('-')]
    all_months = [first_month]
    current_month = min_month
    current_year = min_year

    while all_months[-1] != last_month:
        current_month += 1
        if current_month > 12:
            current_year += 1
            current_month = 1
        
        current_month_string = f'{current_year}-{str(current_month).zfill(2)}'

        print(f'current {current_month_string}')
        all_months.append(current_month_string)

fill_missing_months()
    
    