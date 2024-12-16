from datetime import datetime, timedelta

def list_weekdays_between(start_date, end_date, target_weekday):
    # Convert input strings to datetime objects with British date format
    start_date = datetime.strptime(start_date, '%d-%m-%Y')
    end_date = datetime.strptime(end_date, '%d-%m-%Y')

    # Map target weekday to its numerical representation (0 = Monday, ..., 6 = Sunday)
    weekdays = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
    target_weekday = weekdays.get(target_weekday.lower())

    if target_weekday is None:
        print("Invalid weekday. Please enter a valid weekday in natural language.")
        return

    # Initialize the current date as the start date
    current_date = start_date

    # Define a timedelta of one day
    one_day = timedelta(days=1)

    # Loop through the dates and print the specified weekdays
    while current_date <= end_date:
        if current_date.weekday() == target_weekday:
            print(current_date.strftime('%d %B %Y'))
        
        # Move to the next day
        current_date += one_day

# Example usage
start_date_input = input("Enter start date (DD-MM-YYYY): ")
end_date_input = input("Enter end date (DD-MM-YYYY): ")
weekday_input = input("Enter target weekday in natural language: ")

list_weekdays_between(start_date_input, end_date_input, weekday_input)