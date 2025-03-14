# Dataset Conversion Toolkit 🚀

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)

## Overview

The Dataset Conversion Toolkit is a powerful and efficient suite of utilities designed to streamline the preparation of datasets for machine learning tasks.  It focuses on providing robust, memory-efficient solutions for common data preprocessing needs, enabling you to move from raw data to training-ready formats quickly and reliably. This toolkit offers deduplication, format conversion (Parquet to JSONL), and flexible dataset restructuring for both single-turn and multi-turn conversational formats.  It's built with scalability in mind, handling large datasets that might otherwise be challenging to manage.

## Key Features ✨

*   **Deduplication (`dedup.py`):** Eliminate redundancy in your large JSONL datasets with our memory-conscious deduplication tool.  It processes data in manageable chunks, ensuring efficiency even with massive files.
*   **Parquet to JSONL Conversion (`parquet_to_jsonl.py`):** Seamlessly convert large Parquet files into the more readily consumable JSONL format.  This utility efficiently handles large files by processing data in row groups and batches.
*   **Dataset Formatting (`singleormulti.py`):**  Adapt your datasets to your specific training requirements. Transform datasets into either single-turn or multi-turn formats, suitable for a wide variety of conversational AI and instruction-following models. The script is highly flexible, supporting inputs from local directories, individual files, and Hugging Face Datasets.
*   **Extensible Configuration:**  A central `configurations.json` file defines how the toolkit understands and processes different dataset formats.  This includes:
    *   **Format Detection:** Automatically recognizes known dataset structures.
    *   **Customizable Mappings:** Define how fields in your original dataset map to the desired output format (instruction, output, etc.).
    *   **User-Friendly Format Extension:**  If a dataset format is not recognized, the script intelligently prompts you for the necessary information (input/output keys) and automatically updates the configuration for future use.

## Installation 🛠️

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/dataset-conversion-toolkit.git
    cd dataset-conversion-toolkit
    ```

2.  **Install dependencies:**
    It is highly recommended that you create a virtual environment to avoid dependency issues. To create and activate a virtual environment use these commands:
    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

    Then, install the necessary Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

    The `requirements.txt` file should contain (you'll need to create this):

    ```
    pyarrow
    datasets
    tqdm
    ```

## Usage Examples 📖

### 1. Deduplication

To deduplicate a large JSONL file named `my_large_dataset.jsonl`, processing it in chunks of 10,000 lines and saving the results to a folder named `deduplicated_output`:

```bash
python dedup.py
```

You'll be prompted to enter the input file path, chunk size, and output folder.

### 2. Parquet to JSONL Conversion

To convert all Parquet files in the current directory to JSONL, run:

```bash
python parquet_to_jsonl.py
```

This will process each `.parquet` file in the directory, creating a corresponding `.jsonl` file.  Processed Parquet files are moved to a `processed` subdirectory.

### 3. Dataset Formatting (Single-turn/Multi-turn)

#### Using a Hugging Face Dataset

To convert the `Open-Orca/OpenOrca` dataset to multi-turn format:

```bash
python singleormulti.py --multi --repo Open-Orca/OpenOrca
```

#### Using a Local Directory

To convert all dataset files in a local directory named `my_datasets` to single-turn format:

```bash
python singleormulti.py --single --dir ./my_datasets
```

#### Using a Single Local File
To process a specific jsonl dataset stored locally:

```bash
python singleormulti.py --multi --file ./my_dataset.jsonl
```

### Configuration Details

The `configurations.json` file is the heart of the toolkit's adaptability. Here's a breakdown of its structure:

```json
{
  "mappings": {
    "dataset_format_name": {
      "keys": ["list", "of", "expected", "keys"],
      "type": "single_turn" | "multi_turn",
      "mappings": {
        "instruction": "original_instruction_key",
        "output": "original_output_key",
        "extra": ["list", "of", "other", "keys", "to", "include"]
      }
    },
    ...
  },
  "descriptions": {
      "dataset_format_name": {
      "example": "example json object for the dataset",
       "description": "more detailed information about the dataset"
  }
}
```

*   **`mappings`:** This section defines how different dataset formats are interpreted.
    *   `dataset_format_name`:  A unique identifier for each dataset format (e.g., "alpaca", "sharegpt").
    *   `keys`:  A list of keys expected to be present in the dataset.
    *   `type`:  Indicates whether the format is `single_turn` or `multi_turn`.
    *   `mappings`:  Specifies how the original dataset keys map to the standardized `instruction`, `output`, and `extra` fields.
*   **`descriptions`:** Provides examples and descriptions for each supported dataset. This is primarily for documentation and understanding of the supported formats.

**Adding a New Dataset Format:**

If `singleormulti.py` encounters an unrecognized dataset format, it will guide you through the process of adding it to `configurations.json`.  You'll be prompted to:

1.  Enter a unique name for the format.
2.  Specify the key that represents the instruction.
3.  Specify the key that represents the output.

The script will then automatically update the `configurations.json` file with this new format definition.

## Troubleshooting and Known Issues 🐛

*   **Multi-turn Data Detection:** The `singleormulti.py` script currently assumes that multi-turn data has a top-level key named "conversations". It may not correctly detect multi-turn data with different structures (e.g., a different top-level key or multiple top-level keys). See [Issue #1](link-to-issue-if-it-exists).
* **Parquet Conversion Efficiency in singleormulti.py**: The `singleormulti.py` script contains basic support for processing parquet files. However it is highly recommended to use the purpose built `parquet_to_jsonl.py` for significantly faster and more memory-efficient parquet file conversions.
*   **Error Handling:**  The scripts include basic error handling, but more comprehensive error handling and logging could be added.

## Contributing 🤝

We welcome contributions to the Dataset Conversion Toolkit!  Here's how you can help:

1.  **Fork the repository.**
2.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b bugfix/your-bugfix-name`
3.  **Make your changes and commit them** with clear, descriptive commit messages.
4.  **Push your branch** to your forked repository.
5.  **Open a pull request** against the `main` branch of the original repository.


Please follow the existing code style and provide tests for any new functionality. Be sure to update this README if you add or modify any features.

## License 📄

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contact and Support 📧

If you encounter any issues or have questions, please open an issue on the GitHub repository.  We appreciate your feedback!
