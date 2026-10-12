"""One implementation for the local notebook and command-line experiment."""
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import tensorflow as tf
from dataset import ROOT, DATA, inspect_dataset

@dataclass
class Config:
    data_dir: Path = DATA
    batch_size: int = 16
    head_epochs: int = 10
    fine_epochs: int = 5
    seed: int = 42
    smoke_test: bool = False
    threads: int = 2

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        if self.batch_size < 1 or self.threads < 1:
            raise ValueError('Batch size and CPU threads must be positive.')
        if not 1 <= self.head_epochs <= 10 or not 1 <= self.fine_epochs <= 5:
            raise ValueError('Head epochs must be 1–10; fine-tuning epochs must be 1–5.')

@tf.keras.utils.register_keras_serializable(package='CropWeed')
class VGGPreprocess(tf.keras.layers.Layer):
    def call(self, inputs):
        return tf.keras.applications.vgg16.preprocess_input(inputs)

def augmentation(seed=42):
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal', seed=seed),
        tf.keras.layers.RandomRotation(.05, seed=seed+1),
        tf.keras.layers.RandomZoom(.1, seed=seed+2),
        tf.keras.layers.RandomTranslation(.05, .05, seed=seed+3)], name='training_augmentation')

def build_model(seed=42):
    requested_weights = 'imagenet'
    base = tf.keras.applications.VGG16(weights=requested_weights, include_top=False, input_shape=(224,224,3))
    assert requested_weights == 'imagenet'
    assert base.name == 'vgg16' and len([l for l in base.layers if isinstance(l, tf.keras.layers.Conv2D)]) == 13
    base.trainable = False
    assert not base.trainable_weights and all(not l.trainable for l in base.layers)
    inputs = tf.keras.Input((224,224,3), name='raw_rgb_0_255')
    x = augmentation(seed)(inputs)
    x = VGGPreprocess(name='vgg16_preprocessing')(x)
    x = base(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(128, activation='relu')(x)
    x = tf.keras.layers.Dropout(.5, seed=seed)(x)
    out = tf.keras.layers.Dense(1, activation='sigmoid', name='weed_probability')(x)
    model = tf.keras.Model(inputs, out, name='vgg16_crop_weed')
    assert model.output_shape[-1] == 1 and model.layers[-1].activation == tf.keras.activations.sigmoid
    compile_model(model, .001)
    return model

def compile_model(model, lr):
    model.compile(optimizer=tf.keras.optimizers.Adam(lr), loss='binary_crossentropy', metrics=['accuracy'])

def enable_block5(model):
    base = model.get_layer('vgg16')
    base.trainable = True
    for layer in base.layers:
        layer.trainable = layer.name.startswith('block5_')
    assert all(layer.trainable == layer.name.startswith('block5_') for layer in base.layers)
    assert any(layer.trainable_weights for layer in base.layers if layer.name.startswith('block5_'))
    compile_model(model, .00001)

def split_dataset(df, seed=42):
    train, rest = train_test_split(df, test_size=.3, stratify=df.label, random_state=seed)
    val, test = train_test_split(rest, test_size=.5, stratify=rest.label, random_state=seed)
    sets = [set(x.path) for x in (train,val,test)]
    assert all(not sets[i] & sets[j] for i in range(3) for j in range(i+1,3))
    result = pd.concat([x.assign(split=name) for x,name in zip((train,val,test), ('train','validation','test'))])
    assert result.path.nunique() == len(df)
    return result

def pipeline(frame, batch_size, training=False, seed=42):
    ds = tf.data.Dataset.from_tensor_slices((frame.path.to_numpy(), frame.label.to_numpy(dtype=np.float32)))
    if training:
        ds = ds.shuffle(len(frame), seed=seed, reshuffle_each_iteration=True)
    @tf.autograph.experimental.do_not_convert
    def load(path, label):
        image = tf.io.decode_image(tf.io.read_file(path), channels=3, expand_animations=False)
        image.set_shape((None,None,3))
        return tf.image.resize(tf.cast(image, tf.float32), (224,224)), tf.reshape(label,(1,))
    ds = ds.map(load, num_parallel_calls=1).batch(batch_size).prefetch(1)
    options = tf.data.Options(); options.threading.private_threadpool_size = 1
    return ds.with_options(options)

def class_weights(train):
    values = compute_class_weight('balanced', classes=np.array([0,1]), y=train.label)
    return {i:float(v) for i,v in enumerate(values)}

def callbacks(path, previous_best=np.inf):
    checkpoint = tf.keras.callbacks.ModelCheckpoint(str(path), monitor='val_loss', save_best_only=True)
    # Keep the global best across both separately compiled training phases.
    checkpoint.best = previous_best
    return [checkpoint, tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=.5, patience=2, min_lr=1e-7)]

