"""Execute a smoke copy without changing the default full-training notebook."""
import argparse
import nbformat
from nbclient import NotebookClient
from dataset import ROOT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke-test',action='store_true')
    args=parser.parse_args()
    source=ROOT/'notebooks/VGG16_Crop_Weed_Classification.ipynb'
    nb=nbformat.read(source,as_version=4)
    if args.smoke_test:
        for cell in nb.cells:
            if cell.cell_type=='code':
                cell.source=cell.source.replace('SMOKE_TEST = False','SMOKE_TEST = True')
    client=NotebookClient(nb,timeout=3600,kernel_name='crop-weed-vgg16',resources={'metadata':{'path':str(ROOT/'notebooks')}})
    client.execute()
    target=ROOT/('outputs/smoke/executed_notebook.ipynb' if args.smoke_test else 'outputs/executed_notebook.ipynb')
    target.parent.mkdir(parents=True,exist_ok=True);nbformat.write(nb,target)
    print(f'PASS: all notebook cells executed from notebooks folder: {target}')

if __name__=='__main__':main()
