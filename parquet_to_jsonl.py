import os
import pyarrow.parquet as pq
import json

def parquet_to_jsonl(input_file, output_file, batch_size=5000):
    parquet_file = pq.ParquetFile(input_file)
    
    total_rows_processed = 0
    
    with open(output_file, 'w') as output:
        for i in range(parquet_file.num_row_groups):
            table = parquet_file.read_row_group(i)
            df = table.to_pandas()
            
            for start_idx in range(0, len(df), batch_size):
                end_idx = start_idx + batch_size
                batch = df.iloc[start_idx:end_idx]
                
                for _, row in batch.iterrows():
                    output.write(json.dumps(row.to_dict()) + '\n')
                    total_rows_processed += 1
                    
                    if total_rows_processed % batch_size == 0:
                        print(f"Written {total_rows_processed} rows to {output_file}")

def process_all_parquets(directory):
    processed_dir = os.path.join(directory, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    parquet_files = [f for f in os.listdir(directory) if f.endswith('.parquet') and os.path.isfile(os.path.join(directory, f))]
    
    for idx, parquet_file in enumerate(parquet_files):
        print(f"Processing file {idx+1}/{len(parquet_files)}: {parquet_file}")
        input_path = os.path.join(directory, parquet_file)
        output_path = os.path.join(directory, parquet_file.replace('.parquet', '.jsonl'))
        
        parquet_to_jsonl(input_path, output_path)
        
        os.rename(input_path, os.path.join(processed_dir, parquet_file))

# Usage
directory_path = './'
process_all_parquets(directory_path)
