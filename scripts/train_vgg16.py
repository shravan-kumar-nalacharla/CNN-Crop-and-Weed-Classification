import argparse
from pathlib import Path
from core import Config, Experiment
from dataset import DATA

def main():
    parser=argparse.ArgumentParser(description='Roll 43 VGG16 transfer learning')
    parser.add_argument('--smoke-test',action='store_true')
    parser.add_argument('--batch-size',type=int,default=16)
    parser.add_argument('--head-epochs',type=int,default=10)
    parser.add_argument('--fine-epochs',type=int,default=5)
    parser.add_argument('--data-dir',type=Path,default=DATA)
    parser.add_argument('--threads',type=int,default=2)
    a=parser.parse_args()
    if not 1<=a.head_epochs<=10 or not 1<=a.fine_epochs<=5 or a.batch_size<1:
        parser.error('Batch must be positive; head epochs 1–10 and fine epochs 1–5.')
    e=Experiment(Config(a.data_dir,a.batch_size,a.head_epochs,a.fine_epochs,42,a.smoke_test,a.threads))
    e.explore();e.prepare();e.build();e.train_head();e.fine_tune();e.plot_history();e.evaluate()

if __name__=='__main__':
    main()
