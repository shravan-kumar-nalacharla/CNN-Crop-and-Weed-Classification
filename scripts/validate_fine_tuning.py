"""One real-image backward pass checks block5 without claiming a full run."""
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from core import ROOT, enable_block5, pipeline, predict_image

def main():
    tf.config.threading.set_intra_op_parallelism_threads(2)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    model=tf.keras.models.load_model(ROOT/'models/smoke/best_vgg16_crop_weed.keras')
    enable_block5(model)
    base=model.get_layer('vgg16')
    frozen=base.get_layer('block1_conv1').get_weights()[0].copy()
    trainable=base.get_layer('block5_conv3').get_weights()[0].copy()
    frame=pd.read_csv(ROOT/'outputs/smoke/test_predictions.csv').head(1)
    frame['path']=frame.relative_path.map(lambda p:str(ROOT/p))
    images,labels=next(iter(pipeline(frame,1)))
    values=model.train_on_batch(images,labels)
    assert all(np.isfinite(values))
    np.testing.assert_array_equal(frozen,base.get_layer('block1_conv1').get_weights()[0])
    assert not np.array_equal(trainable,base.get_layer('block5_conv3').get_weights()[0])
    path=ROOT/'models/smoke/block5_validation.keras';model.save(path)
    expected=model(images,training=False).numpy()
    restored=tf.keras.models.load_model(path)
    np.testing.assert_allclose(expected,restored(images,training=False).numpy(),rtol=1e-5,atol=1e-6)
    prediction=predict_image(restored,frame.iloc[0].path)
    receipt={'block5_backward_pass':'passed','blocks1_to4_remain_frozen':True,'save_reload':'passed','single_image_prediction':prediction,'full_training_completed':False}
    (ROOT/'outputs/smoke/fine_tuning_validation.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
