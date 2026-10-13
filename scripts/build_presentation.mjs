// Evidence-based deck inspired by the two supplied course presentations.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const runtime=process.env.CODEX_ARTIFACT_RUNTIME || 'C:/Users/shrav/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill=process.env.CODEX_PRESENTATIONS_SKILL || 'C:/Users/shrav/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
process.env.RUNTIME_NODE=path.join(runtime,'node/bin/node.exe');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const data=JSON.parse(await fs.readFile(path.join(root,'.build/presentation_data.json'),'utf8'));
const draft=process.argv.includes('--draft');
const result=data.results, history=data.history;
const imageBytes=new Map();
for(const p of new Set([...data.cover_images,...data.dataset_samples.map(r=>r.path),...(data.examples||[]).map(r=>r.relative_path)])) imageBytes.set(p,new Uint8Array(await fs.readFile(path.join(root,p))));
if(!result&&!draft)throw new Error('Full-dataset results are required. Run training and scripts/prepare_presentation.py first.');
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#12213d',blue:'#2863a6',cyan:'#2cb7c9',orange:'#ed9133',paper:'#f1f6fc',white:'#ffffff',ink:'#27364a',muted:'#596d84',line:'#d5e0ed',green:'#24794f'};
const font='Arial', pct=v=>(100*v).toFixed(2)+'%', num=v=>v.toFixed(4);
const timings=[30,50,70,55,85,65,65,60,45,45,30];
const sources='Sources: outputs/dataset_splits.csv, outputs/training_history.json, outputs/results_summary.json, outputs/test_predictions.csv. Dataset attribution: Giselsson et al. (2017), https://arxiv.org/abs/1711.05458, https://vision.eng.au.dk/plant-seedlings-dataset/, CC BY-SA 4.0.';
const slides=[];
function rect(s,x,y,w,h,fill,stroke='none',radius=0){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1},borderRadius:radius});}
function text(s,value,x,y,w,h,size=26,color=C.ink,bold=false){
 const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={typeface:font,fontSize:size,color,bold};shape.text.insets=0;return shape;
}
function photo(s,p,x,y,w,h,alt){return s.images.add({blob:imageBytes.get(p),contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain',alt});}
function slide(title,subtitle,notes){
 const s=presentation.slides.add();s.background.fill=C.paper;
 rect(s,0,0,1280,110,C.navy);text(s,title,54,25,1120,54,40,C.white,true);
 text(s,subtitle,56,80,1120,22,18,'#c8d6e8');
 text(s,String(slides.length+1).padStart(2,'0'),1195,39,45,30,22,C.cyan,true);
 text(s,'Nalacherla Shravan Kumar   23EG110C43',56,679,1010,22,16,C.muted);
 s.speakerNotes.text=`Suggested time: ${timings[slides.length]} seconds. ${notes}\n${sources}`;
 slides.push(s);return s;
}
function table(s,values,x,y,w,h,widths,size=24){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});
 t.borders.assign({style:'solid',fill:C.line,width:1});
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{top:3,bottom:3,left:10,right:10},anchor:'center'});
 t.styleOptions={headerRow:true,bandedRows:false};
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?C.navy:r%2?'#ffffff':'#e6eef8';
  cell.text.style={typeface:font,fontSize:size,color:r===0?C.white:C.ink,bold:r===0};
 }
 return t;
}
function metric(s,label,value,x,y,w=320,color=C.blue){text(s,label,x,y,w,32,24,C.navy,true);text(s,value,x,y+38,w,75,56,color,true);}
function pending(s){text(s,'Training is running',900,180,300,50,30,C.orange,true);text(s,'Internal design preview.\nMeasured results will populate this slide after training.',900,245,300,160,24);}

