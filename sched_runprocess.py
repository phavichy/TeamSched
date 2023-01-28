import glob
from process import sched_process

# Import PDF
pdf_files = glob.glob('*.pdf')
df_all, df_dep, midnight_flt, df_passive, df_date, df_vertical, df_final, df_final_block = sched_process(pdf_files)
