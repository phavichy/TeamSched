import pandas as pd
import numpy as np
import re


def get_max_pilots(df_date):
    max_pilots = 4
    for _, row in df_date.iterrows():
        for cell in row:
            num_pilots = len(cell.split())
            if num_pilots > max_pilots:
                max_pilots = num_pilots
    return max_pilots


def body_final(df_date):
    max_pilots = get_max_pilots(df_date)
    # Create vertical dataframe as df_vertical
    columns = ['Flight Number'] + [f'Pilot{i + 1}' for i in range(max_pilots)]
    df_vertical = pd.DataFrame(columns=columns)
    df_final = pd.DataFrame(index=['Date'], columns=['Data', 'Date', 'Code'])
    for i, df_1day in df_date.iterrows():
        df_pilots = pd.DataFrame(columns=columns)
        for flight_number, cell in df_1day.items():
            cell_dict = {'Flight Number': flight_number}
            cell_split = cell.split()
            for j, data in enumerate(cell_split):
                cell_dict[f'Pilot{(j + 1)}'] = data
            df_pilots = pd.concat([df_pilots, pd.DataFrame([cell_dict])], ignore_index=True)
        df_pilots = df_pilots.fillna('')
        df_pilots2 = pd.concat([pd.DataFrame([[i] + [''] * max_pilots], columns=df_pilots.columns), df_pilots]
                               , ignore_index=True)
        df_vertical = pd.concat([df_vertical, df_pilots2], ignore_index=True)

        # create final dataframe as df_final and df_final_block
        df_stack = df_pilots.stack()
        df_stack = pd.DataFrame(df_stack)
        df_stack.rename(index={**{'Flight Number': ''}, **{f'Pilot{i + 1}': '' for i in range(max_pilots)}}
                        , inplace=True)
        df_stack.rename(columns={0: "Data"}, inplace=True)
        df_stack = df_stack.reset_index(drop=True)
        df_stack['Code'] = ''
        for k in range(len(df_stack)):
            match = re.search(r'\d{5}', df_stack.loc[k, 'Data'])
            if match:
                df_stack.loc[k, 'Code'] = ''.join(c for c in df_stack.loc[k, 'Data'] if not c.isdigit())
                df_stack.loc[k, 'Data'] = ''.join(c for c in df_stack.loc[k, 'Data'] if c.isdigit())
            else:
                df_stack.loc[k, 'Data'] = df_stack.loc[k, 'Data']
        # create new column in df_stack 'Date' and fill it with empty string as the second column
        df_stack.insert(1, 'Date', '')
        df_stack = df_stack.fillna('')
        df_stack['Data'] = df_stack['Data'].astype(str)
        df_stack['Date'] = df_stack['Date'].astype(str)
        df_stack['Code'] = df_stack['Code'].astype(str)
        df_stack = pd.concat([pd.DataFrame([['', i, '']], columns=df_stack.columns), df_stack], ignore_index=True)
        df_final = pd.concat([df_final, df_stack], ignore_index=True)
    df_final = df_final.drop(0)
    df_final_block = df_final.copy()

    df_final['next_data'] = df_final['Data'].shift(-1)
    df_final['next_code'] = df_final['Code'].shift(-1)
    cond_below_is_empty = df_final['next_data'].str.match(r'^\s*$') & df_final['next_code'].str.match(r'^\s*$')
    cond_34letters = (df_final['Data'].str.match(r'^\d{3,4}$'))
    df_final = df_final.drop(df_final[cond_below_is_empty & cond_34letters].index).drop(
        columns=['next_data', 'next_code'])

    df_final['next_data'] = df_final['Data'].shift(-1)
    df_final['next_code'] = df_final['Code'].shift(-1)
    cond_below_is_empty = df_final['next_data'].str.match(r'^\s*$') & df_final['next_code'].str.match(r'^\s*$')
    cond_row_is_empty = df_final['Data'].str.match(r'^\s*$') & df_final['Code'].str.match(r'^\s*$')
    cond_is_date = df_final['Date'].str.match(r'^([A-Za-z]{3})(\d{2})([A-Za-z]{3})$')
    df_final = df_final.drop(df_final[(cond_row_is_empty & cond_below_is_empty) & ~cond_is_date].index).drop(
        columns=['next_data', 'next_code'])

    df_final['prev_code'] = df_final['Code'].shift(1)
    df_final['prev_date'] = df_final['Date'].shift(1)
    cond_above_is_date = df_final['prev_date'].str.match(r'^([A-Za-z]{3})(\d{2})([A-Za-z]{3})$')
    cond_row_is_empty = df_final['Data'].str.match(r'^\s*$') & df_final['Code'].str.match(r'^\s*$')
    df_final = df_final.drop(df_final[(cond_row_is_empty & cond_above_is_date)].index).drop(
        columns=['prev_code', 'prev_date'])

    df_final['Data'] = df_final['Data'].str.replace(r'(\b\d{3}\b)', r'TG\1', regex=True)
    df_final_block['Data'] = df_final_block['Data'].str.replace(r'(\b\d{3}\b)', r'TG\1', regex=True)
    df_final = df_final.reset_index(drop=True)
    df_final_block = df_final_block.reset_index(drop=True)

    return df_vertical, df_final, df_final_block


def count_flights(df_final):
    # Filter rows containing flight numbers (assuming flight numbers start with 'TG')
    flight_rows = df_final['Data'].str.startswith('TG')
    # Get the flight numbers from the filtered rows
    flight_numbers = df_final.loc[flight_rows, 'Data']
    # Count the occurrences of each flight number
    flight_counts = flight_numbers.value_counts()

    # Convert the Series to a DataFrame
    df_flightcounts = flight_counts.reset_index()
    df_flightcounts.columns = ['Flight Number', 'Count']

    return df_flightcounts

