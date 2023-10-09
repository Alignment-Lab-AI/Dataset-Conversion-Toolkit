import argparse
import json
import os
import glob
import pandas as pd
from datasets import load_dataset

def convert_to_single_turn(data, config):
    print("Starting conversion to single turn...")
    formatted_data = []
    for item in data:
        print("Processing item...")
        def detect_format(item, config):
            print("Detecting format...")
            for format_type, format_data in config['mappings'].items():
                if all(key in item for key in format_data['keys']):
                    return format_type
            return None

        format_type = detect_format(item, config)
        if format_type is None:
            print("Format not found, adding new format...")
            format_type = add_format(item, config)
        mappings = config['mappings'][format_type]['mappings']
        if 'conversations' in item:
            print("Processing conversations...")
            conversation_list = item['conversations']
            for i in range(len(conversation_list) - 1):
                new_item = {
                    'instruction': conversation_list[i].get('value'),
                    'input': "",
                    'output': conversation_list[i + 1].get('value')
                }
                formatted_data.append(new_item)
                yield new_item  # Yielding the item for memory efficiency
        elif 'source' in item and 'conversation' in item:
            print("Processing source and conversation...")
            item['conversations'] = item.pop('conversation')
            del item['source']
            conversation_list = item['conversations']
            for i in range(len(conversation_list) - 1):
                new_item = {
                    'instruction': conversation_list[i].get('value'),
                    'input': "",
                    'output': conversation_list[i + 1].get('value')
                }
                formatted_data.append(new_item)
                yield new_item  # Yielding the item for memory efficiency
        else:
            print("Processing non-conversation item...")
            extra_keys = [key for key in item.keys() if key not in [mappings.get('instruction'), mappings.get('output')]]
            input_value = ' '.join(str(item.get(key, '') or '') for key in extra_keys) if extra_keys else ''
            new_item = {
                'instruction': item.get(mappings.get('instruction'), ''),
                'input': input_value,
                'output': item.get(mappings.get('output'), '')
            }
            formatted_data.append(new_item)
            yield new_item  # Yielding the item for memory efficiency

    print("Conversion to single turn completed.")
    return formatted_data


def detect_format(item, config):
    print("Detecting format...")
    for format_type, format_data in config['mappings'].items():
        if all(key in item for key in format_data['keys']):
            return format_type
    return None

def convert_to_multi_turn(data, config):
    print("Starting conversion to multi turn...")
    formatted_data = []
    buffer = []
    for item in data:
        print("Processing item...")
        format_type = detect_format(item, config)
        if format_type is None:
            print("Format not found, adding new format...")
            format_type = add_format(item, config)
        mappings = config['mappings'][format_type]['mappings']
        value_key = mappings.get('value', 'value')  # defaulting to 'value' if not found in configuration
        if 'conversations' in item:
            print("Processing conversations...")
            new_conversations = []
            for conversation in item['conversations']:
                new_value = conversation.get(value_key, '')
                if new_value:  # ensuring the value is non-empty
                    new_conversations.append({
                        'from': 'human' if conversation.get('from', '').lower() in ['user', 'human'] else 'gpt',
                        value_key: new_value
                    })
            if new_conversations:  # ensuring the conversation is non-empty
                formatted_data.append({'conversations': new_conversations})
                yield {'conversations': new_conversations}  # Yielding the item for memory efficiency
        elif 'source' in item and 'conversation' in item:
            print("Processing source and conversation...")
            item['conversations'] = item.pop('conversation')
            del item['source']
            new_conversations = []
            for conversation in item['conversations']:
                new_value = conversation.get(value_key, '')
                if new_value:  # ensuring the value is non-empty
                    new_conversations.append({
                        'from': 'human' if conversation.get('from', '').lower() in ['user', 'human'] else 'gpt',
                        value_key: new_value
                    })
            if new_conversations:  # ensuring the conversation is non-empty
                formatted_data.append({'conversations': new_conversations})
                yield {'conversations': new_conversations}  # Yielding the item for memory efficiency
        else:
            print("Processing non-conversation item...")
            instruction = item.get(mappings.get('instruction'), '')
            output = item.get(mappings.get('output'), '')
            if instruction and output:  # ensuring both instruction and output are non-empty
                buffer.append({'from': 'human', value_key: instruction})
                buffer.append({'from': 'gpt', value_key: output})
                if len(buffer) // 2 == 3:
                    formatted_data.append({'conversations': buffer.copy()})
                    yield {'conversations': buffer.copy()}  # Yielding the item for memory efficiency
                    buffer.clear()
    if buffer:
        formatted_data.append({'conversations': buffer})
        yield {'conversations': buffer}  # Yielding the item for memory efficiency
    print("Conversion to multi turn completed.")
    return formatted_data

