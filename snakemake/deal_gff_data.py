import os


input_folder = '/root/fsas/ESM-G2V/Data/Example/raw_files/raw_gff'

output_folder = '/root/fsas/ESM-G2V/Data/Example/deal_raw_data/deal_raw_gff'


if not os.path.exists(output_folder):
    os.makedirs(output_folder)


for filename in os.listdir(input_folder):
    if filename.endswith('.gff'): 
        file_path = os.path.join(input_folder, filename)
       
        with open(file_path, 'r') as file:
            lines = file.readlines()


        current_first_col = None
        ids = []
        output_lines = []

       
        for line in lines:
            parts = line.strip().split('\t')
            first_col = parts[0]
            attributes = parts[-1]
           
            if first_col != current_first_col and current_first_col is not None:
                output_lines.append(' '.join(ids))
                ids = []
           
            for attr in attributes.split(';'):
                if attr.startswith('ID='):
                    id_value = attr.split('=')[1]
                    ids.append(id_value)
                    break
            current_first_col = first_col

        
        if ids:
            output_lines.append(' '.join(ids))

        
        output_file_name = os.path.splitext(filename)[0] + '_output.txt'
        output_file_path = os.path.join(output_folder, output_file_name)

       
        with open(output_file_path, 'w') as output_file:
            for output_line in output_lines:
                output_file.write(output_line + '\n')