# Local execution record

Execution date: 13 October 2026. Student: Nalacherla Shravan Kumar, 23EG110C43, Roll Number 43.

Environment: Windows 11 Home, Python 3.11.9 in the repository-specific .venv, TensorFlow 2.21.0, JupyterLab 4.6.4. Hardware: AMD Ryzen 3 5300U (4 cores / 8 logical processors), approximately 7.3 GiB RAM, AMD Radeon graphics, no NVIDIA GPU. TensorFlow detected one CPU and no GPU. Dependency consistency passed. A Windows package lock records installed versions.

The public Kaggle archive includes duplicate species trees and an incorrectly decoded apostrophe. The downloader now selects one complete species tree and normalizes that name. Kaggle API authentication was absent; kagglehub public access succeeded. Dataset verification decoded all 5,539 images and confirmed all twelve exact species counts. No unreadable images remained.

The stratified seed-42 partitions contain 3,877 training images, 831 validation images and 831 test images. Crop/Weed counts are 681/3,196 in training and 146/685 in each held-out partition. Saved paths are unique and disjoint.

The CLI smoke test passed on real images with batch size 2 and one head epoch. It checked 224×224 loading, the pretrained VGG16 structure, frozen Phase 1 base, correct channel-mean preprocessing, a head-weight update from backpropagation, sigmoid output, model saving/reloading and test predictions. It generated every required graph/CSV/JSON type under outputs/smoke/ and a checkpoint under models/smoke/. These are execution checks, not full-dataset performance claims.

An additional single-image backward pass passed with only block5 enabled: block1 weights stayed identical, block5 weights changed, loss/accuracy were finite, and the fine-tuned model saved/reloaded with matching predictions. Single-image prediction also passed.

Notebook execution passed: all 25 code cells ran top to bottom in a smoke copy using the registered Crop Weed VGG16 kernel, starting from the notebooks folder. The executed copy is saved locally under outputs/smoke/executed_notebook.ipynb. The main notebook remains configured for full training. The local JupyterLab server exposes the registered kernel. The actual project path contains spaces. Python compilation, notebook schema validation, split disjointness, PowerShell setup syntax, Linux shell syntax and stale-reference checks all passed. Linux syntax was checked locally using Git Bash; training was executed on Windows.

Full training completed successfully on the full training partition with batch size 4 and four CPU threads: three frozen-head epochs followed by two block5 fine-tuning epochs (five total). Test accuracy was 97.71%, loss 0.0760 and ROC AUC 0.9918 on 831 images. The confusion matrix is [[131, 15], [4, 681]]: 812 correct predictions and 19 errors. Crop recall is 89.73%; Weed recall is 99.42%. These are measured full-run results, not smoke metrics. Checkpoint reload predictions matched the saved model.

The completed results-review notebook executed all nine code cells in the registered kernel without retraining. Its single-image inference matched the saved test prediction. The project validator recomputed threshold decisions, confusion matrix, class metrics and AUC from saved predictions and checked history and split membership; all passed.

The final Results report renders to 15 A4 pages; the beginner guide renders to 20 pages. Every final page was visually inspected. The final eleven-slide Results PowerPoint includes three editable charts, five native tables, genuine held-out images and ten minutes of speaker notes. It passed package, layout, fonts, first-party import, chart cache and embedded workbook checks; every slide was visually inspected. Original course references remain unchanged. Earlier artifacts without Results in their names are pre-training drafts.

Source, notebooks, final documents, presentation and small measured PNG/CSV/JSON outputs are versioned. Raw data, models, credentials, environment, smoke outputs and build intermediates remain local. Dataset path: data/raw/plant_seedlings. The saved model is models/best_vgg16_crop_weed.keras. No training or implementation work remains for submission; study the guide and practise the presentation.