def add_format(item, config):
    print("Adding new format...")
    keys = list(item.keys())
    print(f"Available keys in the item: {keys}")
    instruction = 'instruction' if 'instruction' in keys else input("Enter the instruction key: ")
    output = 'output' if 'output' in keys else input("Enter the output key: ")
    extra = [key for key in keys if key not in [instruction, output]]
    print(f"Available keys for extra: {extra}")
    selected_extras = input("Enter one or multiple keys for extra, separated by comma: ").split(', ')
    extra = [key for key in extra if key in selected_extras]
    format_type = input("Enter a unique name for the new format: ")
    try:
        config['mappings'][format_type] = {
            'keys': keys,
            'mappings': {
                'instruction': instruction,
                'output': output,
                'extra': extra
            }
        }
    except TypeError as e:
        print(f"An error occurred: {str(e)}. Please ensure that the selected keys are string values.")
        return None
    with open('configurations.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
    print("New format added.")
    return config['mappings'][format_type]['mappings']


def main():
    try:
        print("Starting main function...")
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--dir', help='Path to the directory containing dataset files.', default=os.getcwd())
        group.add_argument('--file', help='Path to the single file.')
        group.add_argument('--repo', help='Huggingface repo name.')
        parser.add_argument('--single', action='store_true', help='Convert to single turn format.')
        parser.add_argument('--multi', action='store_true', help='Convert to multi turn format.')
        args = parser.parse_args()

        with open('configurations.json', 'r') as config_file:
            print("Loading configurations...")
            config = json.load(config_file)

            if args.dir:
                print("Processing directory...")
                directory_path = args.dir  # directly using the directory name
                if not os.path.exists(directory_path):
                    print(f"Directory '{args.dir}' not found.")
                    exit()
                files = glob.glob(os.path.join(directory_path, '*'))
                # If the input was a directory, use a default name for the output file.
                output_file = "formatted_data.jsonl"
                # Ensure the directory exists
                output_dir = os.getcwd()  # Change to script directory
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                output_path = os.path.join(output_dir, output_file)
                # Open the output file once, outside the loop
                with open(output_path, 'w') as out_file:
                    for file_path in files:
                        print(f"Processing file: {file_path}")
                        if file_path.endswith('.parquet'):
                            data = pd.read_parquet(file_path).to_dict('records')
                        else:
                            with open(file_path, 'r') as file:
                                try:
                                    data = []
                                    for line in file:
                                        data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    print("Error decoding JSON.")
                        if args.single:
                            formatted_data = convert_to_single_turn(data, config)
                        elif args.multi:
                            formatted_data = convert_to_multi_turn(data, config)
                        # Write each formatted data to the output file
                        for item in formatted_data:
                            out_file.write(json.dumps(item) + '\n')  # Each item on a new line
                print(f"Data saved to {output_path}")
            elif args.file:
                print("Processing single file...")
                file_path = args.file
                print(f"Processing file: {file_path}")
                if file_path.endswith('.parquet'):
                    data = pd.read_parquet(file_path).to_dict('records')
                else:
                    with open(file_path, 'r') as file:
                        try:
                            data = []
                            for line in file:
                                data.append(json.loads(line))
                        except json.JSONDecodeError:
                            print("Error decoding JSON.")
                if args.single:
                    formatted_data = convert_to_single_turn(data, config)
                elif args.multi:
                    formatted_data = convert_to_multi_turn(data, config)

                # If the input was a file, use its name for the output. Otherwise, use a default name.
                output_file = os.path.splitext(os.path.basename(file_path))[0] + '.jsonl' if args.file else "formatted_data.jsonl"

                # Ensure the directory exists
                output_dir = os.getcwd()  # Change to script directory
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                output_path = os.path.join(output_dir, output_file)

                # Save data to the output file
                with open(output_path, 'w') as out_file:
                    for item in formatted_data:
                        out_file.write(json.dumps(item) + '\n')  # Each item on a new line

                print(f"Data saved to {output_path}")
            elif args.repo:
                print("Processing Huggingface repo...")
                dataset = load_dataset(args.repo, split='train')
                data = [item for item in dataset]

                if args.single:
                    formatted_data = convert_to_single_turn(data, config)
                elif args.multi:
                    formatted_data = convert_to_multi_turn(data, config)

                # If the input was a file, use its name for the output. Otherwise, use a default name.
                output_file = "formatted_data.jsonl"

                output_path = os.path.join(os.getcwd(), output_file)  # Change to script directory

                # Save data to the output file
                with open(output_path, 'w') as out_file:
                    for item in formatted_data:
                        out_file.write(json.dumps(item) + '\n')  # Each item on a new line

                print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
