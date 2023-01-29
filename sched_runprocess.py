import glob
import time
from process2_optimized import sched_process

start_time = time.time()

# Import PDF
pdf_files = glob.glob('*.pdf')
df_all, df_dep, midnight_flt, df_passive, df_date, df_vertical, df_final, df_final_block = sched_process(pdf_files)

end_time = time.time()
run_time = end_time - start_time
print(df_final_block)
print('Total time: ', run_time)