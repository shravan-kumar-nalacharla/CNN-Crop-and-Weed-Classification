// Run with the bundled artifact-tool Node runtime. See presentation/README.md.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const runtime=process.env.CODEX_ARTIFACT_RUNTIME || 'C:/Users/shrav/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
process.env.RUNTIME_NODE=path.join(runtime,'node/bin/node.exe');
const skill=process.env.CODEX_PRESENTATIONS_SKILL || 'C:/Users/shrav/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(root,'.build/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href).catch(async()=>await import('@oai/artifact-tool'));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
await fs.mkdir(path.join(root,'.build/slides'),{recursive:true});
await fs.mkdir(path.join(root,'presentation'),{recursive:true});
let results=null;
try {const r=JSON.parse(await fs.readFile(path.join(root,'outputs/results_summary.json'),'utf8'));if(r.status==='full_training_completed')results=r;}catch{}
const rows=[
 ['CNN Crop and Weed\nClassification using VGG16','Individual Deep Learning study project\nNalacherla Shravan Kumar\n23EG110C43 • Roll Number 43',40,'Introduce the binary image-classification task and explain that this is an individual project using ImageNet transfer learning.'],
 ['Problem statement','Seedlings can look similar across species.\nThe classifier predicts Crop or Weed from an RGB image.\nControlled dataset performance needs field validation.',55,'Explain why preserving crops while identifying weeds matters. Do not claim deployment readiness.'],
 ['Objectives','Adapt ImageNet VGG16 to a binary classifier.\nKeep training, validation and test images separate.\nMeasure class recall, precision, F1 and AUC.\nProvide a reproducible local Jupyter workflow.',45,'Describe the reproducibility and evaluation goals.'],
 ['Dataset','V2 Plant Seedlings: 5,539 RGB images, 12 species.\nCrop: Maize, Common Wheat and Sugar Beet.\nWeed: the remaining nine species.\nCC BY-SA 4.0 with source attribution.',60,'Explain that the mapping is project-specific. Original source describes roughly 960 plants at multiple growth stages. Sources: https://vision.eng.au.dk/plant-seedlings-dataset/ and https://www.kaggle.com/datasets/vbookshelf/v2-plant-seedlings-dataset'],
 ['Preprocessing','224 × 224 RGB images, raw pixels in 0–255.\nVGG16 converts RGB to BGR and subtracts channel means.\nSeed 42, stratified 70% / 15% / 15% split.\nAugmentation only during training.',60,'Explain why dividing by 255 would be incorrect here. Discuss flips, small rotation, zoom and translation. Source: https://www.tensorflow.org/api_docs/python/tf/keras/applications/VGG16'],
 ['VGG16 architecture','ImageNet base with 13 convolution layers in five blocks.\nGlobal average pooling replaces the original classifier.\nDense 128 ReLU and Dropout 0.5.\nOne sigmoid estimates Weed probability.',70,'Explain convolution features, pooling and the binary output threshold of 0.5. Source: https://arxiv.org/abs/1409.1556'],
 ['Transfer learning procedure','Phase 1: freeze the base and train the new head.\nPhase 2: unfreeze block5 and recompile.\nKeep blocks 1–4 frozen.\nReload the best validation-loss checkpoint.',70,'Explain that pretrained early features stay fixed and higher-level features adapt cautiously.'],
 ['Hyperparameters','Batch 16 by default, configurable for laptop memory.\nHead: Adam 0.001, maximum 10 epochs.\nBlock5: Adam 0.00001, maximum 5 more epochs.\nBinary cross-entropy and balanced class weights.\nEarly stopping and learning-rate reduction.',55,'Weights use training labels only. Early stopping patience 3 and plateau patience 2. Explain lower fine-tuning learning rate.'],
 ['Accuracy and loss graphs',results?`Full training completed: ${results.epochs} epochs.\nMeasured accuracy: ${(results.test_accuracy*100).toFixed(2)}%.`:'FULL TRAINING RESULTS PENDING\nAccuracy and loss graphs will come from generated outputs.\nSmoke-test metrics verify execution only.',60,'Discuss overfitting using measured curves when available. Do not invent performance.'],
 ['Confusion matrix and predictions',results?`Test loss: ${results.test_loss.toFixed(4)}   AUC: ${results.auc.toFixed(4)}\nInspect Crop recall and misclassified images.`:'FULL TRAINING RESULTS PENDING\nInsert generated confusion matrix and test predictions.\nPrioritize Crop recall when interpreting errors.',55,'Explain matrix rows as actual and columns as predicted. A crop predicted as weed can be costly.'],
 ['Conclusion and limitations','VGG16 provides a reproducible transfer-learning baseline.\nCPU execution is supported in local Jupyter.\nControlled backgrounds and repeated plants limit generalization.\nFuture work: plant-level splits, field images and calibration.',30,'Conclude honestly about implementation and pending or measured results. Sum of slide timings is 600 seconds.']
];
function text(slide,value,left,top,width,height,size=30,color='#163c2f',bold=false){
 const shape=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={typeface:'Arial',fontSize:size,color,bold};return shape;
}
for(const [i,row] of rows.entries()){
 const [title,body,seconds,notes]=row;
 const slide=presentation.slides.add();slide.background.fill='#f8faf7';
 text(slide,title,72,70,1136,i===0?170:100,i===0?56:44,'#163c2f',true);
 const hasEvidence=results&&(i===8||i===9);
 text(slide,body,72,i===0?310:210,1136,hasEvidence?100:360,hasEvidence?26:32,'#25332e');
 text(slide,`Roll 43   /   ${i+1} of 11`,72,654,700,30,18,'#657568');
 slide.speakerNotes.text=`Suggested time: ${seconds} seconds. ${notes}`;
 if(hasEvidence){
  const names=i===8?['accuracy_graph','loss_graph']:['confusion_matrix','sample_predictions'];
  for(const [j,name] of names.entries())slide.images.add({path:path.join(root,`outputs/${name}.png`),fit:'contain',alt:name,position:{left:72+j*580,top:320,width:550,height:300}});
 }
 const png=await presentation.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(root,`.build/slides/slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(root,'.build/candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const final=path.join(root,'presentation/Roll_43_VGG16_Presentation.pptx');
// Finalizer requires a new destination; use a unique validated file, then copy unchanged.
await fs.mkdir(path.join(root,'.build/validated'),{recursive:true});
const checked=path.join(root,`.build/validated/deck-${Date.now()}.pptx`);
const receipt=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:checked,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 explicitTotalSlideCount:11,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(root,`.build/presentation-validation-${Date.now()}.json`)});
await fs.copyFile(checked,final);console.log(JSON.stringify(receipt));
