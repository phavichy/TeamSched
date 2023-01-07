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
# create a dictionary that maps rank names to a numerical order
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
# sort df_all by the mapped values
df_all = df_all.sort_values(by='Rank', key=lambda x: x.map(rank_order))

# get numbers of rows and columns
# num_rows, num_columns = df_all.shape
# columns_to_search = df_all.columns[2:(num_columns - 1)]

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


# ######## Extract the flights list for this month ##########
def extract_digits(row):
    # check if the cell contains a string
    if isinstance(row, str):
        # extract 3 consecutive standalone digits from the cell
        digits = re.findall(r'\b\d{3}\b', row)
        # return a list of extracted digits
        return digits
    # if the cell is not a string, return an empty list
    return []


# get the 3rd to last columns
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
pattern = r'\b[a-zA-Z]{1}\b'
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
            df_date.loc[date, flight_number] += f" {code} {id}"

# ######### Output ##########
print(df_all.to_string())
print('\n')
print(df_flt_dep_only.to_string())
print('\n')
print(df_date.to_string())
print('\n')