// 1. Cover with real crop and weed images, rather than decorative illustrations.
{
 const s=presentation.slides.add();s.background.fill=C.navy;slides.push(s);
 text(s,'DEEP LEARNING INDIVIDUAL PROJECT',56,56,950,35,24,C.cyan,true);
 text(s,'CNN Crop and Weed\nClassification using VGG16',56,127,780,175,54,C.white,true);
 text(s,'ImageNet transfer learning for binary seedling classification',58,328,720,70,28,'#cedcec');
 text(s,'Nalacherla Shravan Kumar\n23EG110C43\nRoll Number 43',58,447,720,120,27,C.white);
 photo(s,data.cover_images[0],875,115,330,215,'Original Maize seedling image');
 photo(s,data.cover_images[1],875,377,330,215,'Original Black-grass seedling image');
 text(s,'CROP',885,336,310,30,22,C.cyan,true);text(s,'WEED',885,598,310,30,22,C.orange,true);
 text(s,result?'Measured results from local CPU training':'Local CPU training in progress',58,651,1100,27,19,'#bdcee4');
 s.speakerNotes.text=`Suggested time: 30 seconds. Introduce the student, project and two binary categories. ${sources}`;
}
// 2. Problem statement and objective, following the reference's explicit task definition.
{
 const s=slide('1. Problem statement','Identify crops and weeds from one RGB seedling image','Explain why crop protection requires reliable recognition, and why seedlings are visually challenging. This experiment studies classification on controlled images.');
 text(s,'The task',56,150,550,40,30,C.blue,true);
 text(s,'Given one plant image, predict Crop or Weed using the project’s species mapping.',56,207,550,110,31);
 text(s,'Why it is challenging',56,356,550,40,28,C.blue,true);
 text(s,'Young plants share leaf shapes and green colour.\nWeed images greatly outnumber crop images.\nControlled backgrounds differ from field conditions.',56,414,570,170,26);
 text(s,'Project objective',720,150,500,40,30,C.blue,true);
 text(s,'Adapt pretrained VGG16 features and evaluate predictions on unseen test images.',720,207,500,125,31);
 text(s,'Binary decision',720,377,500,35,28,C.navy,true);
 rect(s,720,437,210,83,C.blue);rect(s,961,437,210,83,C.orange);
 text(s,'0 = Crop',742,458,170,40,29,C.white,true);text(s,'1 = Weed',981,458,180,40,29,C.white,true);
 text(s,'Decision threshold: Weed probability ≥ 0.5',720,555,500,70,25);
}
// 3. Real images and verified species counts.
{
 const s=slide('2. Dataset used','V2 Plant Seedlings dataset from Kaggle and Aarhus University','Explain that the downloaded dataset has twelve species. Point to crop samples and the nine mapped weed species. All counts come from saved splits.');
 metric(s,'Verified RGB images',String(data.images),56,139,330);
 metric(s,'Plant species',String(data.species.length),415,139,220);
 text(s,'Original dataset samples',56,282,620,40,26,C.navy,true);
 for(const [i,row] of data.dataset_samples.entries()){
  const x=56+(i%3)*193,y=330+Math.floor(i/3)*154;
  photo(s,row.path,x,y,174,100,`${row.species} ${row.label===0?'Crop':'Weed'}`);
  text(s,row.species,x,y+104,182,24,17,C.ink,true);
  text(s,row.label===0?'Crop':'Weed',x,y+128,182,23,17,row.label===0?C.green:C.orange);
 }
 const values=[['Species','Images'],...data.species.map(r=>[r.species,String(r.images)])];
 table(s,values,700,147,524,482,[390,134],20);
 text(s,'CC BY-SA 4.0. Original images recorded at several plant growth stages.',56,643,1160,25,17,C.muted);
}
// 4. Class imbalance, independent splits, and preprocessing.
{
 const s=slide('2. Preprocessing and data split','Seed 42, binary stratification, augmentation only during training','Explain the 70/15/15 split. VGG16 requires raw 0–255 RGB pixels, channel reversal and mean subtraction. Augmentation happens after splitting.');
 text(s,'Image pipeline',56,143,550,40,30,C.blue,true);
 const steps=[['RGB input','Resize to 224 × 224'],['Training augmentation','Horizontal flip, small rotation, zoom and translation'],['VGG16 preprocessing','RGB to BGR, subtract ImageNet channel means']];
 for(const [i,[name,detail]] of steps.entries()){
  text(s,String(i+1).padStart(2,'0'),56,208+i*116,57,52,34,C.cyan,true);
  text(s,name,135,203+i*116,500,34,27,C.navy,true);text(s,detail,135,245+i*116,493,59,24);
 }
 text(s,'Do not divide pixel values by 255.',56,594,610,38,26,C.orange,true);
 const chart=s.charts.add('bar',{position:{left:698,top:145,width:526,height:282},title:'Binary class distribution',titleTextStyle:{fontSize:25,fill:C.navy,bold:true},categories:['Crop','Weed'],series:[{name:'Images',values:[data.crop_images,data.weed_images],fill:C.blue,points:[{idx:0,fill:C.cyan},{idx:1,fill:C.orange}]}],hasLegend:false,dataLabels:{showValue:true,numberFormatCode:'0',position:'outEnd',textStyle:{fontSize:22,bold:true}},xAxis:{textStyle:{fontSize:20}},yAxis:{title:'Images',min:0,textStyle:{fontSize:18},majorGridlines:{fill:C.line,width:1}}});
 applyPresentationChartFont(chart,{fontFamily:font});
 const values=[['Split','Crop','Weed','Total'],...Object.entries(data.splits).map(([name,r])=>[name==='train'?'Training':name==='test'?'Test':'Validation',String(r.crop),String(r.weed),String(r.total)])];
 table(s,values,698,454,526,166,[184,108,108,126],21);
}
// 5. Editable architecture diagram.
{
 const s=slide('3. VGG16 model architecture','ImageNet convolution base with a binary classification head','Walk through the editable diagram. Explain thirteen convolutions in five blocks, pooled features and one Weed probability. Blocks 1–4 remain frozen in fine-tuning.');
 const nodes=[['Input','224 × 224 × 3 RGB pixels',C.blue],['Augment and preprocess','Training transforms, then VGG16 channel means',C.cyan],['VGG16 convolution base','13 convolutions, 5 pooling blocks, ImageNet weights',C.blue],['Global average pooling','7 × 7 × 512 feature maps become 512 features',C.cyan],['Dense layer','128 neurons with ReLU activation',C.blue],['Dropout','Rate 0.5 to limit overfitting',C.orange],['Output','1 sigmoid neuron: probability of Weed',C.cyan]];
 for(const [i,[name,detail,color]] of nodes.entries()){
  const y=139+i*70;rect(s,106,y,1068,53,color,'none',7);
  text(s,name,129,y+14,365,32,25,C.white,true);text(s,detail,520,y+14,634,32,24,C.white);
  if(i<6)s.shapes.add({geometry:'downArrow',position:{left:625,top:y+55,width:18,height:13},fill:C.muted,line:{fill:'none',width:0}});
 }
 text(s,'Phase 1: all VGG16 layers frozen. Phase 2: only block5 trainable.',106,646,1068,25,20,C.muted);
}
// 6. Actual run budget and training procedure.
{
 const s=slide('4. Hyperparameters','Settings used in the measured full-dataset run','Describe the settings actually executed, rather than only default maximums. Class weights are calculated from training labels alone.');
 const head=result?.head_epochs_requested??3,fine=result?.fine_epochs_requested??2,batch=result?.batch_size??4;
 const values=[['Parameter','Configured value'],['Input size','224 × 224 RGB'],['Batch size',String(batch)],['Optimizer and loss','Adam, binary cross-entropy'],['Head training',`${head} epochs at learning rate 0.001`],['Block5 fine-tuning',`${fine} epochs at learning rate 0.00001`],['Classification head','Dense 128 ReLU, Dropout 0.5'],['Class weights',`Crop ${data.class_weights['0'].toFixed(3)}, Weed ${data.class_weights['1'].toFixed(3)}`],['Early stopping','Validation loss, patience 3'],['LR reduction','Factor 0.5, patience 2'],['Random seed','42']];
 table(s,values,56,150,754,467,[268,486],23);
 text(s,'Phase 1',869,168,345,39,30,C.blue,true);
 text(s,'Freeze the convolution base.\nTrain the new binary head.',869,223,345,102,27);
 text(s,'Phase 2',869,363,345,39,30,C.orange,true);
 text(s,'Enable block5 only.\nRecompile at a lower learning rate.',869,419,345,115,27);
 text(s,'Reload the checkpoint with the lowest validation loss across both phases.',869,561,345,91,22);
 text(s,'Laptop run budget shown above. The code also supports maximum budgets of 10 + 5 epochs.',56,641,754,28,17,C.muted);
}
function historyChart(s,metric){
 const h=history,epochs=h[metric].map((_,i)=>String(i+1));
 // Six decimals preserve the measured curve while fitting Excel's numeric precision.
 // The original TensorFlow values remain unchanged in training_history.json.
 const chartValues=values=>values.map(v=>Number(v.toFixed(6)));
 const chart=s.charts.add('line',{position:{left:53,top:155,width:823,height:464},title:metric==='accuracy'?'Training and validation accuracy':'Training and validation loss',titleTextStyle:{fontSize:25,fill:C.navy,bold:true},categories:epochs,series:[{name:'Training',values:chartValues(h[metric]),line:{fill:C.blue,width:3},marker:{symbol:'circle',size:7,fill:C.blue}},{name:'Validation',values:chartValues(h['val_'+metric]),line:{fill:C.orange,width:3},marker:{symbol:'circle',size:7,fill:C.orange}}],legend:{position:'bottom',overlay:false,textStyle:{fontSize:21}},xAxis:{title:'Epoch',textStyle:{fontSize:20}},yAxis:{title:metric==='accuracy'?'Accuracy':'Binary cross-entropy',numberFormatCode:metric==='accuracy'?'0%':'0.00',min:0,...(metric==='accuracy'?{max:1,majorUnit:.2}:{}),textStyle:{fontSize:20},majorGridlines:{fill:C.line,width:1}},chartFill:C.white,plotAreaFill:C.white});
 applyPresentationChartFont(chart,{fontFamily:font});
 const head=result.head_epochs_completed??result.head_epochs_requested;
 const phase=`Epochs 1–${head}: frozen VGG16. Epochs ${head+1}–${h[metric].length}: block5 fine-tuning.`;
 text(s,phase+(metric==='loss'?'\nTraining loss uses class weights. Validation loss is unweighted.':''),56,metric==='loss'?627:638,822,metric==='loss'?43:26,17,C.muted);
}
// 7. Actual accuracy curve and held-out test result.
{
 const s=slide('5. Results: accuracy','Measured curves and evaluation on the untouched test set','The line chart is editable and uses the generated epoch history. The test set contains 831 images and was excluded from training and checkpoint selection.');
 if(result){
  historyChart(s,'accuracy');metric(s,'Held-out test accuracy',pct(result.test_accuracy),917,158,300,C.blue);
  metric(s,'Test images',String(result.evaluated_test_images),917,301,300,C.cyan);
  text(s,'Evaluation',917,457,300,34,26,C.navy,true);
  text(s,`${result.epochs} measured epochs.\nThreshold: 0.5.\nSeed: ${result.seed}.`,917,507,300,126,25);
 }else pending(s);
}
// 8. Actual loss curve with test loss and AUC.
{
 const s=slide('5. Results: loss','Validation loss selects the best checkpoint across both phases','Explain binary cross-entropy. Discuss the measured training/validation gap without claiming field reliability. AUC measures ranking across thresholds.');
 if(result){
  historyChart(s,'loss');metric(s,'Held-out test loss',num(result.test_loss),917,158,300,C.orange);
  metric(s,'ROC AUC',num(result.auc),917,301,300,C.blue);
  text(s,'Checkpoint selection',917,458,300,40,26,C.navy,true);
  text(s,'The saved model uses the lowest measured validation loss. Test data never selects the checkpoint.',917,508,300,132,24);
 }else pending(s);
}
// 9. Editable confusion matrix and measured class metrics.
{
 const s=slide('5. Results: confusion matrix','Rows are actual labels and columns are predicted labels','Interpret crop images incorrectly predicted as weeds, then compare both classes using precision, recall and F1.');
 if(result){
  const m=result.confusion_matrix;
  text(s,'Actual vs predicted labels',56,153,570,40,28,C.navy,true);
  const t=table(s,[['Actual / Predicted','Crop','Weed'],['Crop',String(m[0][0]),String(m[0][1])],['Weed',String(m[1][0]),String(m[1][1])]],56,216,570,280,[250,160,160],28);
  for(let r=1;r<=2;r++)for(let c=1;c<=2;c++){t.getCell(r,c).fill=r===c?'#d3e8f8':'#fce6cc';t.getCell(r,c).text.style={typeface:font,fontSize:45,color:C.navy,bold:true};}
  const report=result.classification_report;
  const values=[['Class','Precision','Recall','F1'],...['Crop','Weed'].map(label=>[label,...['precision','recall','f1-score'].map(k=>pct(report[label][k]))])];
  table(s,values,684,217,540,222,[120,140,140,140],22);
  text(s,'Errors to inspect',56,541,1150,40,28,C.navy,true);
  text(s,`${m[0][1]} crop images predicted as Weed. ${m[1][0]} weed images predicted as Crop.`,56,597,1140,45,27);
 }else pending(s);
}
// 10. Actual held-out prediction examples with labels and probabilities.
{
 const s=slide('5. Results: sample predictions','Original held-out test images and saved model probabilities','Show both correct and incorrect examples. Explain that probability is the sigmoid Weed score, not a calibrated guarantee.');
 if(result){
  for(const [i,row] of data.examples.entries()){
   const x=56+(i%3)*398,y=139+Math.floor(i/3)*250,correct=row.label===row.predicted_label;
   photo(s,row.relative_path,x,y,360,151,`${row.species}: true ${row.label===0?'Crop':'Weed'}, predicted ${row.predicted_class}`);
   text(s,`${correct?'Correct':'Error'}: ${row.species}`,x,y+156,367,28,21,correct?C.green:C.orange,true);
   text(s,`Actual ${row.label===0?'Crop':'Weed'}  /  Predicted ${row.predicted_class}`,x,y+189,365,28,20);
   text(s,`Weed probability: ${pct(row.weed_probability)}`,x,y+218,365,26,19,C.muted);
  }
 }else pending(s);
}
// 11. Measured outcome and honest limitations.
{
 const s=slide('6. Conclusion','Measured outcome, limitations and future work','Conclude with actual measured test results. Explain that disjoint image paths do not guarantee independent plant identities across growth stages.');
 text(s,'What was implemented',56,158,1140,40,30,C.blue,true);
 text(s,'A complete local VGG16 transfer-learning pipeline with verified data, disjoint splits, saved checkpoints and test predictions.',56,212,1140,90,30);
 text(s,'Measured outcome',56,339,1140,40,30,C.blue,true);
 if(result){
  const baseline=data.splits.test.weed/data.splits.test.total;
  text(s,`${pct(result.test_accuracy)} test accuracy and ${num(result.test_loss)} test loss on ${result.evaluated_test_images} images.`,56,392,1140,44,30);
  text(s,`${result.test_accuracy>baseline?'Accuracy exceeds':'Accuracy does not exceed'} the ${pct(baseline)} majority-Weed baseline on this image split.`,56,446,1140,50,25);
 }else text(s,'Training is running. Measured outcome will populate after evaluation.',56,392,1140,70,26,C.orange);
 text(s,'Limitations and next steps',56,518,1140,40,29,C.blue,true);
 text(s,'Controlled backgrounds and repeated plant identities limit generalization.\nNext: verify plant-level splits, collect field images and tune decision thresholds.',56,572,1140,80,26);
}

const build=path.join(root,draft?'.build/deck-draft':'.build/deck-results');
await fs.mkdir(build,{recursive:true});
for(const [i,s] of slides.entries()){
 const png=await presentation.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(build,'candidate.pptx');
await(await PresentationFile.exportPptx(presentation)).save(candidate);
if(draft){console.log('Internal layout preview saved to '+build);process.exit(0);}
const final=path.join(root,'presentation/Roll_43_VGG16_Presentation_Results.pptx');
await fs.mkdir(path.join(root,'.build/validated'),{recursive:true});
const checked=path.join(root,`.build/validated/results-${Date.now()}.pptx`);
const receipt=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:checked,
 pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...([3,4,6,9].flatMap(n=>['--require-native-table-slide',String(n)]))],explicitTotalSlideCount:11,
 requiredNativeTableOwnerSlides:[3,4,6,9],requiredNativeChartOwnerSlides:[4,7,8],materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(root,`.build/results-validation-${Date.now()}.json`)});
await fs.copyFile(checked,final);console.log('Final presentation: '+final);console.log(JSON.stringify(receipt));
