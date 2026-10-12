"""Kaggle API first, public kagglehub fallback, then explicit manual instructions."""
import shutil
from pathlib import Path
from dataset import DATA, SPECIES, inspect_dataset, normalize, species_root

def copy_one_tree(source):
    canonical = species_root(source)
    print(f'Using one canonical species tree: {canonical}', flush=True)
    names = {normalize(p.name): p for p in canonical.iterdir() if p.is_dir()}
    for name in SPECIES:
        folder = names[normalize(name)]
        destination = DATA / name
        existing = next((p for p in DATA.iterdir() if p.is_dir() and normalize(p.name)==normalize(name)), None)
        if existing is not None:
            destination = existing
        destination.mkdir(exist_ok=True)
        for image in folder.rglob('*'):
            if image.is_file():
                target = destination / image.relative_to(folder)
                target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists() or target.stat().st_size != image.stat().st_size:
                    shutil.copy2(image,target)

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        inspect_dataset(DATA)
        print('Valid dataset already exists; download skipped.')
        print(f'Final dataset path: {DATA.resolve()}')
        return
    except ValueError:
        pass
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi(); api.authenticate()
        staging = DATA.parent / 'kaggle_extraction'
        staging.mkdir(exist_ok=True)
        api.dataset_download_files('vbookshelf/v2-plant-seedlings-dataset', path=str(staging), unzip=True)
        copy_one_tree(staging)
    except (Exception, SystemExit) as e:
        print(f'Kaggle API unavailable: {type(e).__name__}. To authenticate, create an API token in Kaggle Account Settings and save kaggle.json in ~/.kaggle/ (never in Git).')
        try:
            import kagglehub
            cached = Path(kagglehub.dataset_download('vbookshelf/v2-plant-seedlings-dataset'))
            copy_one_tree(cached)
        except Exception as fallback:
            raise RuntimeError('Automatic download failed. Download ZIP from https://www.kaggle.com/datasets/vbookshelf/v2-plant-seedlings-dataset and extract into ' + str(DATA) + '; then run python scripts/verify_dataset.py') from fallback
    inspect_dataset(DATA)
    print(f'Final dataset path: {DATA.resolve()}')

if __name__ == '__main__':
    main()
