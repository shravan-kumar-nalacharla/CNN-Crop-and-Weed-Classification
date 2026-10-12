# CNN Crop and Weed Classification using VGG16

Individual Deep Learning study project, **Roll Number 43**, **Nalacherla Shravan Kumar**, **23EG110C43**. Local Jupyter is the primary workflow. VGG16 ImageNet transfer learning predicts Crop (0) or Weed (1) from V2 Plant Seedlings.

## Windows quick start

Install Git and Python 3.11 if absent. In PowerShell:

```powershell
git clone https://github.com/shravan-kumar-nalacharla/CNN-Crop-and-Weed-Classification.git
cd CNN-Crop-and-Weed-Classification
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-local.txt
python -m ipykernel install --user --name crop-weed-vgg16 --display-name "Crop Weed VGG16"
python scripts/verify_environment.py
python scripts/download_dataset.py
python scripts/verify_dataset.py
python scripts/train_vgg16.py --smoke-test
python -m jupyter lab
```

setup_windows.ps1 automates environment setup. If activation is restricted, use .venv/Scripts/python.exe directly. Never install dependencies globally.

## Linux or WSL quick start

Install Git, Python 3.11 and its OS venv package if absent:

```bash
git clone https://github.com/shravan-kumar-nalacharla/CNN-Crop-and-Weed-Classification.git
cd CNN-Crop-and-Weed-Classification
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-local.txt
python -m ipykernel install --user --name crop-weed-vgg16 --display-name "Crop Weed VGG16"
python scripts/verify_environment.py
python scripts/download_dataset.py
python scripts/verify_dataset.py
python scripts/train_vgg16.py --smoke-test
python -m jupyter lab
```

bash setup_linux.sh automates setup. Modern native Windows TensorFlow supports CPU execution. For NVIDIA acceleration use WSL2 (install tensorflow[and-cuda] inside the environment following https://www.tensorflow.org/install/pip) or optional Google Colab.

## Notebook and full training

Open notebooks/VGG16_Crop_Weed_Classification.ipynb, select **Crop Weed VGG16**, and Run All. Root detection supports starting Jupyter from the repository or notebooks folder, including paths with spaces. First model creation downloads official ImageNet weights.

Full CLI: `python scripts/train_vgg16.py`. Memory-saving option: `python scripts/train_vgg16.py --batch-size 2`. Defaults: 224×224 RGB, batch 16, seed 42, stratified 70/15/15 split, training-only augmentation and balanced training class weights. Never divide pixels by 255 before VGG16 preprocessing. Head: global average pooling, Dense 128 ReLU, Dropout 0.5, one sigmoid. Train the head for up to 10 epochs with frozen VGG16 at 0.001, then only block5 for up to 5 epochs at 0.00001. Checkpoint, early stopping and learning-rate reduction monitor validation loss.

Smoke testing uses 8 balanced training, 4 validation and 4 test real images selected after splitting. It runs one head epoch and verifies preprocessing, block5 trainability, forward/backward passes, saving/reloading and predictions. Smoke results stay in outputs/smoke/ and models/smoke/ and never overwrite full results.

`python scripts/execute_notebook.py --smoke-test` executes a smoke copy of every notebook cell from the notebooks folder without changing the notebook's full-run default. `python scripts/validate_fine_tuning.py` performs an additional single-image block5 backward pass after the CLI smoke test. This additional check remains a validation test, not a full training experiment. See docs/Validation.md for the actual local execution status. requirements-lock-windows.txt records the installed Windows versions; requirements-local.txt is the portable dependency list.

Full outputs include distribution, samples, accuracy/loss, confusion matrix, predictions, misclassified images, classification_report.csv, dataset_splits.csv, test_predictions.csv and results_summary.json. The best model is models/best_vgg16_crop_weed.keras. Generated results are the sole source for report and presentation metrics.

Run `python scripts/build_artifacts.py` to rebuild the notebook and Word report after training. The presentation builder also reads results_summary.json. Full-training result placeholders remain explicit until training completes.

## Validation and submission

`python scripts/validate_project.py` compiles Python/notebook cells, checks disjoint splits and stale references. See docs/Learning_Guide.md and docs/Dataset_Sources.md. Course references remain unchanged. The report follows the sample structure, stays below 20 pages and supports one-sided printing. The 11-slide deck supports a 10-minute individual presentation.

Raw images, credentials, environment, models, caches and smoke results remain local. Source, setup, notebook, docs, report and presentation are versioned. Only actual full-training graphs may be explicitly added to Git.
