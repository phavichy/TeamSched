import pandas as pd
import numpy as np
import tabula
import re
import glob

# ######### PDF Import ##########
pdf_files = glob.glob('*.pdf')
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


# Fn to extract flight number from df_all
def extract_digits(row):
    # check if the cell contains a string
    if isinstance(row, str):
        # extract 3 consecutive standalone digits from the cell
        digits = re.findall(r'\b\d{3}\b', row)
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

df_flt = pd.DataFrame(extracted_digits, columns=['Flight Number'])
# remove duplicate rows
df_flt = df_flt['Flight Number'].unique()
df_flt = pd.DataFrame(df_flt, columns=['Flight Number'])
# Sorts
df_flt = df_flt.sort_values(by='Flight Number')
row_labels = list(range(1, len(df_flt) + 1))
df_flt.index = row_labels

# Extract Only Departures
index_array = np.array(df_flt.index)
mask = index_array % 2 == 1
df_flt_dep_only = df_flt[mask]
row_labels = list(range(1, len(df_flt_dep_only) + 1))
df_flt_dep_only.index = row_labels

flt_amount = df_flt_dep_only.shape

# ######### Schedule sort by Dates ##########

dates = df_all.columns[2:]
flight_numbers = df_flt_dep_only['Flight Number']
df_date = pd.DataFrame(columns=flight_numbers, index=dates)
# df_id = df_all.index[2:]
df_date = df_date.fillna('')

# Extract ID and Code to df_date
pattern = r'\b[a-zA-Z]{1,2}\b'
for date in dates:
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

# Convert the dates to strings
dates = [d.strftime('%a%d%b') for d in dates]

# Rename the row index of df_date
df_date.rename(index=dict(zip(df_date.index, dates)), inplace=True)


# ########### Create df to display each day schedule ###########
# Iterate over the dates
df_day_1 = df_date.iloc[0]
# Create a new dataframe with 8 columns for the pilot IDs and codes
df_pilots = pd.DataFrame(
    columns=['Flight Number', 'Pilot1', 'Code1', 'Pilot2', 'Code2', 'Pilot3', 'Code3', 'Pilot4', 'Code4'])

# Iterate over each cell in the 'df_day_1' column
for flight_number, cell in df_day_1.items():
    # Initialize a dictionary to store the pilot IDs and codes
    cell_dict = {'Flight Number': flight_number}
    # Split the cell by space to separate the IDs and codes
    cell_split = cell.split()
    # Iterate over the split cell data
    for i, data in enumerate(cell_split):
        # Check if the data is a pilot ID
        cell_dict[f'Pilot{(i + 1)}'] = re.sub(r'\D', '', data)
        cell_dict[f'Code{(i + 1)}'] = re.sub(r'\d', '', data)
    # Append the dictionary as a new row in the 'df_pilots' dataframe
    df_pilots = pd.concat([df_pilots, pd.DataFrame([cell_dict])], ignore_index=True)
    df_pilots = df_pilots.fillna('')


# ##### Create csv format table #######


# ######### Output ##########
print(df_date.to_string())
