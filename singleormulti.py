import argparse
import json
import os
import glob
from datasets import load_dataset
from multiprocessing import cpu_count

def convert_to_multi_turn(data, config):
    print("Starting conversion to multi turn...")
    formatted_data = []
    for item in data:
        if 'conversations' in item or 'conversation' in item:
            conversations = item.get('conversations') or item.get('conversation')
            formatted_conversations = []
            start_index = 0
            if conversations[0].get('from', '').lower() == 'system':
                formatted_conversations.append({'from': 'system', 'value': conversations[0].get('value', '')})
                start_index = 1
            for i in range(start_index, len(conversations)):
                if 'value' in conversations[i]:
                    formatted_conversations.append({'from': 'human' if (i - start_index) % 2 == 0 else 'gpt', 'value': conversations[i].get('value', '')})
            formatted_data.append({'conversations': formatted_conversations})
        else:
            format_type = detect_format(item, config)
            if format_type is None:
                format_type = add_format(item, config)
            mappings = config['mappings'][format_type]['mappings']
            instruction = item.get(mappings['instruction'], '')
            output = item.get(mappings['output'], '')
            extra_keys = [key for key in item.keys() if key not in [mappings['instruction'], mappings['output']]]
            if extra_keys:
                formatted_data.append({
                    'conversations': [
                        {'from': 'system', 'value': ' '.join(str(item.get(key, '')) for key in extra_keys)},
                        {'from': 'human', 'value': instruction},
                        {'from': 'gpt', 'value': output}
                    ]
                })
            else:
                formatted_data.append({
                    'conversations': [
                        {'from': 'human', 'value': instruction},
                        {'from': 'gpt', 'value': output}
                    ]
                })
    print("Conversion to multi turn completed.")
    return formatted_data

def detect_format(item, config):
    for format_type, format_data in config['mappings'].items():
        if all(key in item for key in format_data['keys']):
            return format_type
    return None

def add_format(item, config):
    keys = list(item.keys())
    instruction = 'instruction' if 'instruction' in keys else input("Enter the instruction key: ")
    output = 'output' if 'output' in keys else input("Enter the output key: ")
    extra = [key for key in keys if key not in [instruction, output]]
    format_type = input("Enter a unique name for the new format: ")
    config['mappings'][format_type] = {
        'keys': keys,
        'mappings': {
            'instruction': instruction,
            'output': output,
            'extra': extra
        }
    }
    with open('configurations.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
    print("New format added.")
    return format_type

def process_file(file_path, config, args):
    dataset = load_dataset(file_path)
    
    if args.multi:
        formatted_data = dataset.map(lambda x: convert_to_multi_turn(x, config), num_proc=cpu_count())
    else:
        formatted_data = dataset
    
    return formatted_data

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dir', help='Path to the directory containing dataset files.')
    group.add_argument('--file', help='Path to a text file with a repo/path on each new line.')
    group.add_argument('--repo', help='Huggingface repo name.')
    parser.add_argument('--single', action='store_true', help='Convert to single turn format.')
    parser.add_argument('--multi', action='store_true', help='Convert to multi turn format.')
    args = parser.parse_args()

    with open('configurations.json', 'r') as config_file:
        config = json.load(config_file)

    if args.dir:
        files = glob.glob(os.path.join(args.dir, '*'))
        output_file = "formatted_data.parquet"
    elif args.file:
        with open(args.file, 'r') as f:
            repo_list = [line.strip() for line in f]
        data = []
        for repo in repo_list:
            try:
                dataset = load_dataset(repo)
            except ValueError as e:
                if "should be one of" in str(e):
                    available_splits = eval(str(e).split("should be one of ")[1])
                    dataset = None
                    for split in available_splits:
                        try:
                            dataset = load_dataset(repo, split=split)
                            break
                        except:
                            continue
                    if dataset is None:
                        print(f"No valid split found for {repo}. Skipping.")
                        continue
                else:
                    raise e
            for split, ds in dataset.items():
                ds.to_parquet(f"{repo.replace('/', '_')}_{split}_unprocessed.parquet")
            data.append(dataset)
        output_file = "formatted_data.parquet"
    else:
        dataset = load_dataset(args.repo)
        data = [dataset]
        output_file = "formatted_data.parquet"

    if args.dir:
        formatted_data = []
        for file_path in files:
            formatted_data.append(process_file(file_path, config, args))
    else:
        if args.multi:
            formatted_data = data[0].map(lambda x: convert_to_multi_turn(x, config), num_proc=cpu_count())
            for dataset in data[1:]:
                for split, ds in dataset.items():
                    formatted_data = formatted_data.concatenate(ds.map(lambda x: convert_to_multi_turn(x, config), num_proc=cpu_count()))
        else:
            formatted_data = data[0] 
            for dataset in data[1:]:
                for split, ds in dataset.items():
                    formatted_data = formatted_data.concatenate(ds)

    formatted_data.to_parquet(output_file)

    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()

