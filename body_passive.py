import pandas as pd
import re


def body_passive(df_all):
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
    return df_passive
