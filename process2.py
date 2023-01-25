import pandas as pd
import numpy as np
import tabula
import re


def sched_process(pdf_files):
    df_list = []
    for pdf_file in pdf_files:
        df_list.append(pd.concat(tabula.read_pdf(pdf_file, pages="all")))

    # ######### Full Sched of Everyone ##########
    df = pd.concat(df_list)
    df = df.astype(str)
    df = df.replace('nan', np.nan)
    df = df.fillna('')
    df = df.replace('\r', ' ', regex=True)

    df['ID'] = df['Name'].str.extract(r'(\d+)')
    df['Rank'] = df['Name'].str.extract(r'\b\d{5}  ([A-Z]{1,4}) ')

    # Remove the original 'Name' column
    df.drop('Name', axis=1, inplace=True)
    columns = ['ID', 'Rank'] + [col for col in df.columns if col not in ['ID', 'Rank']]
    df = df.reindex(columns=columns)
    df = df.reset_index(drop=True)

    df_all = df.astype(str)
    df_all = df_all.replace(r'\.0', '', regex=True)

    # sort df_all by Rank
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

    # print(df_all.to_string())

    # Fn to extract flight number from df_all
    def extract_digits(row):
        # check if the cell contains a string
        if isinstance(row, str):
            # extract 3 consecutive standalone digits from the cell
            digits = re.findall(r'\b\d{3,4}\b', row)
            # return a list of extracted digits
            return digits
        # if the cell is not a string, return an empty list
        return []

    # Find the flight that depart after midnight
    midnight_flt = []

    for i in range(len(df_all.columns)):
        df_all.iloc[:, i] = df_all.iloc[:, i].astype(str)
        triple_asterisks = df_all.iloc[:, i].str.contains(r'\*\*\*')

        if i + 1 < len(df_all.columns):
            midnight_flt = df_all.loc[triple_asterisks, df_all.columns[i + 1]].apply(extract_digits)
            midnight_flt = [item for sublist in midnight_flt for item in sublist]

    midnight_flt = list(set(midnight_flt))

    # Remove the midnight flight from the first day (asterisk on last day of previous Month
    midnight_pattern = '|'.join(midnight_flt)

    for i, col in enumerate(df_all.columns):
        if i == 2:
            df_all[col] = df_all[col].str.replace(midnight_pattern, '', regex=True)

    # Shift Triple Asterisks (Midnight Flight) to a new format
    for i in range(len(df_all.columns)):
        # Convert the column to a string type
        df_all.iloc[:, i] = df_all.iloc[:, i].astype(str)

        # Check if the cell contains the pattern '***'
        triple_asterisks = df_all.iloc[:, i].str.contains(r'\*\*\*')

        # Shift the values in the next column to the current column
        # and replace the next column with '(shifted)'
        if i + 1 < len(df_all.columns):
            df_all.loc[triple_asterisks, df_all.columns[i]] = (
                    df_all.loc[triple_asterisks, df_all.columns[i + 1]]
                    + ' '
                    + df_all.loc[triple_asterisks, df_all.columns[i]]
            )
            df_all.loc[triple_asterisks, df_all.columns[i + 1]] = '<<<(shifted)'

    # Get the list of dates (excluded ID and Rank)
    columns_to_search = df_all.columns[2:-1]

    # create an empty list to store the extracted digits
    extracted_digits = []

    for index, row in df_all.iterrows():
        # loop through the specified columns
        for column in columns_to_search:
            # apply the extract_digits function to each cell
            cell_digits = extract_digits(row[column])
            # add the extracted digits to the list
            extracted_digits += cell_digits

    df_flt = pd.DataFrame(extracted_digits, columns=['TG'])
    # remove duplicate rows
    df_flt = df_flt['TG'].unique()
    df_flt = pd.DataFrame(df_flt, columns=['TG'])
    # Sorts
    df_flt = df_flt.sort_values(by='TG')
    row_labels = list(range(1, len(df_flt) + 1))
    df_flt.index = row_labels

    df_flt['TG'] = pd.to_numeric(df_flt['TG'])
    df_flt['TG_prev'] = df_flt['TG'].shift(1)
    df_flt['TG_next'] = df_flt['TG'].shift(-1)
    df_flt = df_flt[(df_flt['TG'] == df_flt['TG_prev'] + 1) | (df_flt['TG'] == df_flt['TG_next'] - 1)].reset_index(
        drop=True)
    df_flt = df_flt.drop(columns=['TG_prev', 'TG_next'])

    # Extract Only Departures
    index_array = np.array(df_flt.index)
    mask = index_array % 2 == 0
    df_dep = df_flt[mask]
    row_labels = list(range(1, len(df_dep) + 1))
    df_dep.index = row_labels

    # ######### Extract the flight with Passive Pilot ##########
    df_passive = pd.DataFrame(columns=['Flight Number', 'Date', 'Pilot'])
    passive_pattern = r'P \d{3,4}\b'

    for col in df_all.columns:
        for i, row in df_all[col].items():
            match = re.search(passive_pattern, str(row))
            if match:
                df_passive = pd.concat(
                    [df_passive, pd.DataFrame({'Flight Number': [row], 'Date': [col], 'Pilot': df_all.loc[i, 'ID']})],
                    ignore_index=True)

    # # ######### Schedule sort by Dates ##########

    dates_list = df_all.columns[2:]
    flight_numbers = df_dep['TG'].astype(str).tolist()
    df_date = pd.DataFrame(columns=flight_numbers, index=dates_list)
    df_date = df_date.fillna('')

    # Extract ID and Code to df_date
    pattern = r'\b[a-zA-Z]{1,2}\b'
    for date in dates_list:
        for flight_number in flight_numbers:
            ids = df_all[df_all[date].astype(str).str.contains(flight_number, regex=True)]['ID'].tolist()
            for id in ids:
                # extract code (if present) from cell
                cell_value = df_all.loc[df_all['ID'] == id, date].iloc[0]  # extract string value from series
                match = re.search(pattern, cell_value)  # use new regular expression to match code
                if match:
                    code = match.group(0)  # extract code from the match
                else:
                    code = ''
                # add ID and code to 'df_date' dataframe
                df_date.loc[date, flight_number] += f"{id}{code} "

    # rename the dates
    dates = pd.date_range('01/01/2023', '31/01/2023', freq='D')
    date_index = pd.DatetimeIndex(dates)
    # Convert the dates to strings
    date_index = [d.strftime('%a%d%b') for d in date_index]

    # Rename the row index of df_date
    df_date.rename(index=dict(zip(df_date.index, date_index)), inplace=True)

    # ########### Create df to display each day schedule ###########
    # Iterate over the dates
    # Create a new dataframe with 8 columns for the pilot IDs and codes
    df_pilots = pd.DataFrame(columns=['Flight Number', 'Pilot1', 'Pilot2', 'Pilot3', 'Pilot4', 'Pilot5'])
    df_pilots_all = pd.DataFrame(columns=['Flight Number', 'Pilot1', 'Pilot2', 'Pilot3', 'Pilot4', 'Pilot5'])
    df_header = pd.DataFrame(index=['Date'], columns=['Data', 'Code'])
    df_final = pd.DataFrame(index=['Date'], columns=['Data', 'Code'])
    for i, df_day in df_date.iterrows():
        df_pilots = pd.DataFrame(columns=['Flight Number', 'Pilot1', 'Pilot2', 'Pilot3', 'Pilot4', 'Pilot5'])
        for flight_number, cell in df_day.items():
            cell_dict = {'Flight Number': flight_number}
            cell_split = cell.split()
            for j, data in enumerate(cell_split):
                cell_dict[f'Pilot{(j + 1)}'] = data
            df_pilots = pd.concat([df_pilots, pd.DataFrame([cell_dict])], ignore_index=True)
        df_pilots = df_pilots.fillna('')
        df_pilots2 = pd.concat([pd.DataFrame([[i, '', '', '', '', '']], columns=df_pilots.columns), df_pilots],
                               ignore_index=True)
        df_pilots_all = pd.concat([df_pilots_all, df_pilots2], ignore_index=True)
        # stack the dataframe to make it taller and narrower
        df_csv = df_pilots.stack()
        df_csv = pd.DataFrame(df_csv)
        df_csv.rename(index={'Flight Number': '', 'Pilot1': '', 'Pilot2': '', 'Pilot3': '', 'Pilot4': '', 'Pilot5': ''},
                      inplace=True)
        df_csv.rename(columns={0: "Data"}, inplace=True)
        df_csv = df_csv.reset_index(drop=True)
        for k in range(len(df_csv)):
            match = re.search(r'\d{5}', df_csv.loc[k, 'Data'])
            if match:
                df_csv.loc[k, 'Code'] = ''.join(c for c in df_csv.loc[k, 'Data'] if not c.isdigit())
                df_csv.loc[k, 'Data'] = ''.join(c for c in df_csv.loc[k, 'Data'] if c.isdigit())
            else:
                df_csv.loc[k, 'Data'] = df_csv.loc[k, 'Data']
        df_csv = df_csv.fillna('')
        df_csv['Code'] = df_csv['Code'].astype(str)
        df_csv['Data'] = df_csv['Data'].astype(str)
        df_csv = pd.concat([pd.DataFrame([['', i]], columns=df_csv.columns), df_csv], ignore_index=True)
        df_final = pd.concat([df_final, df_csv], ignore_index=True)
    df_final = df_final.drop(0)

    df_final['next_data'] = df_final['Data'].shift(-1)
    df_final['next_code'] = df_final['Code'].shift(-1)
    cond_belowisempty = df_final['next_data'].str.match(r'^\s*$') & df_final['next_code'].str.match(r'^\s*$')
    cond_34letters = (df_final['Data'].str.match(r'^\d{3,4}$'))
    df_final = df_final.drop(df_final[cond_belowisempty & cond_34letters].index).drop(
        columns=['next_data', 'next_code'])

    # remove empty rows that below row is not empty
    df_final['next_data'] = df_final['Data'].shift(-1)
    df_final['next_code'] = df_final['Code'].shift(-1)
    cond_belowisempty = df_final['next_data'].str.match(r'^\s*$') & df_final['next_code'].str.match(r'^\s*$')
    cond_rowisempty = df_final['Data'].str.match(r'^\s*$') & df_final['Code'].str.match(r'^\s*$')
    cond_isdate = df_final['Data'].str.match(r'^\d{2}\w{3}$')
    df_final = df_final.drop(df_final[(cond_rowisempty & cond_belowisempty) & ~cond_isdate].index).drop(
        columns=['next_data', 'next_code'])

    # remove empty rows below the date
    df_final['prev_code'] = df_final['Code'].shift(1)
    cond_aboveisdate = df_final['prev_code'].str.match(r'^([A-Za-z]{3})(\d{2})([A-Za-z]{3})$')
    cond_rowisempty = df_final['Data'].str.match(r'^\s*$') & df_final['Code'].str.match(r'^\s*$')
    df_final = df_final.drop(df_final[(cond_rowisempty & cond_aboveisdate)].index).drop(columns=['prev_code'])

    df_final['Data'] = df_final['Data'].str.replace(r'(\b\d{3}\b)', r'TG\1', regex=True)
    df_final = df_final.reset_index(drop=True)

    # Text to return a process is completed
    completed_text = 'Process completed'
    return df_all, df_dep, midnight_flt, df_passive, df_date, df_pilots_all, df_final, completed_text
