import pandas as pd
import numpy as np
import PyQt5 as pqt
import tabula
from tabula import read_pdf
import re
import glob

########## PDF Import ##########
pdf_files = glob.glob('*.pdf')
df_list = []

for pdf_file in pdf_files:
    df_list.append(pd.concat(tabula.read_pdf(pdf_file, pages="all")))


########## Full Sched of Everyone ##########

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

#get numbers of rows and columns
num_rows, num_columns = df.shape



########## Extract the flights list for this month ##########
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
columns_to_search = df.columns[2:-1]

# create an empty list to store the extracted digits
extracted_digits = []

for index, row in df.iterrows():
    # loop through the specified columns
    for column in columns_to_search:
        # apply the extract_digits function to each cell
        cell_digits = extract_digits(row[column])
        # add the extracted digits to the list
        extracted_digits += cell_digits

df_flt = pd.DataFrame(extracted_digits, columns=['Flight Number'])
# remove duplicate rows
df_flt = df_flt.drop_duplicates()
# Sorts
df_flt_sorted = df_flt.sort_values(by='Flight Number')
row_labels = list(range(1, len(df_flt_sorted) + 1))
df_flt_sorted.index = row_labels

#Extract Only Departures
mask = df_flt_sorted.index % 2 == 1
df_flt_dep_only = df_flt_sorted[mask]
row_labels = list(range(1, len(df_flt_dep_only) + 1))
df_flt_dep_only.index = row_labels

flt_amount = df_flt_dep_only.shape


########## Schedule sort by Dates ##########

dates = df.columns[2:]
flight_numbers = df_flt_dep_only['Flight Number']
df_new = pd.DataFrame(columns=flight_numbers, index=dates)
df_id = df.index[2:]
df_new = df_new.fillna('x')


# Check How many Pilot per Flight
# for date in dates:
#     for flight_number in flight_numbers:
#         count = df[date].str.contains(flight_number).sum()
#         df_new.loc[date, flight_number] = count

# for date in dates:
#     for flight_number in flight_numbers:
#         ids = df[df[date].astype(str).str.contains(flight_number)]['ID'].tolist()
#         ids_str = ' '.join(ids)
#         df_new.loc[date, flight_number] = ids_str

for date in dates:
    for flight_number in flight_numbers:
        ids = df[df[date].astype(str).str.contains(flight_number)]['ID'].tolist()
        code = str.extract('\d+').fillna('')
        ids_str = ' '.join(ids)
        df_new.loc[date, flight_number] = ids_str





########## Output ##########
#print(f'Total {num_rows} rows // {num_columns} columns')
#print(df.to_string())
#print("\n")
#print(f' This Month Total {flt_amount} Flights)')
#print(df_flt_dep_only.to_string())
#print("\n")
#print(df_new.to_string())
#print("\n")
print(code)