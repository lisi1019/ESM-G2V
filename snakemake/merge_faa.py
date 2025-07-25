import os
def merge_faa_files(source_dir, output_file):
    try:
        with open(output_file, 'w') as outfile:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.faa'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as infile:
                            outfile.write(infile.read())
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    source_directory = '/root/fsas/ESM-G2V/Data/Example/raw_files/raw_faa' 
    output_filename = '/root/fsas/ESM-G2V/Data/Example/deal_raw_data/merged.faa' 
    merge_faa_files(source_directory, output_filename)
    