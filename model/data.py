import numpy as np
import pandas as pd
import os
import re
import ast
import tensorflow as tf
import tempfile
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

class Embedding(object):
    def __init__(self, txt_file, metadata, labels=None):
        # Load data from text file
        with open(txt_file, 'r') as file:
            lines = file.readlines()
       
        data = []
        skipped_lines = []
        
        for idx, line in enumerate(lines):
            try:
               
                parts = line.strip().split(' ', 1)
                if len(parts) < 2:
                    print(f"Skipping line {idx + 1}: does not contain enough parts")
                    skipped_lines.append(line)
                   
                    continue
                key = parts[0].strip()  # Identifier
                vector_str = parts[1].strip()  # Vector part as string

                # Convert vector string to numpy array
                vector = np.array([float(num) for num in vector_str.split(', ')], dtype=np.float16)
                data.append((key, vector))
            except Exception as e:
                print(f"Error processing line {idx + 1}: {line.strip()}, Error: {e}")
                #skipped_lines += 1
                skipped_lines.append(line)

        self.mdl_data = data
        self.metadata = pd.read_csv(metadata)
        self.labels = labels
        self.effective_words = None
        self.train_words = None
        self.data = None
        self.data_with_words = None
        

        

    def extract_known_words(self, unknown="hypo"):
        known_words = [item[0] for item in self.mdl_data if unknown not in item[0]]
        known_embeddings = np.array([item[1] for item in self.mdl_data if unknown not in item[0]])
        self.known_words = known_words
        self.known_embeddings = known_embeddings
       
    def extract_effective_words(self, label='label'):
        metadata = self.metadata
        metadata[label] = metadata[label].apply(lambda x: re.split('(.)\[|\(|,', x)[0].strip())
        eff_words = pd.DataFrame({'word': self.known_words})
        eff_words["KO"] = eff_words["word"].apply(lambda x: x.rsplit(".")[0])
        eff_words = eff_words.merge(metadata, on=["KO"], how='left')[["word", label]].dropna()
        self.effective_words = eff_words
        print(f"Total effective words: {len(self.effective_words)}")

    def filter_effective_words(self, q=0.96, label='label'):
        eff_words = self.effective_words
        labels = self.labels
        if labels is None:
            labels_count = eff_words.groupby(label).size().reset_index(name="size").\
                sort_values(by="size", ascending=False)
            labels_to_keep = labels_count[labels_count["size"] >= np.quantile(labels_count["size"], q)]
            labels_to_keep = labels_to_keep[
                ~labels_to_keep[label].isin(["Function unknown [99997]", "Enzymes with EC numbers [99980]"])]
            labels = labels_to_keep[label].values

        eff_words = eff_words[eff_words[label].isin(labels)]
        self.train_words = eff_words
        print(f"Total filtered effective words: {len(self.train_words)}")

        if self.labels is None:
            self.labels = eff_words[label].unique()

    
    def add_other_class(self, label='label', min_points=1):
        eff_words = self.effective_words
        eff_words[label] = eff_words[label].apply(lambda x: re.split('(.)\[|\(|,', x)[0].strip())

        label_sizes = eff_words.groupby('label').size().reset_index(name='size')
        labels_to_keep = self.labels

        sample_from = label_sizes[~label_sizes["label"].isin(labels_to_keep)].sort_values(by='size', ascending=False)
        labels_to_sample_from = sample_from[sample_from['size'] > min_points]['label']
        label_counts = eff_words[eff_words['label'].isin(labels_to_sample_from)]['label'].value_counts()
        

       
        other_class = eff_words[eff_words['label'].isin(labels_to_sample_from)]
        print(len(other_class))

       
        other_class['label'] = 'Other'

       
        data_with_other = pd.concat([self.train_words, other_class])
        self.train_words = data_with_other
        print(f"Total words after adding 'Other' class: {len(self.train_words)}")
    

    def cleanup_train_data(self, add_other=False):
        df = pd.DataFrame(self.known_embeddings)
        if add_other:
            self.add_other_class()
        df = df.reset_index().merge(self.train_words, left_index=True, right_index=True, how="right")
        
        self.data_with_words = df
        with open('/public/home/xjy/data/paper/data/contigs_data/mnt/Data5/ls_data/NLP/output/G2V/words_column.txt', 'w') as file:
            for word in self.data_with_words['word']:
                file.write(f"{word}\n")
        # Handle NaN and infinite values
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)
       # print(f"Data after cleaning NaN and infinite values: {df.shape[0]}")

        self.data = df.drop(columns=["index", "word"])

    def process_data_pipeline(self, label, q, add_other=False):
        

        self.extract_known_words()
        self.extract_effective_words(label=label)
        self.filter_effective_words(q=q, label=label)

        # Handle NaN values in train_words before cleanup
        self.train_words.dropna(inplace=True)

        self.cleanup_train_data(add_other=add_other)


