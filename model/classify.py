import logging
import os
os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3,4,5,6,7'
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold
from src.genomic_embeddings.models import NNClf, NNClfFolds
from src.genomic_embeddings.data import Embedding
from src.genomic_embeddings.plot import ModelPlots, FoldModelPlots
import argparse
import logging
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        print(e)
argparse = argparse.ArgumentParser()
argparse.add_argument('--model', required=True, type=str, help='model file')
argparse.add_argument('--output',
                      default='/root/fsas/ESM-G2V/model',
                      type=str, help='predictions output dir')
argparse.add_argument('--metadata',
                      default='/root/fsas/ESM-G2V/model/metadata.csv',
                      type=str, help='metadata csv file path')
params = argparse.parse_args()

MODEL = params.model
METADATA = params.metadata
OUTPUT_DIR = params.output

# configure logger
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename=os.path.join(OUTPUT_DIR, "Validation.log"), level=logging.INFO)

# Define your labels and other parameters
curated_labels_no_pumps = [
    'Amino sugar and nucleotide sugar metabolism',
    'Benzoate degradation',
    'Energy metabolism',
    'Oxidative phosphorylation',
    'Porphyrin and chlorophyll metabolism',
    'Prokaryotic defense system',
    'Ribosome',
    'Secretion system',
    'Two-component system'
  
]

labels = [
    (curated_labels_no_pumps, 'NO-PUMPS-CURATED-LABELS')
]

LABEL = 'label'
q = ''

# Iterate over each label set
for label, label_alias in labels:
    alias = label_alias
    logging.info(f"=== Extract embedding for label = {LABEL}, Q= {q}")
    emb = Embedding(txt_file=MODEL, metadata=METADATA, labels=label)
    emb.process_data_pipeline(label=LABEL, q=q, add_other=True)
    logging.info(f"Number of effective words: {emb.effective_words.shape[0]}\n")
    dataset = tf.data.Dataset.from_tensor_slices((emb.data.drop(columns=[LABEL]).values, emb.data[LABEL].values))
    dataset = dataset.shuffle(buffer_size=len(emb.data)).batch(batch_size=32) 
    X_train_full, X_final_test, y_train_full, y_final_test = train_test_split(
        emb.data.drop(columns=[LABEL]).values, emb.data[LABEL].values,
        test_size=0.3, random_state=42, stratify=emb.data[LABEL].values
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full,
        test_size=0.2, random_state=42, stratify=y_train_full
    )

    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    logging.info(f"Matrix shape is: {X_train_full.shape}, 20% used for final testing\n"
                 f"Train size: {X_train.shape[0]}, Validation size: {X_val.shape[0]}, Final Test size: {X_final_test.shape[0]}\n"
                 f"Number of unique classes: {pd.Series(y_train_full).nunique()}")
   
    # Define models to train
    MDLS = [
        (NNClf(X=X_train_full, y=y_train_full, out_dir=OUTPUT_DIR), alias),
    ]

    # Train and evaluate each model
    for mdl, name in MDLS:
        mdl.classification_pipeline(LABEL, alias=name)
        
        # Evaluate on validation set
        val_loss, val_accuracy = mdl.evaluate(X_val, y_val)
        logging.info(f"Validation set performance for {name}:")
        logging.info(f"Validation Loss: {val_loss}")
        logging.info(f"Validation Accuracy: {val_accuracy}")
        
        # Evaluate on final test set
        test_loss, test_accuracy = mdl.evaluate(X_final_test, y_final_test)
        logging.info(f"Final test set performance for {name}:")
        logging.info(f"Test Loss: {test_loss}")
        logging.info(f"Test Accuracy: {test_accuracy}")

        # Plot results
        if 'FOLD' in name:
            plotter = FoldModelPlots(mdl=mdl)
            plotter.plot_single_aupr_with_ci()
            plotter.plot_single_roc_with_ci()
        else:
            plotter = ModelPlots(mdl=mdl)
        
        plotter.plot_precision_recall()
        plotter.plot_roc()
