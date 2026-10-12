# CNN Crop and Weed Classification

Study project for roll numbers 41-45. The project trains a binary Convolutional Neural Network to classify a single seedling image as **Crop** or **Weed**.

## Fastest way to run

1. Upload `notebooks/CNN_Crop_Weed_Classification.ipynb` to Google Colab.
2. Select **Runtime > Change runtime type > T4 GPU**.
3. Run all cells from top to bottom.
4. Download the generated `models/` and `outputs/` folders.

The notebook downloads the public V2 Plant Seedlings Dataset from Kaggle, maps its 12 species to two classes, creates stratified train/validation/test splits, trains the CNN, and saves every figure needed for the report and presentation.

## Project structure

```text
CNN_Crop_Weed_Classification/
|-- README.md
|-- requirements.txt
|-- data/
|   `-- README.md
|-- docs/
|   |-- Dataset_Sources.md
|   |-- Team_Learning_Guide.md
|   `-- Team_Learning_Guide.docx
|-- models/
|   `-- .gitkeep
|-- notebooks/
|   `-- CNN_Crop_Weed_Classification.ipynb
|-- outputs/
|   `-- .gitkeep
|-- presentation/
|   `-- .gitkeep
|-- references/
|   |-- DL Syllabus.docx
|   |-- List of study projects.docx
|   |-- ML_Deep_Learning_Lab_Programs.docx
|   |-- Sample report.docx
|   `-- README.md
|-- report/
|   `-- .gitkeep
`-- scripts/
    |-- build_artifacts.py
    `-- validate_project.py
```

## Dataset

- Dataset: V2 Plant Seedlings Dataset
- Kaggle handle: `vbookshelf/v2-plant-seedlings-dataset`
- Images: 5,539 RGB images in 12 species folders
- Crop species: Maize, Common wheat, Sugar beet
- Weed species: the remaining nine species
- License: CC BY-SA 4.0
- Original source: https://vision.eng.au.dk/plant-seedlings-dataset/
- Paper: https://arxiv.org/abs/1711.05458

The raw dataset is intentionally not stored in this project because it is approximately 1.7 GB. The notebook downloads it when required.

See `docs/Dataset_Sources.md` for the official source, mirrors, fallback, and datasets that were considered but not selected.

The `references/` folder contains the supplied syllabus, lab programs, project allocation, and sample report that should be followed when converting the project to the individual VGG16 submission.

## Reproducibility

- Random seed: 42
- Split: 70% training, 15% validation, 15% testing
- Input: 128 x 128 RGB
- Optimizer: Adam
- Loss: binary cross-entropy
- Class imbalance: balanced class weights
- Model selection: lowest validation loss

Do not type result percentages into the report before running the notebook. Use the values saved in `outputs/results_summary.json` and `outputs/classification_report.csv`.

## Main outputs

- `models/best_crop_weed_cnn.keras`
- `outputs/class_distribution.png`
- `outputs/sample_images.png`
- `outputs/accuracy_graph.png`
- `outputs/loss_graph.png`
- `outputs/confusion_matrix.png`
- `outputs/sample_predictions.png`
- `outputs/misclassified_examples.png`
- `outputs/classification_report.csv`
- `outputs/results_summary.json`

## Local validation

Run this without the dataset to check the notebook structure and Python syntax:

```powershell
python scripts/validate_project.py
```

