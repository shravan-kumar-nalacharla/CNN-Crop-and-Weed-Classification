# Local execution record

Execution date: 13 October 2026. Student: Nalacherla Shravan Kumar, 23EG110C43, Roll Number 43.

Environment: Windows 11 Home, Python 3.11.9 in the repository-specific .venv, TensorFlow 2.21.0, JupyterLab 4.6.4. Hardware: AMD Ryzen 3 5300U (4 cores / 8 logical processors), approximately 7.3 GiB RAM, AMD Radeon graphics, no NVIDIA GPU. TensorFlow detected one CPU and no GPU. Dependency consistency passed. A Windows package lock records installed versions.

The public Kaggle archive includes duplicate species trees and an incorrectly decoded apostrophe. The downloader now selects one complete species tree and normalizes that name. Kaggle API authentication was absent; kagglehub public access succeeded. Dataset verification decoded all 5,539 images and confirmed all twelve exact species counts. No unreadable images remained.

The stratified seed-42 partitions contain 3,877 training images, 831 validation images and 831 test images. Crop/Weed counts are 681/3,196 in training and 146/685 in each held-out partition. Saved paths are unique and disjoint.

The CLI smoke test passed on real images with batch size 2 and one head epoch. It checked 224×224 loading, the pretrained VGG16 structure, frozen Phase 1 base, correct channel-mean preprocessing, a head-weight update from backpropagation, sigmoid output, model saving/reloading and test predictions. It generated every required graph/CSV/JSON type under outputs/smoke/ and a checkpoint under models/smoke/. These are execution checks, not full-dataset performance claims.

An additional single-image backward pass passed with only block5 enabled: block1 weights stayed identical, block5 weights changed, loss/accuracy were finite, and the fine-tuned model saved/reloaded with matching predictions. Single-image prediction also passed.

Notebook execution passed: all 25 code cells ran top to bottom in a smoke copy using the registered Crop Weed VGG16 kernel, starting from the notebooks folder. The executed copy is saved locally under outputs/smoke/executed_notebook.ipynb. The main notebook remains configured for full training. The local JupyterLab server exposes the registered kernel. The actual project path contains spaces. Python compilation, notebook schema validation, split disjointness, PowerShell setup syntax, Linux shell syntax and stale-reference checks all passed. Linux syntax was checked locally using Git Bash; training was executed on Windows.

The Word report renders to twelve A4 pages and follows the reference cover, index and required section structure. All pages were inspected. The eleven-slide PowerPoint contains speaker notes totaling ten minutes and passed package, geometry, font and first-party import checks. All slides were inspected. Original course references remain unchanged; preserved report media/theme/custom XML parts match their source bytes.

Full training has not completed. Its maximum 10 frozen-head plus 5 block5 epochs remain available in the CLI and notebook. CPU training on the full dataset can take several hours. Report and presentation result sections contain explicit placeholders and never import smoke metrics. Run `python scripts/train_vgg16.py --batch-size 2`, then rebuild the report and presentation from the generated full-run results. Generated data, models, caches, environment and smoke outputs are excluded from Git.
