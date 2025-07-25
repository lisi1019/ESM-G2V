import codecs
import glob
import logging
import multiprocessing
from tqdm import tqdm
import argparse
import os
import pickle
import sys
import sklearn.manifold
import pandas as pd
from datetime import datetime
from gensim.models import word2vec as w2v


class Corpus(object):
    def __init__(self, dir_path):
        self.dirs = dir_path
        self.len = None
        self.corpus = None
        self.sentences = None
        self.token_count = None

    def load_corpus(self):
        corpus_raw = u""
        files = glob.glob(self.dirs)
        files.sort()
        print(f"Number of files in corpus: {len(files)}")
        for f in tqdm(files):
            with codecs.open(f, "r", "utf-8") as book_file:
                corpus_raw += book_file.read()
        self.corpus = corpus_raw

    def make_sentences(self, delim=". "):
        if self.corpus is None:
            print("Error: no corpus object found, use load_corpus function to generate corpus object")
            return
        raw_sentences = self.corpus.split(delim)
        sentences = []
        for raw_sentence in tqdm(raw_sentences):
            if len(raw_sentence) > 0:
                sentences.append(raw_sentence.split())
        self.sentences = sentences
        self.token_count = sum([len(sentence) for sentence in sentences])


def main(args):
    out_dir = os.path.join(args.output, args.alias)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        filename=os.path.join(out_dir, f"{args.alias}.log"), level=logging.INFO)
    corpus = Corpus(args.input)
    corpus.load_corpus()
    corpus.make_sentences()
    seed = 1
    if args.workers is None:
        args.workers = multiprocessing.cpu_count()
    gene2vec = w2v.Word2Vec(
        sg=1,
        seed=seed,
        workers=args.workers,
        vector_size=args.size,  
        min_count=args.minTF,
        window=args.window,
        sample=args.sample
    )
    gene2vec.build_vocab(corpus.sentences)
    print("Gene2Vec vocabulary length:", len(gene2vec.wv.key_to_index))  
    gene2vec.train(corpus.sentences,
                   total_examples=gene2vec.corpus_count, epochs=args.epochs)
    # save model
    gene2vec.save(os.path.join(out_dir, f"{args.alias}.w2v"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument('--window', default=5, type=int, help='window size')
    parser.add_argument('--size', default=320, type=int, help='vector size')
    parser.add_argument('--workers', required=False, type=int, help='number of processes')
    parser.add_argument('--epochs', default=5, type=int, help='number of epochs')
    parser.add_argument('--minTF', default=1, type=int, help='minimum term frequency')
    parser.add_argument('--sample', default=1e-3, type=float, help='down sampling setting for frequent words')  
    parser.add_argument('--model', required=False, type=str, help='model file if exists')
    parser.add_argument('--input', default='/root/fsas/ESM-G2V/Data/Example/KO_identifiers/genomo_text/*.txt',
                        type=str, help='dir to learn from, as a regex for file generation')
    parser.add_argument('--output', default='/root/fsas/Experiment5/Predict',
                        type=str, help='output folder for results')
    parser.add_argument('--alias', default='G2V', type=str, help='model running alias that will be used for model tracking')
    params = parser.parse_args()
    main(params)