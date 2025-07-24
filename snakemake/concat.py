import os
import torch
from gensim.models import Word2Vec
import gensim
from gensim.models import KeyedVectors
import argparse

def process_pt_file(file_path):
    try:
        data = torch.load(file_path)
        if isinstance(data, dict):
            label = data.get('label', '')
            vector = data.get('mean_representations', {}).get(6, None)
        elif isinstance(data, tuple) and len(data) >= 2:
            label, vector = data[0], data[1]
        else:
            print(f"Skipped {os.path.basename(file_path)}: Unsupported data structure.")
            return None

        if vector is not None:
            vector_array = vector.numpy() if isinstance(vector, torch.Tensor) else vector
            protein_id = label.split(' ')[0] if isinstance(label, str) else 'Unknown'
            vector_str = ','.join(map(str, vector_array.tolist()))
            return protein_id, vector_str
        else:
            print(f"Skipped {os.path.basename(file_path)}: No valid vector found.")
            return None
    except Exception as e:
        print(f"Error processing {os.path.basename(file_path)}: {e}")
        return None

def get_wv_from_model(w2v_model_path):
    try:
        model = Word2Vec.load(w2v_model_path)
        wv = model.wv
    except AttributeError:
        wv = KeyedVectors.load(w2v_model_path)
    return wv

def build_w2v_data_dict(w2v_model_path):
    wv = get_wv_from_model(w2v_model_path)
    data_dict = {}
    if gensim.__version__ >= '4.0':
        vocab = wv.index_to_key
    else:
        vocab = wv.index2word
    for word in vocab:
        vector = wv[word]
        vector_str = " ".join(map(str, vector))
        data_dict[word] = ','.join(map(str, vector_str.split()))
    return data_dict

def build_mapping_dict(mapping_file_path):
    mapping = {}
    try:
        with open(mapping_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line: 
                    parts = line.split('\t') if '\t' in line else line.split()
                    if len(parts) >= 2:
                        protein_id = parts[0].strip()  
                        ko_id = parts[1].strip()
                        mapping[protein_id] = ko_id
                    else:
                        print(f"Invalid line in mapping file (expected 2 columns): {line}")
    except Exception as e:
        print(f"Error reading mapping file: {e}")
    return mapping

def merge_files(pt_folder_path, new_folder_path, mapping_dict, data_dict):
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    for filename in os.listdir(pt_folder_path):
        if filename.endswith('.pt'):
            file_path = os.path.join(pt_folder_path, filename)
            protein_id = os.path.splitext(filename)[0]  
            
            if protein_id in mapping_dict:
                ko_id = mapping_dict[protein_id]
                if ko_id in data_dict:
                    result = process_pt_file(file_path)
                    if result:
                        protein_id_from_pt, esm_vector = result  
                        w2v_vector = data_dict[ko_id]
                        
                        merged_content = f"{protein_id_from_pt} {esm_vector},{w2v_vector}"
                        
                        output_filename = f"{protein_id}.txt"
                        output_path = os.path.join(new_folder_path, output_filename)
                        
                        with open(output_path, 'w') as f:
                            f.write(merged_content)
                        print(f"Merged: {filename} -> {output_filename}")
                else:
                    pass
                    #print(f"KO ID {ko_id} (from {protein_id}) not found in Word2Vec model")
            else:
                print(f"No mapping for protein ID: {protein_id} (file: {filename})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pt_folder',default='/root/fsas/ESM-G2V/Data/Example/deal_raw_data/faa_embedding', help='Path to the pt folder')
    parser.add_argument('--w2v_model',default='/root/fsas/ESM-G2V/Data/Example/G2V/G2V.w2v', help='Path to the w2v model')
    parser.add_argument('--mapping_file', default='/root/fsas/ESM-G2V/Data/Example/KO_identifiers/clusterRes_mapping.txt', help='Path to the mapping file')
    parser.add_argument('--new_folder', default='/root/fsas/ESM-G2V/Data/Example/merge_embedding', help='Path to the output folder')
    args = parser.parse_args()

    # 验证输入路径
    if not os.path.isdir(args.pt_folder):
        raise ValueError(f"PT folder does not exist: {args.pt_folder}")
    if not os.path.isfile(args.w2v_model):
        raise ValueError(f"Word2Vec model file does not exist: {args.w2v_model}")
    if not os.path.isfile(args.mapping_file):
        raise ValueError(f"Mapping file does not exist: {args.mapping_file}")

    w2v_data = build_w2v_data_dict(args.w2v_model)
    mappings = build_mapping_dict(args.mapping_file)
    merge_files(args.pt_folder, args.new_folder, mappings, w2v_data)