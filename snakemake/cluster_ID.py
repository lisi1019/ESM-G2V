def process_sequences(input_file, output_file):
    current_group = 0
    prev_line_was_header = False
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if line.startswith('>'):
                seq_id = line[1:]
               
                if prev_line_was_header:
                    current_group += 1
               
                prev_line_was_header = True
            else:
               
                if line and prev_line_was_header:
                    outfile.write(f"{last_seq_id} {current_group}\n")
                prev_line_was_header = False
           
            if line.startswith('>'):
                last_seq_id = line[1:]


process_sequences("/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_all_seqs.fasta", "/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_ID.txt")
