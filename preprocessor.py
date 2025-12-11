import re
import pandas as pd

def preprocess(data):
    # WhatsApp message pattern (date, time - )
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:AM|PM|am|pm|a.m.|p.m.)?\s?-\s'

    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Normalize spaces and AM/PM
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ', regex=False)  # Replace narrow space
    df['message_date'] = df['message_date'].str.upper()  # Convert am/pm to AM/PM

    # Try parsing with 2-digit year and 12-hour AM/PM
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ', errors='coerce')

    # If some dates are NaT (e.g., 4-digit year), try alternative format
    mask = df['message_date'].isna()
    if mask.any():
        df.loc[mask, 'message_date'] = pd.to_datetime(
            df.loc[mask, 'message_date'].str.replace('\u202f', ' ', regex=False),
            format='%d/%m/%Y, %I:%M %p - ', errors='coerce'
        )

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract date/time components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create period column in AM/PM format
    period = []
    for hour in df['hour']:
        if hour == 0:
            period.append('12 AM - 1 AM')
        elif 1 <= hour < 12:
            period.append(f'{hour} AM - {hour+1} AM')
        elif hour == 12:
            period.append('12 PM - 1 PM')
        else:  # 13-23 hours
            period.append(f'{hour-12} PM - {hour-11} PM')

    df['period'] = period

    return df
