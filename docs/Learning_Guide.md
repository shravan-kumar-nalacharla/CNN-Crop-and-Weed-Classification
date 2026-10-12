# Roll 43 individual learning guide

This project demonstrates syllabus Unit I (Adam, learning rate, cross-entropy, dropout), Unit II (convolution and pooling) and Unit V (transfer learning). It extends the lab image-classification workflow using pretrained VGG16. Read scripts/core.py beside the notebook: both use the same implementation.

VGG16 uses 13 convolution layers in five blocks. ImageNet features initialize the binary head. Global average pooling produces a feature vector; Dense 128 learns the task, dropout 0.5 regularizes it, and one sigmoid gives Weed probability. Below 0.5 means Crop.

Keep raw pixels in 0–255. VGG16 preprocessing reverses RGB to BGR and subtracts ImageNet means. It occurs inside the saved model after augmentation, so inference uses the same conversion.

Split before augmentation. Seed 42 fixes stratified 70/15/15 partitions. Class weights use training labels only. Test images remain held out. Repeated growth stages of plants can share identity across image-level splits and overestimate generalization. Future work should use verified plant identities for grouped splits.

Train the head with the frozen base at 0.001 for at most 10 epochs. Then train only block5 at 0.00001 for at most 5 epochs, recompiling after trainability changes. The checkpoint preserves best validation loss across both phases.

Use the 11-slide deck for a 10-minute individual talk. Explain split hygiene, preprocessing and the training phases before measured results. Smoke metrics verify execution only.

Viva questions: Why ImageNet? Why not divide by 255? Why class weights? Why keep test data separate? Why fine-tune only block5? Why can high accuracy conceal poor Crop recall? Answer using the code and generated classification report.
