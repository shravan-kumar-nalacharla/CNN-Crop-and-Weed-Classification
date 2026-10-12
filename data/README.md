# Local V2 Plant Seedlings dataset

Run `python scripts/download_dataset.py` and `python scripts/verify_dataset.py` with .venv active. Download tries Kaggle API first, then public kagglehub access. A valid existing dataset is reused.

Create an API token in Kaggle Account Settings if required and store legacy kaggle.json in `%USERPROFILE%/.kaggle/` (Windows) or `~/.kaggle/` (Linux), never in Git.

Manual fallback: download the ZIP from https://www.kaggle.com/datasets/vbookshelf/v2-plant-seedlings-dataset and extract into data/raw/plant_seedlings/. Nested directories are supported. Verification fully decodes every PNG/JPG/JPEG, checks species and exact V2 counts totaling 5,539.

The Kaggle archive can contain both a flat species tree and a duplicate nonsegmentedv2 tree. The downloader copies only one complete tree. For manual extraction, retain one tree, or point --data-dir to the single nested tree; do not mix both copies. The verifier recognizes the archive's misdecoded Shepherd’s Purse apostrophe.

Expected counts: Black-grass 309; Charlock 452; Cleavers 335; Common Chickweed 713; Common Wheat 253; Fat Hen 538; Loose Silky-bent 762; Maize 257; Scentless Mayweed 607; Shepherd’s Purse 274; Small-flowered Cranesbill 576; Sugar Beet 463.

Crop (0): Maize, Common Wheat, Sugar Beet. Weed (1): remaining species. See docs/Dataset_Sources.md for CC BY-SA attribution. Raw data is excluded from Git. Allow several GB for archive, extraction and downloader cache.
