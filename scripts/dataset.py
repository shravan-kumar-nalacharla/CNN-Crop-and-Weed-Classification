"""Strict, recursive V2 dataset inspection shared by training and download tools."""
from pathlib import Path
import unicodedata
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/raw/plant_seedlings'
CROPS = {'Maize', 'Common Wheat', 'Sugar Beet'}
SPECIES = ['Black-grass', 'Charlock', 'Cleavers', 'Common Chickweed', 'Common Wheat',
           'Fat Hen', 'Loose Silky-bent', 'Maize', 'Scentless Mayweed',
           "Shepherd’s Purse", 'Small-flowered Cranesbill', 'Sugar Beet']
EXPECTED = [309, 452, 335, 713, 253, 538, 762, 257, 607, 274, 576, 463]

def normalize(s):
    # The public ZIP sometimes decodes its UTF-8 apostrophe through CP437.
    return unicodedata.normalize('NFKC', s).replace('ΓÇÖ', "'").replace('â€™', "'").replace('’', "'").casefold().strip()

def species_root(path):
    """Select one complete tree when an archive includes duplicate nested copies."""
    expected = {normalize(s) for s in SPECIES}
    candidates = []
    for parent in [Path(path), *[p for p in Path(path).rglob('*') if p.is_dir()]]:
        children = {normalize(p.name) for p in parent.iterdir() if p.is_dir()}
        if expected.issubset(children):
            candidates.append(parent)
    if not candidates:
        raise ValueError(f'No complete 12-species folder tree found under {path}')
    return min(candidates, key=lambda p: (len(p.parts), str(p)))

def inspect_dataset(path=DATA, strict=True):
    path = Path(path).resolve()
    lookup = {normalize(s): s for s in SPECIES}
    records, errors = [], []
    for p in sorted(path.rglob('*')):
        if p.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
            continue
        species = next((lookup[normalize(q)] for q in reversed(p.parts[:-1]) if normalize(q) in lookup), None)
        if species is None:
            errors.append(f'Unknown species: {p}'); continue
        try:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                im.convert('RGB').load()
        except Exception as e:
            errors.append(f'Unreadable {p}: {e}'); continue
        records.append({'path': str(p), 'relative_path': p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),
                        'species': species, 'label': int(species not in CROPS)})
        if len(records) % 500 == 0:
            print(f'Validated {len(records)} images...', flush=True)
    df = pd.DataFrame(records, columns=['path', 'relative_path', 'species', 'label'])
    counts = df.species.value_counts().reindex(SPECIES, fill_value=0)
    print(f'Dataset: {path}\nImages: {len(df)}\nSpecies: {(counts > 0).sum()}\n{counts.to_string()}')
    if strict:
        if counts.tolist() != EXPECTED:
            errors.append('Incomplete or unexpected V2 extraction: expected 5539 images and exact published species counts.')
        if errors:
            raise ValueError('\n'.join(errors[:20]))
    return df
