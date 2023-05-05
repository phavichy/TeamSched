import pandas as pd
import numpy as np
import tabula
import re


def body_import(pdf_files):
    df_all = pd.concat([pd.concat(tabula.read_pdf(pdf_file, pages="all")) for pdf_file in pdf_files])
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
    df_flt = df_flt.reset_index(drop=True)
    df_flt.index += 1
    return df_all, df_flt