def image_grid(frame, path, title, prediction=False):
    fig, axes = plt.subplots(2,4,figsize=(12,6))
    fig.suptitle(title)
    for ax in axes.flat:
        ax.axis('off')
    if frame.empty:
        axes.flat[0].text(.1,.5,'No misclassified examples', transform=axes.flat[0].transAxes)
    for ax, (_,row) in zip(axes.flat, frame.head(8).iterrows()):
        with Image.open(row.path) as image:
            ax.imshow(image.convert('RGB'))
        label = ['Crop','Weed'][int(row.label)]
        ax.set_title(f'{label}\nPred: {row.predicted_class}' if prediction else f'{row.species}\n{label}', fontsize=9)
    fig.tight_layout(); fig.savefig(path,dpi=140); plt.close(fig)

class Experiment:
    def __init__(self, config=None):
        self.cfg = config or Config()
        tf.keras.utils.set_random_seed(self.cfg.seed)
        try:
            tf.config.threading.set_intra_op_parallelism_threads(self.cfg.threads)
            tf.config.threading.set_inter_op_parallelism_threads(1)
        except RuntimeError:
            pass
        self.output = ROOT / ('outputs/smoke' if self.cfg.smoke_test else 'outputs')
        self.models = ROOT / ('models/smoke' if self.cfg.smoke_test else 'models')
        self.output.mkdir(parents=True,exist_ok=True); self.models.mkdir(parents=True,exist_ok=True)
        self.model_path = self.models/'best_vgg16_crop_weed.keras'
        self.histories = []

    def explore(self):
        self.df = inspect_dataset(self.cfg.data_dir)
        counts = self.df.label.value_counts().reindex([0,1])
        fig,ax=plt.subplots(figsize=(6,4)); ax.bar(['Crop','Weed'],counts)
        ax.set_ylabel('Images'); ax.set_title('Binary class distribution')
        fig.tight_layout(); fig.savefig(self.output/'class_distribution.png',dpi=140); plt.close(fig)
        image_grid(self.df.sample(8,random_state=42), self.output/'sample_images.png','V2 Plant Seedlings samples')
        return self.df

    def prepare(self):
        self.splits = split_dataset(self.df, self.cfg.seed)
        self.splits.drop(columns='path').to_csv(self.output/'dataset_splits.csv',index=False)
        frames = [self.splits[self.splits.split == name].copy() for name in ('train','validation','test')]
        if self.cfg.smoke_test:
            # Balanced real images selected AFTER splitting to preserve the held-out boundary.
            frames = [pd.concat([f[f.label==i].sample(n=n,random_state=42) for i in (0,1)]) for f,n in zip(frames,(4,2,2))]
            pd.concat([f.assign(split=n) for f,n in zip(frames,('train','validation','test'))]).drop(columns='path').to_csv(self.output/'smoke_subset.csv',index=False)
        self.train,self.val,self.test=frames
        batch = min(self.cfg.batch_size,2) if self.cfg.smoke_test else self.cfg.batch_size
        self.actual_batch_size = batch
        self.train_ds=pipeline(self.train,batch,True,self.cfg.seed)
        self.val_ds=pipeline(self.val,batch)
        self.test_ds=pipeline(self.test,batch)
        self.weights=class_weights(self.train)
        return self.splits

    def build(self):
        self.model=build_model(self.cfg.seed)
        batch, _ = next(iter(self.train_ds))
        assert self.model(batch,training=False).shape == (len(batch),1)
        pixel=tf.constant([[[[10.,20.,30.]]]])
        np.testing.assert_allclose(VGGPreprocess()(pixel).numpy(),[[[[-73.939,-96.779,-113.68]]]], atol=1e-3)
        self.model.summary()
        return self.model

    def train_head(self):
        assert not self.model.get_layer('vgg16').trainable_weights
        original_head = self.model.layers[-1].get_weights()[0].copy()
        h=self.model.fit(self.train_ds,validation_data=self.val_ds,epochs=1 if self.cfg.smoke_test else self.cfg.head_epochs,
                         class_weight=self.weights,callbacks=callbacks(self.model_path),verbose=2,shuffle=False)
        self.histories.append(h.history)
        assert not np.array_equal(original_head,self.model.layers[-1].get_weights()[0]), 'Backward pass did not update the head.'
        return h.history

    def fine_tune(self):
        enable_block5(self.model)
        if self.cfg.smoke_test:
            # One head epoch is the quick test. Validate the fine-tuning flags without another epoch.
            return {}
        previous=min(self.histories[0]['val_loss'])
        h=self.model.fit(self.train_ds,validation_data=self.val_ds,epochs=self.cfg.fine_epochs,
                         class_weight=self.weights,callbacks=callbacks(self.model_path,previous),verbose=2,shuffle=False)
        self.histories.append(h.history)
        return h.history

    def plot_history(self):
        self.history={key:sum([h[key] for h in self.histories],[]) for key in self.histories[0]}
        (self.output/'training_history.json').write_text(json.dumps(self.history,indent=2))
        for metric in ('accuracy','loss'):
            fig,ax=plt.subplots(figsize=(7,4))
            for key,label in ((metric,'Training'),('val_'+metric,'Validation')):
                ax.plot(range(1,len(self.history[key])+1),self.history[key],label=label)
            if len(self.histories)>1:
                ax.axvline(len(self.histories[0][metric])+.5,color='gray',linestyle='--',label='Block5 fine-tuning begins')
            ax.set(xlabel='Epoch',ylabel=metric.title(),title=('Smoke test ' if self.cfg.smoke_test else '')+metric.title())
            ax.legend();fig.tight_layout();fig.savefig(self.output/f'{metric}_graph.png',dpi=140);plt.close(fig)
        return self.history

    def evaluate(self):
        before = tf.keras.models.load_model(self.model_path)
        self.model=before
        images,_=next(iter(self.test_ds))
        expected=before(images,training=False).numpy()
        roundtrip=self.models/'reload_check.keras'; before.save(roundtrip)
        reloaded=tf.keras.models.load_model(roundtrip)
        np.testing.assert_allclose(expected,reloaded(images,training=False).numpy(),rtol=1e-5,atol=1e-6)
        roundtrip.unlink(); del reloaded
        loss,accuracy=self.model.evaluate(self.test_ds,verbose=0)
        probs=self.model.predict(self.test_ds,verbose=0).ravel(); predicted=(probs>=.5).astype(int)
        report=classification_report(self.test.label,predicted,target_names=['Crop','Weed'],labels=[0,1],output_dict=True,zero_division=0)
        pd.DataFrame(report).transpose().to_csv(self.output/'classification_report.csv')
        matrix=confusion_matrix(self.test.label,predicted,labels=[0,1])
        fig,ax=plt.subplots(figsize=(5,4));sns.heatmap(matrix,annot=True,fmt='d',xticklabels=['Crop','Weed'],yticklabels=['Crop','Weed'],ax=ax)
        ax.set(xlabel='Predicted',ylabel='Actual',title='Confusion matrix');fig.tight_layout();fig.savefig(self.output/'confusion_matrix.png',dpi=140);plt.close(fig)
        self.predictions=self.test.assign(weed_probability=probs,predicted_label=predicted,predicted_class=np.where(predicted==1,'Weed','Crop'))
        self.predictions.drop(columns='path').to_csv(self.output/'test_predictions.csv',index=False)
        image_grid(self.predictions,self.output/'sample_predictions.png','Test predictions',True)
        image_grid(self.predictions[self.predictions.label!=self.predictions.predicted_label],self.output/'misclassified_examples.png','Misclassified test images',True)
        summary={'status':'smoke_test_only' if self.cfg.smoke_test else 'full_training_completed','roll_number':43,
                 'model':'VGG16','weights_requested':'imagenet','test_loss':float(loss),'test_accuracy':float(accuracy),
                 'auc':float(roc_auc_score(self.test.label,probs)), 'classification_report':report,'confusion_matrix':matrix.tolist(),
                 'dataset_images':len(self.df),'dataset_species':int(self.df.species.nunique()),
                 'evaluated_test_images':len(self.test),'epochs':len(self.history['loss']),'batch_size':self.actual_batch_size,
                 'head_epochs_requested':self.cfg.head_epochs,'fine_epochs_requested':self.cfg.fine_epochs,
                 'split_counts':self.splits.split.value_counts().to_dict(),
                 'seed':self.cfg.seed,'model_saves_and_reloads':True}
        (self.output/'results_summary.json').write_text(json.dumps(summary,indent=2))
        print(json.dumps(summary,indent=2)); return summary

def predict_image(model,path):
    image=tf.keras.utils.load_img(path,target_size=(224,224),color_mode='rgb')
    raw=tf.keras.utils.img_to_array(image)[None,...]
    probability=float(model(raw,training=False).numpy()[0,0])
    return {'class':'Weed' if probability>=.5 else 'Crop','weed_probability':probability}
