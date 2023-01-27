from itertools import product
from pathlib import Path
import re, os, time
import argparse

def recursive_conversation(kind, file_index):
    '''
    im basically dicking around overcomplicating a simple y/n question
    '''
    inp = input('continue? [y]/n\n')
    if inp == 'n':
        return False
    elif inp not in ['y', '']:
        return recursive_conversation(kind, file_index)
    return True



parser = argparse.ArgumentParser()
parser.add_argument('filename', nargs='?', default=None)
args = parser.parse_args()

if args.filename is None:
    files = [
        re.search("history_(\d+).json", s.name).group(1)
        for s in sorted(Path('./movement_data').glob('history_*.json'))
    ]
else:
    files = [args.filename]

for kind, file_index in product(
    ['points','linear','quadratic','cubic','mimic'],
    files
):
    command = f'python ./controller.py {kind} --file_index {file_index}'
    print(f'{command = }')
    os.system(command)
    if not recursive_conversation(kind, file_index):
        break
    time.sleep(1)
