import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from focal_loss import SparseCategoricalFocalLoss

model_path = '/root/fsas/ESM-G2V/model/ESM_gene2vec.h5'
model = load_model(model_path,custom_objects={'SparseCategoricalFocalLoss': SparseCategoricalFocalLoss})

labels = [
    'Amino sugar and nucleotide sugar metabolism',
    'Benzoate degradation',
    'Energy metabolism',
    'Other',
    'Oxidative phosphorylation',
    'Porphyrin and chlorophyll metabolism',
    'Prokaryotic defense system',
    'Ribosome',
    'Secretion system',
    'Two-component system'
]

label_mapping = {i: label for i, label in enumerate(labels)}
input_folder = '/root/fsas/ESM-G2V/Data/Example/merge_embedding'
output_folder = '/root/fsas/ESM-G2V/Data/Example/predictions'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        results = []

        for line in lines:
            parts = line.strip().split(' ')
            gene_id = parts[0]  

            feature_str = parts[1]
            features = feature_str.split(',')

            features = np.array(features, dtype=np.float32)

            features = features.reshape(1, -1) 

            y_pred = model.predict(features)
            y_pred_class = np.argmax(y_pred, axis=1)[0]  
            y_pred_label = label_mapping[y_pred_class]  
            y_pred_prob = np.max(y_pred)  

            results.append(f'{gene_id} {y_pred_label} {y_pred_prob:.4f}')

        output_filename = filename.replace('.txt', '.prediction.txt')
        output_file = os.path.join(output_folder, output_filename)

        with open(output_file, 'w') as f:
            f.write('\n'.join(results))

        print(f"Predictions for {filename} saved to {output_file}") 