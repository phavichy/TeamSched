import pandas as pd
import numpy as np
import tabula
import re
import time

def sched_process(pdf_files):
    start_time = time.time()
    df_all = pd.concat([pd.concat(tabula.read_pdf(pdf_file, pages="all")) for pdf_file in pdf_files])
    end_time = time.time()
    print("df_all time taken: ", end_time - start_time)
    df_all = df_all.astype(str)
    df_all = df_all.replace('nan', np.nan)
    df_all = df_all.fillna('')
    df_all = df_all.replace('\r', ' ', regex=True)

    df_all['ID'] = df_all['Name'].str.extract(r'(\d+)')
    df_all['Rank'] = df_all['Name'].str.extract(r'\b\d{5}  ([A-Z]{1,4}) ')

    df_all.drop('Name', axis=1, inplace=True)
    columns = ['ID', 'Rank'] + [col for col in df_all.columns if col not in ['ID', 'Rank']]
    df_all = df_all.reindex(columns=columns)
    df_all = df_all.reset_index(drop=True)

    df_all = df_all.astype(str)
    df_all = df_all.replace(r'\.0', '', regex=True)

    rank_order = {
        'FCIV': 1,
        'FCRV': 2,
        'FCRH': 3,
        'FCI': 4,
        'FCR': 5,
        'FCS': 6,
        'FC': 7,
        'FCT': 8,
        'FPIR': 9,
        'FPI': 10,
        'FPR': 11,
        'FPRX': 12,
        'FP': 13,
        'FPX': 14,
        'FPT': 15,
    }
    df_all = df_all.sort_values(by='Rank', key=lambda x: x.map(rank_order))
    unnamed_cols = [col for col in df_all.columns if 'Unnamed' in col]
    df_all = df_all.drop(columns=unnamed_cols)


    def extract_digits(row1):
        return re.findall(r'\b\d{3,4}\b', row1) if isinstance(row1, str) else []

    # Extract Flight departs after midnight from df_all to midnight_flt[]
    # Then shifted the ***
    midnight_flt = []

    for i, col in enumerate(df_all.columns):
        df_all.iloc[:, i] = df_all.iloc[:, i].astype(str)
        triple_asterisks = df_all.iloc[:, i].str.contains(r'\*\*\*')

        if i + 1 < len(df_all.columns):
            midnight_flt = df_all.loc[triple_asterisks, df_all.columns[i + 1]].apply(extract_digits)
            midnight_flt = [item for sublist in midnight_flt for item in sublist]

    midnight_flt = list(set(midnight_flt))

    midnight_pattern = '|'.join(midnight_flt)
    df_all[df_all.columns[2]] = df_all[df_all.columns[2]].str.replace(midnight_pattern, '', regex=True)

    for i in range(len(df_all.columns)):
        df_all.iloc[:, i] = df_all.iloc[:, i].astype(str)
        triple_asterisks = df_all.iloc[:, i].str.contains(r'\*\*\*')
        if i + 1 < len(df_all.columns):
            df_all.loc[triple_asterisks, df_all.columns[i]] = \
                (
                    df_all.loc[triple_asterisks, df_all.columns[i + 1]]
                    + ' '
                    + df_all.loc[triple_asterisks, df_all.columns[i]]
                )
            df_all.loc[triple_asterisks, df_all.columns[i + 1]] = '<<<(shifted)'


    # Extract the flight numbers this month to df_dep
    columns_to_search = df_all.columns[2:-1]
    extracted_digits = []

    for index, row in df_all.iterrows():
        for column in columns_to_search:
            extracted_digits.extend(extract_digits(row[column]))

    df_flt = pd.DataFrame(extracted_digits, columns=['TG'])
    df_flt = df_flt['TG'].unique()
    df_flt = pd.DataFrame(df_flt, columns=['TG'])
    df_flt = df_flt.sort_values(by='TG')
    row_labels = list(range(1, len(df_flt) + 1))
    df_flt.index = row_labels
    df_flt['TG'] = pd.to_numeric(df_flt['TG'])
    df_flt['TG_prev'] = df_flt['TG'].shift(1)
    df_flt['TG_next'] = df_flt['TG'].shift(-1)
    df_flt = df_flt[(df_flt['TG'] == df_flt['TG_prev'] + 1) | (df_flt['TG'] == df_flt['TG_next'] - 1)].reset_index(
        drop=True)
    df_flt = df_flt.drop(columns=['TG_prev', 'TG_next'])

    index_array = np.array(df_flt.index)
    mask = index_array % 2 == 0
    df_dep = df_flt[mask]
    row_labels = list(range(1, len(df_dep) + 1))
    df_dep.index = row_labels

    # Extract information of passive pilots to df_passive
    df_passive = pd.DataFrame(columns=['Flight Number', 'Date', 'Pilot'])
    passive_pattern = r'P \d{3,4}\b'
    for col in df_all.columns:
        for i, row in df_all[col].items():
            match = re.search(passive_pattern, str(row))
            if match:
                df_passive = pd.concat(
                    [df_passive, pd.DataFrame({'Flight Number': [row], 'Date': [col], 'Pilot': df_all.loc[i, 'ID']})],
                    ignore_index=True)

    # Re-arrange dataframe to dates as index in df_date
    dates_list = df_all.columns[2:]
    flight_numbers = df_dep['TG'].astype(str).tolist()
    df_date = pd.DataFrame(columns=flight_numbers, index=dates_list)
    df_date = df_date.fillna('')

    pattern = r'\b[a-zA-Z]{1,2}\b'
    for date in dates_list:
        for flight_number in flight_numbers:
            ids = df_all[df_all[date].astype(str).str.contains(flight_number, regex=True)]['ID'].tolist()
            for pilot_id in ids:
                cell_value = df_all.loc[df_all['ID'] == pilot_id, date].iloc[0]
                match = re.search(pattern, cell_value)
                if match:
                    code = match.group(0)
                else:
                    code = ''
                df_date.loc[date, flight_number] += f"{pilot_id}{code} "

    dates = pd.date_range('01/Jan/2023', '31/Jan/2023', freq='D')
    date_index = pd.DatetimeIndex(dates)
    date_index = [d.strftime('%a%d%b') for d in date_index]

    df_date.rename(index=dict(zip(df_date.index, date_index)), inplace=True)

    # Create vertical dataframe as df_vertical
    df_vertical = pd.DataFrame(columns=['Flight Number', 'Pilot1', 'Pilot2', 'Pilot3', 'Pilot4', 'Pilot5', 'Pilot6'])
    df_final = pd.DataFrame(index=['Date'], columns=['Data', 'Date', 'Code'])
    for i, df_1day in df_date.iterrows():
        df_pilots = pd.DataFrame(columns=['Flight Number', 'Pilot1', 'Pilot2', 'Pilot3', 'Pilot4', 'Pilot5', 'Pilot6'])
        for flight_number, cell in df_1day.items():
            cell_dict = {'Flight Number': flight_number}
            cell_split = cell.split()
            for j, data in enumerate(cell_split):
                cell_dict[f'Pilot{(j + 1)}'] = data
            df_pilots = pd.concat([df_pilots, pd.DataFrame([cell_dict])], ignore_index=True)
        df_pilots = df_pilots.fillna('')
        df_pilots2 = pd.concat([pd.DataFrame([[i, '', '', '', '', '', '']], columns=df_pilots.columns), df_pilots],
                               ignore_index=True)
        df_vertical = pd.concat([df_vertical, df_pilots2], ignore_index=True)

        # create final dataframe as df_final and df_final_block
        df_stack = df_pilots.stack()
        df_stack = pd.DataFrame(df_stack)
        df_stack.rename(index={'Flight Number': '', 'Pilot1': '', 'Pilot2': '', 'Pilot3': '', 'Pilot4': '', 'Pilot5': '', 'Pilot6': ''},
                        inplace=True)
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
    cond_is_date = df_final['Data'].str.match(r'^\d{2}\w{3}$')
    df_final = df_final.drop(df_final[(cond_row_is_empty & cond_below_is_empty) & ~cond_is_date].index).drop(
        columns=['next_data', 'next_code'])

    df_final['prev_code'] = df_final['Code'].shift(1)
    cond_above_is_date = df_final['prev_code'].str.match(r'^([A-Za-z]{3})(\d{2})([A-Za-z]{3})$')
    cond_row_is_empty = df_final['Data'].str.match(r'^\s*$') & df_final['Code'].str.match(r'^\s*$')
    df_final = df_final.drop(df_final[(cond_row_is_empty & cond_above_is_date)].index).drop(columns=['prev_code'])

    df_final['Data'] = df_final['Data'].str.replace(r'(\b\d{3}\b)', r'TG\1', regex=True)
    df_final_block['Data'] = df_final_block['Data'].str.replace(r'(\b\d{3}\b)', r'TG\1', regex=True)
    df_final = df_final.reset_index(drop=True)
    df_final_block = df_final_block.reset_index(drop=True)

    return df_all, df_dep, midnight_flt, df_passive, df_date, df_vertical, df_final, df_final_block
