# Original Code
for index, row in df_all.iterrows():
    for column in columns_to_search:
        extracted_digits.extend(extract_digits(row[column]))

# Optimized Code
extracted_digits = [extract_digits(row[column]) for index, row in df_all.iterrows() for column in columns_to_search]
