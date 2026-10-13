"""Create a fast notebook for reviewing the completed full-run outputs."""
import json
import nbformat
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    result=json.loads((ROOT/'outputs/results_summary.json').read_text())
    assert result['status']=='full_training_completed'
    n=nbformat.v4;cells=[]
    def md(s):cells.append(n.new_markdown_cell(s))
    def code(s):cells.append(n.new_code_cell(s))
    md('# Review the Completed VGG16 Results\n\nNalacherla Shravan Kumar · 23EG110C43 · Roll 43.\n\nThis notebook reads the completed full-run files. **It does not train the model.** Use the Crop Weed VGG16 kernel and Run All to review results quickly. The main VGG16 notebook contains the full training workflow.')
    code("from pathlib import Path\nimport json, sys\nimport pandas as pd\nimport numpy as np\nfrom IPython.display import Image, display\nROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'scripts/core.py').exists())\nOUTPUT = ROOT/'outputs'\nprint('Project:', ROOT)")
    md('## Test summary\nThe model was selected using validation loss. These metrics come from the held-out test partition, not the smoke test.')
    code("results = json.loads((OUTPUT/'results_summary.json').read_text())\nassert results['status'] == 'full_training_completed'\ndisplay(pd.DataFrame({'Metric':['Test accuracy','Test loss','ROC AUC','Test images','Measured epochs','Batch size'], 'Value':[results['test_accuracy'],results['test_loss'],results['auc'],results['evaluated_test_images'],results['epochs'],results['batch_size']]}))\nprint(f\"Test accuracy: {results['test_accuracy']:.2%}\")")
    md('## Verified partitions\nTraining updates weights, validation selects checkpoints, and test data measures the selected model. Paths are disjoint; plant identities may still overlap across growth stages.')
    code("splits = pd.read_csv(OUTPUT/'dataset_splits.csv')\ndisplay(splits.groupby(['split','label']).size().unstack().rename(columns={0:'Crop',1:'Weed'}))\nassert not splits.relative_path.duplicated().any()\nassert len(splits) == 5539")
    md('## Accuracy and epoch values\nBlue and orange curves represent training and validation. Test accuracy is reported separately.')
    code("history = json.loads((OUTPUT/'training_history.json').read_text())\ndisplay(pd.DataFrame(history).assign(epoch=lambda f: np.arange(1,len(f)+1)))\ndisplay(Image(filename=str(OUTPUT/'accuracy_graph.png')))")
    md('## Loss\nTraining loss uses class weights. Validation loss is unweighted. The best validation loss selects the checkpoint across both phases.')
    code("display(Image(filename=str(OUTPUT/'loss_graph.png')))")
    md('## Confusion matrix and class metrics\nRows are actual labels and columns are predicted labels. Inspect Crop recall as well as overall accuracy.')
    code("display(Image(filename=str(OUTPUT/'confusion_matrix.png')))\ndisplay(pd.read_csv(OUTPUT/'classification_report.csv',index_col=0))")
    md('## Actual prediction examples and errors\nThese are saved predictions for test images. A sigmoid score is not a calibrated guarantee.')
    code("display(Image(filename=str(OUTPUT/'sample_predictions.png')))\ndisplay(Image(filename=str(OUTPUT/'misclassified_examples.png')))")
    md('## Every test prediction\nThe CSV records the original image path, species, actual label, score and predicted label.')
    code("predictions = pd.read_csv(OUTPUT/'test_predictions.csv')\nassert len(predictions) == results['evaluated_test_images']\nassert set(predictions.relative_path) == set(splits.loc[splits.split=='test','relative_path'])\ndisplay(predictions.head(10))\nprint('Correct predictions:', (predictions.label == predictions.predicted_label).sum())")
    md('## Reload the saved model and check one prediction\nThis final cell performs inference only. It checks that a single-image prediction matches the saved test score. The checkpoint and raw data remain local, so the cell skips inference on a fresh clone that does not contain those files.')
    code("model_path = ROOT/'models/best_vgg16_crop_weed.keras'\nrow = predictions.loc[predictions.label==0].iloc[0]\nimage_path = ROOT/row.relative_path\nif model_path.exists() and image_path.exists():\n    import tensorflow as tf\n    tf.config.threading.set_intra_op_parallelism_threads(2)\n    tf.config.threading.set_inter_op_parallelism_threads(1)\n    sys.path.insert(0,str(ROOT/'scripts'))\n    from core import predict_image\n    model = tf.keras.models.load_model(model_path,compile=False)\n    prediction = predict_image(model,image_path)\n    np.testing.assert_allclose(prediction['weed_probability'], row.weed_probability, rtol=1e-4, atol=1e-5)\n    assert prediction['class'] == row.predicted_class\n    print('Actual label: Crop')\n    print(prediction)\nelse:\n    print('Graphs and metrics reviewed. The local checkpoint and raw image are required for inference.')")
    md('## What to study next\nRead docs/Project_Explained_From_Zero.md or the Word study guide. Use the results presentation for the eleven-slide talk. Remember the image-level split and controlled-background limitations.')
    nb=n.new_notebook(cells=cells,metadata={'kernelspec':{'name':'crop-weed-vgg16','display_name':'Crop Weed VGG16','language':'python'},'language_info':{'name':'python','version':'3.11'}})
    path=ROOT/'notebooks/Review_Completed_Results.ipynb';nbformat.write(nb,path)
    print('Results review notebook:',path)

if __name__=='__main__':main()
