# CNN Crop and Weed Classification Team Learning Guide

## What we are building

We are training a binary CNN that receives one RGB seedling image and returns Crop or Weed. The model is trained on the V2 Plant Seedlings Dataset. Its 12 species are simplified into three crop species and nine weed species.

The notebook is the source of truth. Every metric and graph in the report or PPT must come from a completed notebook run.

## What each team member should understand

Everyone should be able to explain the problem, dataset, label mapping, preprocessing, CNN layers, hyperparameters, accuracy and loss curves, confusion matrix, conclusion, and limitations. Divide presentation work only after everyone understands this common flow.

## Dataset labels

Crop means Maize, Common wheat, or Sugar beet. Weed means Black-grass, Charlock, Cleavers, Common chickweed, Fat hen, Loose silky-bent, Scentless mayweed, Shepherd's purse, or Small-flowered cranesbill.

The dataset is imbalanced because weed images are much more common. A model that always predicts Weed would appear accurate, so accuracy alone is insufficient. We use class weights and also report precision, recall, F1-score, and the confusion matrix.

## CNN in plain language

A convolution layer learns small visual patterns such as edges, curves, leaf shapes, and textures. Pooling reduces spatial size while keeping important information. Deeper convolution layers combine simple patterns into more meaningful plant features. The dense layer combines these features. The sigmoid output produces a probability from 0 to 1, where values at or above 0.5 are predicted as Weed.

## Training flow

1. Download or locate the 12 species folders.
2. Convert species names into binary labels.
3. Make stratified 70/15/15 splits with random seed 43.
4. Resize images to 128 x 128 and normalize pixel values.
5. Augment training images only.
6. Compute class weights from the training labels.
7. Train the CNN while monitoring validation loss.
8. Restore the best model and evaluate it once on the test set.
9. Save graphs, metrics, sample predictions, and the trained model.

## How to read the results

Training accuracy shows how well the model fits images it learns from. Validation accuracy estimates performance on unseen images during training. If training accuracy rises while validation accuracy falls, the model is overfitting. Loss measures prediction error, so lower is better. The confusion matrix shows correct and incorrect Crop and Weed predictions. Recall for Crop is especially important because the dataset contains fewer crop images.

## Safe result reporting

Never copy an accuracy value from another project. Read the final values from `outputs/results_summary.json`. Explain both strengths and weaknesses. The dataset uses isolated seedlings and controlled backgrounds, so performance may fall on crowded real-field photographs.

## Suggested team roles

- Member 1: problem statement, motivation, and objectives
- Member 2: dataset, labels, preprocessing, and augmentation
- Member 3: CNN architecture and hyperparameters
- Member 4: training graphs, confusion matrix, and metrics
- Member 5: conclusion, limitations, future work, and final file checks

Roll number 43 should be ready to connect all sections and answer questions about the complete workflow.

## Common viva questions

**Why CNN instead of a normal neural network?** CNNs preserve spatial relationships and learn image features with shared filters, using fewer parameters than fully connected processing of every pixel.

**Why binary cross-entropy?** There are two output classes and the model produces one sigmoid probability.

**Why use class weights?** Crop images are the minority. Class weights make errors on minority crop images contribute more during training.

**Why do we need validation and test sets?** Validation data guides model selection. The untouched test set estimates final generalization.

**What does dropout do?** It randomly disables some neurons during training to reduce dependence on particular features and limit overfitting.

**Why use early stopping?** It stops training when validation loss no longer improves and restores the best weights.

**What is the biggest limitation?** Most images show isolated plants under controlled conditions, so the model is not yet proven on cluttered field scenes.

## Final checklist

- Run every notebook cell in order.
- Confirm that all 12 species were found and exactly two binary labels were created.
- Confirm that train, validation, and test sets do not overlap.
- Save the best model and all figures.
- Copy metrics only from generated output files.
- Put accuracy and loss graphs in both report and PPT.
- Add the confusion matrix and sample predictions.
- Keep the report within 20 one-sided pages.
- Rehearse the presentation to finish in 9 minutes, leaving 1 minute for questions.

## References

- Plant Seedlings Dataset: https://vision.eng.au.dk/plant-seedlings-dataset/
- Dataset paper: https://arxiv.org/abs/1711.05458
- Kaggle V2 dataset: https://www.kaggle.com/datasets/vbookshelf/v2-plant-seedlings-dataset
- TensorFlow image classification tutorial: https://www.tensorflow.org/tutorials/images/classification

