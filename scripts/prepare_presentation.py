"""Read measured outputs and choose original dataset images for the slide deck."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def main():
    splits = pd.read_csv(ROOT/'outputs/dataset_splits.csv')
    counts = splits.groupby(['species','label']).size().reset_index(name='images')
    partitions = splits.groupby(['split','label']).size().unstack().reindex(['train','validation','test'])
    crops = int((splits.label==0).sum()); weeds = int((splits.label==1).sum())
    train = splits[splits.split=='train']
    weights = {str(label):len(train)/(2*int((train.label==label).sum())) for label in [0,1]}
    selected = []
    names = ['Maize','Common Wheat','Sugar Beet','Charlock','Cleavers','Common Chickweed']
    for name in names:
        row=train[train.species==name].iloc[1]
        selected.append({'path':row.relative_path,'species':name,'label':int(row.label)})
    cover=[train[train.species==name].iloc[0].relative_path for name in ['Maize','Black-grass']]
    result=None; history=None; examples=[]
    summary=ROOT/'outputs/results_summary.json'
    if summary.exists():
        result=json.loads(summary.read_text())
        assert result['status']=='full_training_completed'
        history=json.loads((ROOT/'outputs/training_history.json').read_text())
        predictions=pd.read_csv(ROOT/'outputs/test_predictions.csv')
        correct=predictions[predictions.label==predictions.predicted_label]
        errors=predictions[predictions.label!=predictions.predicted_label]
        correct_parts=[correct[correct.label==label].head(2) for label in [0,1]]
        error_parts=[errors[errors.label==label].head(1) for label in [0,1]]
        selected_errors=pd.concat(error_parts)
        selected_errors=pd.concat([selected_errors,errors.drop(index=selected_errors.index).head(2-len(selected_errors))])
        examples=pd.concat([*correct_parts,selected_errors]).head(6).to_dict('records')
        if len(examples)<6:
            used={r['relative_path'] for r in examples}
            examples.extend(predictions[~predictions.relative_path.isin(used)].head(6-len(examples)).to_dict('records'))
    data={'images':len(splits),'species':counts.to_dict('records'),'crop_images':crops,'weed_images':weeds,
          'splits':{name:{'crop':int(row[0]),'weed':int(row[1]),'total':int(row.sum())} for name,row in partitions.iterrows()},
          'class_weights':weights,'dataset_samples':selected,'cover_images':cover,'results':result,'history':history,'examples':examples}
    (ROOT/'.build').mkdir(exist_ok=True)
    (ROOT/'.build/presentation_data.json').write_text(json.dumps(data,indent=2),encoding='utf8')
    print('Presentation inputs prepared. Measured full results:',result is not None)

if __name__=='__main__':main()
