import ast
import json
from pathlib import Path
import pandas as pd
from dataset import ROOT

def main():
    for p in (ROOT/'scripts').glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    notebook=json.loads((ROOT/'notebooks/VGG16_Crop_Weed_Classification.ipynb').read_text(encoding='utf-8'))
    for i,cell in enumerate(notebook['cells']):
        if cell['cell_type']=='code':compile(''.join(cell['source']),f'cell {i}','exec')
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
    print('PASS: Python and notebook compilation, kernel metadata, saved split disjointness and individual-project checks.')

if __name__=='__main__':main()
