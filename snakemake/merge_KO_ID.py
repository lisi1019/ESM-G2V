from collections import defaultdict


gene_ko = {}
with open('/root/fsas/ESM-G2V/Data/Example/KO_identifiers/ko_annotation.txt', 'r') as f1:
    for line in f1:
        if line.strip() and not line.startswith('#'):  
            parts = line.strip().split()
           
            if parts[0] == '*':
                gene = parts[1]  
                ko = parts[2]   
                score = float(parts[4]) 
            else:
                gene = parts[0]  
                ko = parts[1]    
                score = float(parts[3])  
            
           
            if gene not in gene_ko or score > gene_ko[gene][1]:
                gene_ko[gene] = (ko, score)


with open('/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_ID.txt', 'r') as f2, \
     open('/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_mapping.txt', 'w') as out:
    for line in f2:
        parts = line.strip().split()
        if len(parts) >= 2:
            gene, num = parts[0], parts[1]
            if gene in gene_ko:
                out.write(f"{gene}\t{gene_ko[gene][0]}.{num}\n")  
            else:
                out.write(f"{gene}\thypo.{num}\n") 