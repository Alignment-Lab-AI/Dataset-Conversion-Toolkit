# Dataset Conversion Toolkit: A Comprehensive Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)

<img width="1049" alt="Screenshot 2024-01-13 at 10 34 13 PM" src="https://github.com/bananaml/dataset-conversion-toolkit/assets/87656893/1a6f55d7-a63e-447f-9e3a-e5596441887b">

## Overview

The **Dataset Conversion Toolkit** is a powerful and efficient suite of utilities designed to streamline the preprocessing and conversion of various dataset formats for machine learning tasks.  This toolkit focuses on providing high performance, ease of use, and extensibility for researchers and developers working with large datasets. It offers functionalities for deduplication, format conversion, and structuring datasets into single-turn or multi-turn conversational formats.

This toolkit draws inspiration from robust, well-regarded projects like ChromaDB, aiming to provide a similar level of quality and user experience in the context of dataset preprocessing.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Deduplication](#deduplication-deduppy)
  - [Parquet to JSONL Conversion](#parquet-to-jsonl-conversion-parquet_to_jsonlpy)
  - [Dataset Formatting (Single-turn/Multi-turn)](#dataset-formatting-singleormultipy)
- [Configuration](#configuration)
- [Extending the Toolkit](#extending-the-toolkit)
  - [Adding New Dataset Formats](#adding-new-dataset-formats)
- [Known Issues and Future Improvements](#known-issues-and-future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

The toolkit provides three core functionalities:

1.  **Deduplication (`dedup.py`):**  Efficiently remove duplicate entries from large JSONL datasets.

    -   **Memory-Efficient Processing:**  Processes data in chunks, making it suitable for datasets that are larger than available RAM.
    -   **Set-Based Deduplication:** Utilizes Python sets within each chunk for fast and efficient deduplication.
    -   **Chunk-and-Merge Strategy:**  Divides the dataset into smaller, manageable chunks, deduplicates each chunk, and then merges them while removing further duplicates.

2.  **Parquet to JSONL Conversion (`parquet_to_jsonl.py`):**  Convert Apache Parquet files to JSONL format.

    -   **Row Group Processing:**  Reads Parquet files row group by row group, enabling processing of large Parquet files without loading the entire file into memory.
    -   **Batch Conversion:**  Converts data in batches (configurable size) to further optimize memory usage.
    -   **Handles Directory Input:** Can process an entire directory of `.parquet` files, creating corresponding `.jsonl` files and moving the originals to a `processed` subdirectory.

3.  **Dataset Formatting (`singleormulti.py`):** Transform datasets into either single-turn or multi-turn conversational formats.

    -   **Flexible Input:** Supports various data sources:  local directories, individual files, and Hugging Face datasets.
    -   **Format Auto-Detection and Configuration:**  Automatically detects the format of known datasets based on a `configurations.json` file. If a format is not recognized, the script prompts the user to define the format, which is then saved for future use.
    -   **Single-Turn Format:**  Structures data into a format suitable for single-turn interactions, typically with `instruction`, `input`, and `output` fields.
    -   **Multi-Turn Format:**  Structures data into a conversational format with a list of turns, each having a `from` (role) and `value` (content) field. Supports system prompts.  Defaults to 3-turn conversations when transforming single-turn data.
    -   **Hugging Face Dataset Integration:**  Seamlessly loads datasets from Hugging Face Hub.

## Installation

Clone the repository and install the required packages:

```bash
git clone https://github.com/yourusername/dataset-conversion-toolkit.git # Replace with your repository URL
cd dataset-conversion-toolkit
pip install -r requirements.txt
```

A `requirements.txt` file should be created, containing at minimum:

```
pyarrow
datasets
tqdm
```

## Usage

The command-line interface for each script is designed for simplicity and flexibility.

### Deduplication (`dedup.py`)

```bash
python dedup.py
```

The script prompts you for the following:

-   **Input path:** The path to the large JSONL file to be deduplicated.
-   **Chunk size:** The number of lines to process per chunk (adjust based on your available memory).
-   **Output folder:** The directory where the deduplicated chunks and final merged file will be saved.

**Example:**

```
Enter the path to the large JSONL file: my_large_dataset.jsonl
Enter the preferred chunk size (number of lines per chunk): 100000
Enter the output folder for the deduplicated chunks: output_deduped
Deduplicated file saved at: output_deduped/chunk_0_merged.jsonl
```

### Parquet to JSONL Conversion (`parquet_to_jsonl.py`)

```bash
python parquet_to_jsonl.py
```
The script will process all `.parquet` files in the current directory (`./`).

- Converts each `.parquet` file to a `.jsonl` file with the same name in the same directory.
- Moves the processed `.parquet` files to a subdirectory named `processed`.
- Prints progress updates to the console.

**Example:**
If the directory contains `data1.parquet` and `data2.parquet`, after running the script, the directory will contain:
- `data1.jsonl`
- `data2.jsonl`
- `processed/data1.parquet`
- `processed/data2.parquet`

### Dataset Formatting (`singleormulti.py`)

This script provides options for converting datasets to single-turn or multi-turn formats and supports different input sources.

**Command-line Arguments:**

-   `--dir`:  Specify a directory containing dataset files (mutually exclusive with `--file` and `--repo`).
-   `--file`: Specify a path to a single dataset file (mutually exclusive with `--dir` and `--repo`).
-   `--repo`:  Specify a Hugging Face repository name (mutually exclusive with `--dir` and `--file`).
-   `--single`: Convert to single-turn format.
-   `--multi`: Convert to multi-turn format.

**Examples:**

1.  **Convert a directory of files to multi-turn format:**

    ```bash
    python singleormulti.py --dir ./my_datasets --multi
    ```

2.  **Convert a single file to single-turn format:**

    ```bash
    python singleormulti.py --file ./my_dataset.jsonl --single
    ```

3.  **Convert a Hugging Face dataset to multi-turn format:**

    ```bash
    python singleormulti.py --repo Open-Orca/OpenOrca --multi
    ```
4. **Convert a text file of HuggingFace repo paths to single turn format:**
    ```bash
      python singleormulti.py --file ./huggingface_repos.txt --single
      ```
      Where `huggingface_repos.txt` contains:
      ```
      repo/path/one
      repo/path/two
      ...etc...
      ```
**Interactive Format Detection:**

If `singleormulti.py` encounters a dataset format it doesn't recognize (based on `configurations.json`), it will interactively prompt you to define the format:

```
Enter a unique name for the new format: my_new_format
Enter the instruction key: prompt
Enter the output key: completion
New format added.
```

This information is then saved to `configurations.json`, allowing the script to automatically handle this format in the future.

## Configuration

The `configurations.json` file is the heart of the dataset format detection and mapping system in `singleormulti.py`.  It allows the toolkit to understand the structure of various datasets and how to transform them into the desired output formats.

**Structure:**

The file consists of two main sections: `mappings` and `descriptions`.

-   **`mappings`:**  This section defines the core logic for format recognition and conversion.  Each key in `mappings` represents a unique dataset format (e.g., "alpaca", "sharegpt").  For each format, the following information is provided:
    -   `keys`:  A list of keys that *must* be present in a data item for it to be recognized as belonging to this format.
    -   `type`:  Either `"single_turn"` or `"multi_turn"`, indicating the inherent structure of the dataset.
    -   `mappings`:  A dictionary that maps fields in the original dataset to the corresponding fields in the output format (`instruction`, `output`, `extra`). The `extra` field is a list, allowing for multiple fields to be concatenated in the system prompt for multi-turn conversion.
-  **`descriptions`:** This section is primarily for documentation and provides human-readable explanations of each dataset format. The `example` helps illustrate the dataset's structure, and the `description` details how `mappings` works.

**Example (`configurations.json` snippet):**

```json
{
  "mappings": {
    "alpaca": {
      "keys": ["instruction", "input", "output"],
      "type": "single_turn",
      "mappings": {
        "instruction": "instruction",
        "output": "output",
        "extra": ["input"]
      }
    },
    "sharegpt": {
      "keys": ["conversations"],
      "type": "multi_turn",
      "mappings": {
        "from": "role",
        "value": "value"
      }
    }
  },
  "descriptions": {
     "alpaca": {
        "example": "{\"instruction\": \"...\", \"input\": \"...\", \"output\": \"...\"}",
        "description": "Type: single_turn. Mappings: instruction maps to instruction, output maps to output, and input is considered as an extra field."
      }
  }
}
```

## Extending the Toolkit

### Adding New Dataset Formats

To add support for a new dataset format, you need to modify the `configurations.json` file.  Here's a step-by-step guide:

1.  **Identify the Key Fields:** Determine the key fields that uniquely identify your dataset.  For example, if your dataset has fields like `prompt`, `answer`, and `context`, these might be your key fields.

2.  **Determine the Dataset Type:** Decide whether your dataset is inherently single-turn or multi-turn.

3.  **Define the Mappings:**  Create a new entry in the `mappings` section of `configurations.json`.  Use a unique name for your dataset format (e.g., `my_new_format`).  Specify the `keys`, `type`, and `mappings` according to the structure of your dataset.

4. **Add a Description (Optional but Recommended):** Add a corresponding entry in the `descriptions` section to provide a human-readable explanation of your new format.

**Example:** Let's say you have a new dataset format with the following structure:

```json
{
  "user_query": "What is the capital of France?",
  "system_response": "The capital of France is Paris.",
  "supporting_context": "France is a country in Europe."
}
```

You would add the following to `configurations.json`:

```json
{
  "mappings": {
    "my_new_format": {
      "keys": ["user_query", "system_response", "supporting_context"],
      "type": "single_turn",
      "mappings": {
        "instruction": "user_query",
        "output": "system_response",
        "extra": ["supporting_context"]
      }
    }
  },
  "descriptions":{
    "my_new_format": {
          "example": "{\"user_query\": \"What is the capital of France?\", \"system_response\": \"The capital of France is Paris.\", \"supporting_context\": \"France is a country in Europe.\"}",
          "description": "Type: single_turn. user_query maps to instruction, system_response to output, and supporting_context is an extra field."
        }

  }
}
```

## Known Issues and Future Improvements

- **Multi-turn Detection Limitations:** The `singleormulti.py` script currently has limitations in detecting multi-turn data. It primarily relies on the presence of a top-level key named 'conversations'.  If multi-turn data has a different top-level key or multiple top-level keys, it might not be detected correctly.  Future improvements should address this by implementing more robust multi-turn detection logic. It could also benefit from multi-processing for larger datasets.
- **Parquet Conversion Efficiency:** While `parquet_to_jsonl.py` is efficient, it could be further optimized, particularly for extremely large Parquet files.  Exploring alternative libraries or techniques for Parquet processing might yield performance gains.
- **Error Handling:** The scripts could benefit from more comprehensive error handling and input validation.
- **Testing:**  Adding unit tests would significantly improve the robustness and maintainability of the toolkit.
- **Documentation:** Expanding the documentation, including a contribution guide would make the toolkit easier to maintain.
- **Refactoring:** The scripts, especially `singleormulti.py`, could benefit from some code refactoring to improve readability and maintainability. Consider breaking down large functions into smaller, more manageable units.

## Contributing

Contributions to the Dataset Conversion Toolkit are welcome! Please see the `CONTRIBUTING.md` file (to be created) for guidelines on how to contribute.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgements

- This project was inspired by the design and functionality of well-established projects like ChromaDB.
- Thanks to the developers of the libraries used in this toolkit, including `pyarrow`, `datasets`, and `tqdm`.
