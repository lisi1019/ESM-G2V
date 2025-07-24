import os


id_to_symbol = {}
with open('/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_mapping.txt', 'r') as f2:
    for line in f2:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            gene_id, symbol = parts[0], parts[1]
            id_to_symbol[gene_id] = symbol

def process_file(input_file_path, output_dir):
    output_lines = []
    with open(input_file_path, 'r') as f1:
        for line in f1:
            genes = line.strip().split()
            replaced_genes = []
            for gene in genes:
                if gene in id_to_symbol:
                    replaced_genes.append(id_to_symbol[gene])
            if replaced_genes:
                output_lines.append(" ".join(replaced_genes) + ". ")
    

    base_name = os.path.basename(input_file_path)
    output_file = os.path.join(output_dir, f"processed_{base_name}")
    
    with open(output_file, 'w') as out:
        out.write("".join(output_lines))


input_dir = '/root/fsas/ESM-G2V/Data/Example/deal_raw_data/deal_raw_gff'  
output_dir = '/root/fsas/ESM-G2V/Data/Example/KO_identifiers/genomo_text' 


os.makedirs(output_dir, exist_ok=True)


for filename in os.listdir(input_dir):
    if filename.endswith('.txt'): 
        input_file = os.path.join(input_dir, filename)
        process_file(input_file, output_dir)
        