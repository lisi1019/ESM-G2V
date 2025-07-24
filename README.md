<<<<<<< HEAD
# ESM-G2V

 A dual-input deep learning tool  for protein function annotation, combining sequence-based features(via ESM embeddings) and genomic context features (via Gene2Vec embeddings). Predicts  KEGG Orthology (KO) terms by jointly modeling protein sequences and their genomic neighborhoods, enabling accurate metabolic pathway inference.

## Getting the data

The raw data needed for the experiment is stored in the dataset.


## Setting up the working environment
First, set up python environment and dependencies. 
#### using pip
```
python3 -m venv g2v-env
source g2v-env/bin/activate
pip install -r requirements.txt
```
#### using conda

```
conda env create -f environment.yml
conda activate g2v-env
```

The setup was tested on Python 3.7.
Versions of all required programs appear in `requirements.txt` (for pip) and `environment.yml` (for conda).

## Use of tools for forecasting

Run the following command:
'''snakemake --cores 8 --snakefile /root/fsas/ESM-G2V/snakemake/Snakemakefile --forceall'''

Run this command under this path:
/root/fsas/ESM-G2V/Data/Example/KO_identifiers

## Function classification model validation

To retrain and validate the model, run the following command:
'''python classify.py --model PATH_TO_MERGE_MDL --output PATH_TO_OUT_DIR --metadata PATH_TO_METADATA'''

The metadata file can be found in metadata.csv and The Merge_MDL can be found in merged_data.txt.


=======
# ESM-G2V
>>>>>>> a8dc0e745d83f2164c71b702a7edb6af8569f796
