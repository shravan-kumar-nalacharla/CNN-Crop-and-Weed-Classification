import ast
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from dataset import ROOT

def main():
    for p in (ROOT/'scripts').glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    for notebook_path in (ROOT/'notebooks').glob('*.ipynb'):
        notebook=json.loads(notebook_path.read_text(encoding='utf-8'))
        for i,cell in enumerate(notebook['cells']):
            if cell['cell_type']=='code':compile(''.join(cell['source']),f'{notebook_path.name} cell {i}','exec')
        assert notebook['metadata']['kernelspec']['name']=='crop-weed-vgg16'
    for p in (ROOT/'outputs').rglob('dataset_splits.csv'):
        frame=pd.read_csv(p);assert not frame.relative_path.duplicated().any()
        sets=[set(frame[frame.split==s].relative_path) for s in ('train','validation','test')]
        assert all(not sets[i]&sets[j] for i in range(3) for j in range(i+1,3))
    for p in [ROOT/'README.md',*(ROOT/'docs').glob('*.md'),*(ROOT/'scripts').glob('*.py')]:
        if p.name==Path(__file__).name:continue
        text=p.read_text(encoding='utf-8').lower()
        for forbidden in ['mobilenetv2','assigned roll numbers','team roles','custom cnn','41-45']:
            assert forbidden not in text,f'Stale reference in {p}: {forbidden}'
    assert not (ROOT/'notebooks/CNN_Crop_Weed_Classification.ipynb').exists()
    summary=ROOT/'outputs/results_summary.json'
    if summary.exists():
        result=json.loads(summary.read_text())
        assert result['status']=='full_training_completed'
        frame=pd.read_csv(ROOT/'outputs/test_predictions.csv')
        splits=pd.read_csv(ROOT/'outputs/dataset_splits.csv')
        assert len(frame)==result['evaluated_test_images']==831
        assert len(splits)==result['dataset_images']==5539
        assert set(frame.relative_path)==set(splits.loc[splits.split=='test','relative_path'])
        assert not frame.relative_path.duplicated().any()
        predicted=(frame.weed_probability>=.5).astype(int)
        np.testing.assert_array_equal(predicted,frame.predicted_label)
        np.testing.assert_array_equal(np.where(predicted==1,'Weed','Crop'),frame.predicted_class)
        np.testing.assert_array_equal(confusion_matrix(frame.label,predicted,labels=[0,1]),result['confusion_matrix'])
        np.testing.assert_allclose(accuracy_score(frame.label,predicted),result['test_accuracy'],atol=1e-6)
        np.testing.assert_allclose(roc_auc_score(frame.label,frame.weed_probability),result['auc'],atol=1e-12)
        report=classification_report(frame.label,predicted,labels=[0,1],target_names=['Crop','Weed'],output_dict=True,zero_division=0)
        for label in ['Crop','Weed']:
            for metric in ['precision','recall','f1-score','support']:
                np.testing.assert_allclose(report[label][metric],result['classification_report'][label][metric],atol=1e-12)
        history=json.loads((ROOT/'outputs/training_history.json').read_text())
        assert all(len(values)==result['epochs'] and np.isfinite(values).all() for values in history.values())
        print('PASS: full-run predictions, held-out membership, confusion matrix, class metrics, AUC and epoch history agree.')
    print('PASS: Python and notebook compilation, kernel metadata, saved split disjointness and individual-project checks.')

if __name__=='__main__':main()
