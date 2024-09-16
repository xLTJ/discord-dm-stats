import pandas as pd
import plotly.express as px
import os
import re

# ---- SETTINGS -------
make_plot = True  # Overwrites other actions

export_message = False
specific_date = '2023-12-31'
print_messages_per_day = False

by_week = False

find_text = False
text_to_find = ''

find_call_time = True  # only works with plot

# --------------------------

folder_path = "E:\\Tools\\Messages"


def main():
    combined_data = get_file()

    combined_data['Date'] = pd.to_datetime(combined_data['Date'], format='mixed', utc=True)

    if find_call_time:
        call_data = process_call_data(combined_data)
        call_duration_by_user_day = call_data.groupby([call_data['Date'].dt.date, 'user_name'])['call_duration'].sum()
        plot_call_data(call_duration_by_user_day)
    else:
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


# Filters the data to only include messages for calls.
def process_call_data(combined_data):
    call_data = combined_data[
        combined_data['Content'].str.contains('Started a call that lasted', case=False, na=False)].copy()
    call_data['call_duration'] = call_data['Content'].apply(extract_call_duration)
    return call_data


# Extracts the call duration from the message content. Also checks if the time is in minutes (which it should be lol).
def extract_call_duration(content):
    match = re.search(r'Started a call that lasted (\d+) minutes.', content)
    if match:
        return int(match.group(1))
    else:
        return 0


def plot_call_data(call_duration_data):
    if make_plot:
        call_duration_data = call_duration_data.reset_index(name='CallDuration')
        fig = px.bar(call_duration_data, color="user_name", x='Date', y='CallDuration',
                     title='Total Call Duration (minutes) By User',
                     color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.show()


def plot_messages(message_count_by_time):
    if make_plot:
        fig = px.bar(
            message_count_by_time,
            color="user_name",
            x='Date',
            y='MessageCount',
            title='Number of Messages Sent Each Day By User',
            color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.show()


def get_daily_message_count(combined_data):
    daily_message_count = combined_data.groupby([combined_data['Date'].dt.date, combined_data["user_name"]])[
        'Content'].size()
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
                # name format is "Direct Messages - <username> [<epoch_time>].csv
                # find these and grab everything  ^            ^
                # between them
                first_dash = file.find("-")
                last_start_bracket = file.rfind("[")
                user_name = file[first_dash + 1:last_start_bracket]
                csv_file_path = os.path.join(root, file)
                df = pd.read_csv(csv_file_path).assign(user_name=user_name)
                combined_data = pd.concat([combined_data, df])

    return combined_data


main()
