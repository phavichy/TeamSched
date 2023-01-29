# Original Code
def sched_process(pdf_files):
    df_all = pd.concat([pd.concat(tabula.read_pdf(pdf_file, pages="all")) for pdf_file in pdf_files])

# use process pool to speed up the process
with concurrent.futures.ProcessPoolExecutor() as executor:
    df_all = pd.concat(executor.map(pd.concat, [tabula.read_pdf(pdf_file, pages="all") for pdf_file in pdf_files]))

