def process_sequences(input_file, output_file):
    current_group = 0
    prev_line_was_header = False
    
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if line.startswith('>'):
                seq_id = line[1:]
                # 检查是否是分组标记行（当前是header且上一条也是header）
                if prev_line_was_header:
                    current_group += 1
                # 记录当前行类型
                prev_line_was_header = True
            else:
                # 如果是序列行且上一条是header，则输出
                if line and prev_line_was_header:
                    outfile.write(f"{last_seq_id} {current_group}\n")
                prev_line_was_header = False
            # 保存最后一个遇到的seq_id
            if line.startswith('>'):
                last_seq_id = line[1:]

# 使用示例
process_sequences("/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_all_seqs.fasta", "/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_ID.txt")