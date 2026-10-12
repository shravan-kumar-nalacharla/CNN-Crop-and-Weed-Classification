import argparse
from dataset import DATA, inspect_dataset

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default=str(DATA))
    args = parser.parse_args()
    inspect_dataset(args.data_dir)
