import pandas as pd
import plotly.express as px
import os

# ---- SETTINGS -------
make_plot = True  # Overwrites other actions

export_message = True
specific_date = '2023-12-31'
print_messages_per_day = False

by_week = False

find_text = False
text_to_find = ''

# -------------------------

folder_path = "E:\\Tools\\Messages"


def main():
    combined_data = get_file()

    combined_data['Date'] = pd.to_datetime(combined_data['Date'], format='mixed', utc=True)

    daily_message_count, weekly_message_count = get_daily_message_count(combined_data)

    # Filter the DataFrame based on the desired date
    desired_date = pd.to_datetime(specific_date).date()
    filtered_df = combined_data[combined_data['Date'].dt.date == desired_date]

    if find_text:
        filtered_df = combined_data[combined_data['Content'].str.contains(text_to_find, case=False, na=False)]

    # Export the filtered DataFrame to a CSV file
    if export_message:
        if find_text:
            filtered_df.to_csv(f'export(text).csv', index=False)
            print('worked')
        else:
            filtered_df.to_csv(f'filtered_data_({desired_date}).csv', index=False)

    # Print the messages
    if by_week:
        for week, count in weekly_message_count.items():
            print(f'on {week}, {count} messages were sent')
    else:
        for date, count in daily_message_count.items():
            print(f'on {date}, {count} messages were sent')

    # Plot the number of messages sent each day
    if by_week:
        plot_messages(weekly_message_count)
    else:
        plot_messages(daily_message_count)


def plot_messages(message_count_by_time):
    if make_plot:
        fig = px.bar(message_count_by_time, x='Date', y='MessageCount', title='Number of Messages Sent Each Day')
        fig.show()


def get_daily_message_count(combined_data):
    daily_message_count = combined_data.groupby(combined_data['Date'].dt.date)['Content'].size()
    weekly_message_count = ''
    if by_week:
        weekly_message_count = combined_data.groupby(combined_data['Date'].dt.to_period("W"))['Content'].size()
    if make_plot:
        daily_message_count = daily_message_count.reset_index(name='MessageCount')
        if by_week:
            weekly_message_count = weekly_message_count.reset_index(name='MessageCount')
    return daily_message_count, weekly_message_count


def get_file():
    combined_data = pd.DataFrame()
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                csv_file_path = os.path.join(root, file)
                df = pd.read_csv(csv_file_path)
                combined_data = pd.concat([combined_data, df])

    return combined_data


main()