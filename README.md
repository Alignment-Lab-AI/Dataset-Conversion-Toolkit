# Dataset Conversion Toolkit

This toolkit provides essential utilities to process and convert various dataset formats, making them ready for machine learning training tasks. The primary features include deduplication of large datasets, conversion from Parquet to JSONL, and transformation of datasets into single-turn or multi-turn formats.

## Features

1. **Deduplication (`dedup.py`)**: 
    - Deduplicates large JSONL datasets in a memory-efficient manner by processing them in chunks.
    - Uses a set-based approach for efficient deduplication within each chunk.

2. **Parquet to JSONL Conversion (`parquet_to_jsonl.py`)**:
    - Converts Parquet files to JSONL format.
    - Efficiently processes large Parquet files by reading them in row groups and converting in batches.

3. **Dataset Formatting (`singleormulti.py`)**:
    - Converts datasets into either single-turn or multi-turn formats based on user input.
    - Can process datasets from various sources including local directories, individual files, or HuggingFace datasets.
    - If a dataset format is not recognized, the script prompts for input/output keys, saves the new format to the configuration, and remembers it for future use.
    - --single and --multi as args specify the output format chosen
      
      ```python3 singleormulti.py --single```
   
    - --repo specifies a huggingface repo
      
      ```python3 singleormulti.py --multi --repo Open-Orca/OpenOrca```
   
    - --dir specifies a directory (dont select the directory with the script or it will eat its own config file)
      
      ```python3 singleormulti.py --single --dir ./yourfolderwithdatasets```
   
    - --file specifies a specific file stored locally
      
      ```python2 singleormultipy --multi --file .dataset.jsonl```
      
## Usage

### Deduplication

Run `dedup.py` with the appropriate arguments for input, chunk size, and output directory.

### Parquet to JSONL Conversion

Run `parquet_to_jsonl.py` with the appropriate arguments for input Parquet file and output JSONL file.

### Dataset Formatting

Run `singleormulti.py` with the desired mode (single/multi) and specify the data source (repo, directory, or file).

## Configuration

The toolkit uses a `configurations.json` file to understand various dataset formats. This configuration includes:

- Identifying keys for each dataset format.
- Classification as either `single_turn` or `multi_turn`.
- Mappings to dictate how fields in the original dataset are converted to the desired output format.

Users can extend the `configurations.json` file to include new dataset formats as needed.
code should detect if the dataset isnt in a recognized format and prompt the user to select the input/output tuples
and will default to 3 turns of conversation in the case of turning single turn conversations to multiturn, otherwise preserves the turn number in the source dataset.


ONGOING ISSUES:  does not currently detect multi turn data properly if there is more than one top level key, or the top level key has any name other than 'conversations'

singleormulti script needs cleaning, currently designed to take parquets but doesnt convert them as efficiently as parquet parquet_to_jsonl.
