# Dataset Sources and Selection

## Selected dataset

### V2 Plant Seedlings Dataset

- Original source: https://vision.eng.au.dk/plant-seedlings-dataset/
- Kaggle download used by the notebook: https://www.kaggle.com/datasets/vbookshelf/v2-plant-seedlings-dataset
- Hugging Face mirror: https://huggingface.co/datasets/Project-AgML/plant_seedlings_aarhus
- Original paper: https://arxiv.org/abs/1711.05458
- Size: 5,539 RGB images, approximately 1.7 GB
- Original classes: 12 plant species
- License: CC BY-SA 4.0

This is the selected dataset because it contains three crop species and nine weed species, already organized for image classification. The notebook converts those species into the required binary Crop and Weed labels.

## Smaller fallback

The official Aarhus page also provides automatically segmented single-plant images of approximately 258 MB. Use this only if the 1.7 GB V2 download cannot be completed. Clearly state in the report that the automatically segmented variant was used; the official source warns that its segmentation is not ground truth.

## Datasets considered but not selected

### DeepWeeds

DeepWeeds contains weed species and a negative class, but it does not provide the same clear three-crop-versus-nine-weed mapping. It is better suited to weed-species recognition than this assignment's simple Crop/Weed classification.

### Crop and Weed Detection datasets

Several field datasets provide bounding boxes for object detection. They are useful for locating multiple plants, but would require a YOLO-style detection project rather than the CNN image-classification workflow taught in the lab.

## Citation requirement

The report should cite the original Aarhus dataset page and the Giselsson et al. dataset paper. Do not cite only Kaggle, because Kaggle is a convenient distribution source rather than the original creator.

