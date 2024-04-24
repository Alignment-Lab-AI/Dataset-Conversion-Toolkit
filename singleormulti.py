import argparse
import json
import os
import glob
import pandas as pd
from datasets import load_dataset

def convert_to_single_turn(data, config):
    print("Starting conversion to single turn...")
    for item in data:
        if 'conversations' in item or 'conversation' in item:
            conversations = item.get('conversations') or item.get('conversation')
            for i in range(len(conversations) - 1):
                yield {
                    'instruction': conversations[i].get('value', ''),
                    'input': '',
                    'output': conversations[i + 1].get('value', '')
                }
        else:
            format_type = detect_format(item, config)
            if format_type is None:
                format_type = add_format(item, config)
            mappings = config['mappings'][format_type]['mappings']
            extra_keys = [key for key in item.keys() if key not in [mappings['instruction'], mappings['output']]]
            yield {
                'instruction': item.get(mappings['instruction'], ''),
                'input': ' '.join(str(item.get(key, '')) for key in extra_keys),
                'output': item.get(mappings['output'], '')
            }
    print("Conversion to single turn completed.")

def convert_to_multi_turn(data, config):
    print("Starting conversion to multi turn...")
    for item in data:
        if 'conversations' in item or 'conversation' in item:
            conversations = item.get('conversations') or item.get('conversation')
            yield {'conversations': [
                {'from': 'human' if turn.get('from', '').lower() in ['user', 'human'] else 'gpt', 'value': turn.get('value', '')}
                for turn in conversations if 'value' in turn
            ]}
        else:
            format_type = detect_format(item, config)
            if format_type is None:
                format_type = add_format(item, config)
            mappings = config['mappings'][format_type]['mappings']
            instruction = item.get(mappings['instruction'], '')
            output = item.get(mappings['output'], '')
            if instruction and output:
                yield {'conversations': [
                    {'from': 'human', 'value': instruction},
                    {'from': 'gpt', 'value': output}
                ]}
    print("Conversion to multi turn completed.")

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

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dir', help='Path to the directory containing dataset files.')
    group.add_argument('--file', help='Path to the single file.')
    group.add_argument('--repo', help='Huggingface repo name.')
    parser.add_argument('--single', action='store_true', help='Convert to single turn format.')
    parser.add_argument('--multi', action='store_true', help='Convert to multi turn format.')
    args = parser.parse_args()

    with open('configurations.json', 'r') as config_file:
        config = json.load(config_file)

    if args.dir:
        files = glob.glob(os.path.join(args.dir, '*'))
        output_file = "formatted_data.jsonl"
    elif args.file:
        files = [args.file]
        output_file = os.path.splitext(os.path.basename(args.file))[0] + '.jsonl'
    else:
        dataset = load_dataset(args.repo, split='train')
        data = [item for item in dataset]
        output_file = "formatted_data.jsonl"

    if args.dir or args.file:
        data = []
        for file_path in files:
            if file_path.endswith('.parquet'):
                data.extend(pd.read_parquet(file_path).to_dict('records'))
            else:
                with open(file_path, 'r') as file:
                    data.extend(json.loads(line) for line in file)

    if args.single:
        formatted_data = convert_to_single_turn(data, config)
    else:
        formatted_data = convert_to_multi_turn(data, config)

    output_path = os.path.join(os.getcwd(), output_file)
    with open(output_path, 'w') as out_file:
        for item in formatted_data:
            out_file.write(json.dumps(item) + '\n')

    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
