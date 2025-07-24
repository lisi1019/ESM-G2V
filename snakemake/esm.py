import os

import logging
input_folder = '/root/fsas/ESM-G2V/Data/Example/raw_files/raw_faa'
output_folder = '/root/fsas/ESM-G2V/Data/Example/deal_raw_data/faa_embedding'
os.makedirs(output_folder, exist_ok=True)
faa_files = [file for file in os.listdir(input_folder) if file.endswith('.faa')]
for faa_file in faa_files:
    filepath = os.path.join(input_folder, faa_file)
    protein_id = os.path.splitext(faa_file)[0]
    command = f"python /root/fsas/Project/esm-main/scripts/extract.py esm2_t6_8M_UR50D {filepath} {output_folder} --include mean"
    try:
        return_code = os.system(command)
    except Exception as e:
        logging.error(f"An error occurred while processing file {faa_file}: {str(e)}")