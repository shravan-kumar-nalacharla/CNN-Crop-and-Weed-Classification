"""Execute the training notebook or a results review using the registered kernel."""
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from dataset import ROOT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--notebook',type=Path,default=Path('notebooks/VGG16_Crop_Weed_Classification.ipynb'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--timeout',type=int,default=0,help='Seconds per cell; 0 allows long CPU training cells.')
    args=parser.parse_args()
    source=args.notebook if args.notebook.is_absolute() else ROOT/args.notebook
    if args.smoke_test and source.name!='VGG16_Crop_Weed_Classification.ipynb':
        parser.error('--smoke-test is only for the training notebook.')
    nb=nbformat.read(source,as_version=4)
    if args.smoke_test:
        for cell in nb.cells:
            if cell.cell_type=='code':
                cell.source=cell.source.replace('SMOKE_TEST = False','SMOKE_TEST = True')
    client=NotebookClient(nb,timeout=args.timeout or None,kernel_name='crop-weed-vgg16',resources={'metadata':{'path':str(ROOT/'notebooks')}})
    client.execute()
    target=args.output or ROOT/('outputs/smoke/executed_notebook.ipynb' if args.smoke_test else 'outputs/executed_notebook.ipynb')
    if not target.is_absolute():target=ROOT/target
    target.parent.mkdir(parents=True,exist_ok=True);nbformat.write(nb,target)
    print(f'PASS: all notebook cells executed from notebooks folder: {target}')

if __name__=='__main__':main()
