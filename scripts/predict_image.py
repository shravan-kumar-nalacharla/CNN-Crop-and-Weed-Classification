"""Predict one image with the completed project's saved VGG16 checkpoint."""
import argparse
import json
from pathlib import Path
import tensorflow as tf
from core import predict_image
from dataset import ROOT

def main():
    parser=argparse.ArgumentParser(description='Predict Crop or Weed using the saved VGG16 model')
    parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--model',type=Path,default=ROOT/'models/best_vgg16_crop_weed.keras')
    args=parser.parse_args()
    image=args.image if args.image.is_absolute() else ROOT/args.image
    model_path=args.model if args.model.is_absolute() else ROOT/args.model
    if not image.is_file():parser.error(f'Image does not exist: {image}')
    if not model_path.is_file():parser.error(f'Trained model does not exist: {model_path}')
    tf.config.threading.set_intra_op_parallelism_threads(2)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    model=tf.keras.models.load_model(model_path,compile=False)
    print(json.dumps({'image':str(image),**predict_image(model,image)},indent=2))

if __name__=='__main__':main()
