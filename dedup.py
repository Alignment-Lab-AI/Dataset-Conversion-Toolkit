import json
import os
from tqdm import tqdm

def dedup_chunk(input_path, chunk_size, output_folder):
    """
    Reads the input JSONL file in chunks, deduplicates each chunk and writes to a new file.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    chunk_files = []
    with open(input_path, 'r') as f:
        chunk = []
        count = 0
        for line in tqdm(f, desc="Processing chunks"):
            chunk.append(line)
            if len(chunk) >= chunk_size:
                # Deduplicate
                deduped_chunk = list(set(chunk))
                # Write to a new file
                output_path = os.path.join(output_folder, f"chunk_{count}.jsonl")
                with open(output_path, 'w') as out_f:
                    out_f.writelines(deduped_chunk)
                chunk_files.append(output_path)
                chunk = []
                count += 1
        
        # Handle the last chunk
        if chunk:
            deduped_chunk = list(set(chunk))
            output_path = os.path.join(output_folder, f"chunk_{count}.jsonl")
            with open(output_path, 'w') as out_f:
                out_f.writelines(deduped_chunk)
            chunk_files.append(output_path)
    
    return chunk_files

def merge_dedup_files(fileA, fileB):
    """
    Merges two files while deduplicating.
    """
    output_file = fileA.replace(".jsonl", "_merged.jsonl")
    seen = set()
    
    with open(output_file, 'w') as out_f:
        # Process fileA
        with open(fileA, 'r') as fA:
            for line in fA:
                seen.add(line)
                out_f.write(line)
        
        # Process fileB
        with open(fileB, 'r') as fB:
            for line in fB:
                if line not in seen:
                    out_f.write(line)
    
    # Delete original files
    os.remove(fileA)
    os.remove(fileB)
    
    return output_file

def deduplicate_large_jsonl(input_path, chunk_size, output_folder):
    """
    Deduplicates a large JSONL file using the chunking and merging method.
    """
    # Step 1: Chunking & Dedup within each chunk
    chunk_files = dedup_chunk(input_path, chunk_size, output_folder)
    
    # Step 2: Merge & Dedup
    while len(chunk_files) > 1:
        merged_files = []
        for i in tqdm(range(0, len(chunk_files), 2), desc="Merging chunks"):
            if i+1 < len(chunk_files):
                merged_file = merge_dedup_files(chunk_files[i], chunk_files[i+1])
                merged_files.append(merged_file)
            else:
                merged_files.append(chunk_files[i])
        chunk_files = merged_files
    
    return chunk_files[0]

if __name__ == "__main__":
    input_path = input("Enter the path to the large JSONL file: ")
    chunk_size = int(input("Enter the preferred chunk size (number of lines per chunk): "))
    output_folder = input("Enter the output folder for the deduplicated chunks: ")

    final_file = deduplicate_large_jsonl(input_path, chunk_size, output_folder)
    print(f"Deduplicated file saved at: {final_file}")

