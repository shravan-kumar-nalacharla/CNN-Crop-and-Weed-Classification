from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "CNN_Crop_Weed_Classification.ipynb"
DOCX_PATH = ROOT / "docs" / "Team_Learning_Guide.docx"


def source_lines(text: str) -> list[str]:
    text = dedent(text).strip("\n") + "\n"
    return text.splitlines(keepends=True)


def markdown_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source_lines(text)}


def code_cell(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines(text),
    }


def build_notebook() -> None:
    cells = [
        markdown_cell(
            """
            # CNN Crop and Weed Classification

            **Assigned roll numbers:** 41-45  
            **Task:** Binary image classification with TensorFlow and Keras

            This notebook downloads the V2 Plant Seedlings Dataset, maps its 12 plant species to **Crop** or **Weed**, creates reproducible train/validation/test splits, trains a custom CNN, and saves the graphs and metrics required for the report and presentation.

            Use a Google Colab GPU. Run the cells from top to bottom and do not report results until the final evaluation cells finish.
            """
        ),
        markdown_cell(
            """
            ## 1 Setup

            The only extra Colab dependency is KaggleHub, which downloads the public dataset. TensorFlow, pandas, scikit-learn, matplotlib, and seaborn are normally preinstalled in Colab.
            """
        ),
        code_cell(
            """
            import importlib.util
            import subprocess
            import sys

            if importlib.util.find_spec("kagglehub") is None:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "kagglehub"])

            import json
            import random
            import re
            from pathlib import Path

            import kagglehub
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            import tensorflow as tf
            from sklearn.metrics import classification_report, confusion_matrix
            from sklearn.model_selection import train_test_split
            from sklearn.utils.class_weight import compute_class_weight

            SEED = 42
            random.seed(SEED)
            np.random.seed(SEED)
            tf.keras.utils.set_random_seed(SEED)

            PROJECT_ROOT = Path.cwd()
            if PROJECT_ROOT.name == "notebooks":
                PROJECT_ROOT = PROJECT_ROOT.parent

            OUTPUT_DIR = PROJECT_ROOT / "outputs"
            MODEL_DIR = PROJECT_ROOT / "models"
            LOCAL_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "plant_seedlings"
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            MODEL_DIR.mkdir(parents=True, exist_ok=True)

            print("TensorFlow:", tf.__version__)
            print("GPU devices:", tf.config.list_physical_devices("GPU"))
            print("Project root:", PROJECT_ROOT)
            """
        ),
        markdown_cell(
            """
            ## 2 Download and locate the dataset

            The dataset contains 5,539 RGB seedling images in 12 species folders. If `data/raw/plant_seedlings` already contains those folders, the notebook uses the local copy. Otherwise it downloads the public Kaggle dataset `vbookshelf/v2-plant-seedlings-dataset`.
            """
        ),
        code_cell(
            """
            DATASET_HANDLE = "vbookshelf/v2-plant-seedlings-dataset"

            if LOCAL_DATA_DIR.exists() and any(LOCAL_DATA_DIR.rglob("*.png")):
                DATASET_ROOT = LOCAL_DATA_DIR
                print("Using local dataset:", DATASET_ROOT)
            else:
                DATASET_ROOT = Path(kagglehub.dataset_download(DATASET_HANDLE))
                print("Downloaded dataset:", DATASET_ROOT)
            """
        ),
        markdown_cell(
            """
            ## 3 Convert 12 species into Crop and Weed

            Crop species are Maize, Common wheat, and Sugar beet. All other species are weeds. Label `0` means Crop and label `1` means Weed, so the sigmoid output is the estimated probability of Weed.
            """
        ),
        code_cell(
            """
            CROP_SPECIES = {"maize", "common_wheat", "sugar_beet"}
            EXPECTED_SPECIES = {
                "black_grass", "charlock", "cleavers", "common_chickweed",
                "common_wheat", "fat_hen", "loose_silkybent", "maize",
                "scentless_mayweed", "shepherds_purse",
                "small_flowered_cranesbill", "sugar_beet",
            }
            IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

            def normalize_species(name):
                normalized = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
                aliases = {
                    "blackgrass": "black_grass",
                    "commonwheat": "common_wheat",
                    "fathen": "fat_hen",
                    "loose_silky_bent": "loose_silkybent",
                    "loosesilkybent": "loose_silkybent",
                    "scentlessmayweed": "scentless_mayweed",
                    "shepherd_s_purse": "shepherds_purse",
                    "shepherdspurse": "shepherds_purse",
                    "smallflowered_cranesbill": "small_flowered_cranesbill",
                    "sugarbeet": "sugar_beet",
                }
                return aliases.get(normalized, normalized)

            rows = []
            for path in DATASET_ROOT.rglob("*"):
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                    species = normalize_species(path.parent.name)
                    if species in EXPECTED_SPECIES:
                        binary_name = "Crop" if species in CROP_SPECIES else "Weed"
                        rows.append({
                            "path": str(path),
                            "species": species,
                            "label_name": binary_name,
                            "label": 0 if binary_name == "Crop" else 1,
                        })

            images = pd.DataFrame(rows).drop_duplicates(subset="path").reset_index(drop=True)
            found_species = set(images["species"].unique())

            assert len(images) >= 5_000, f"Expected about 5,539 images, found {len(images)}"
            assert found_species == EXPECTED_SPECIES, (
                f"Species mismatch. Missing={EXPECTED_SPECIES - found_species}; "
                f"unexpected={found_species - EXPECTED_SPECIES}"
            )

            print("Images:", len(images))
            display(images.head())
            display(images.groupby(["label_name", "species"]).size().rename("images").to_frame())
            """
        ),
        markdown_cell("## 4 Explore the dataset"),
        code_cell(
            """
            sns.set_theme(style="whitegrid")

            class_counts = images["label_name"].value_counts().reindex(["Crop", "Weed"])
            ax = class_counts.plot(kind="bar", color=["#2E7D32", "#C45A31"], figsize=(6, 4))
            ax.set_title("Crop and Weed Image Distribution")
            ax.set_xlabel("Class")
            ax.set_ylabel("Number of images")
            ax.tick_params(axis="x", rotation=0)
            for container in ax.containers:
                ax.bar_label(container)
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "class_distribution.png", dpi=200)
            plt.show()

            samples = images.groupby("label_name", group_keys=False).sample(n=4, random_state=SEED)
            fig, axes = plt.subplots(2, 4, figsize=(12, 6))
            for ax, row in zip(axes.flat, samples.itertuples()):
                image = tf.keras.utils.load_img(row.path)
                ax.imshow(image)
                ax.set_title(f"{row.label_name}\\n{row.species.replace('_', ' ').title()}")
                ax.axis("off")
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "sample_images.png", dpi=200)
            plt.show()
            """
        ),
        markdown_cell(
            """
            ## 5 Create reproducible splits

            Stratification preserves the Crop/Weed proportion. The 70/15/15 split is performed before augmentation. The assertions prove that no file appears in more than one split.
            """
        ),
        code_cell(
            """
            train_df, remaining_df = train_test_split(
                images,
                test_size=0.30,
                random_state=SEED,
                stratify=images["label"],
            )
            val_df, test_df = train_test_split(
                remaining_df,
                test_size=0.50,
                random_state=SEED,
                stratify=remaining_df["label"],
            )

            train_paths = set(train_df["path"])
            val_paths = set(val_df["path"])
            test_paths = set(test_df["path"])
            assert train_paths.isdisjoint(val_paths)
            assert train_paths.isdisjoint(test_paths)
            assert val_paths.isdisjoint(test_paths)
            assert len(train_df) + len(val_df) + len(test_df) == len(images)

            split_table = pd.concat([
                train_df.assign(split="train"),
                val_df.assign(split="validation"),
                test_df.assign(split="test"),
            ], ignore_index=True)
            split_table.to_csv(OUTPUT_DIR / "dataset_splits.csv", index=False)
            display(pd.crosstab(split_table["split"], split_table["label_name"], margins=True))
            """
        ),
        markdown_cell("## 6 Build the TensorFlow input pipeline"),
        code_cell(
            """
            IMAGE_SIZE = (128, 128)
            BATCH_SIZE = 32
            AUTOTUNE = tf.data.AUTOTUNE

            def load_image(path, label):
                image_bytes = tf.io.read_file(path)
                image = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
                image.set_shape([None, None, 3])
                image = tf.image.resize(image, IMAGE_SIZE)
                image = tf.cast(image, tf.float32) / 255.0
                return image, tf.cast(label, tf.float32)

            def make_dataset(frame, training=False):
                dataset = tf.data.Dataset.from_tensor_slices(
                    (frame["path"].values, frame["label"].values)
                )
                if training:
                    dataset = dataset.shuffle(len(frame), seed=SEED, reshuffle_each_iteration=True)
                dataset = dataset.map(load_image, num_parallel_calls=AUTOTUNE)
                dataset = dataset.batch(BATCH_SIZE).prefetch(AUTOTUNE)
                return dataset

            train_ds = make_dataset(train_df, training=True)
            val_ds = make_dataset(val_df)
            test_ds = make_dataset(test_df)

            weights = compute_class_weight(
                class_weight="balanced",
                classes=np.array([0, 1]),
                y=train_df["label"].to_numpy(),
            )
            CLASS_WEIGHTS = {0: float(weights[0]), 1: float(weights[1])}
            print("Class weights:", CLASS_WEIGHTS)
            """
        ),
        markdown_cell(
            """
            ## 7 Build the CNN

            Augmentation is part of the model and is active only during training. Three convolution blocks learn progressively richer visual features. Dropout reduces overfitting. The final sigmoid neuron returns Weed probability.
            """
        ),
        code_cell(
            """
            augmentation = tf.keras.Sequential([
                tf.keras.layers.RandomFlip("horizontal", seed=SEED),
                tf.keras.layers.RandomRotation(0.08, seed=SEED),
                tf.keras.layers.RandomZoom(0.10, seed=SEED),
                tf.keras.layers.RandomTranslation(0.05, 0.05, seed=SEED),
            ], name="augmentation")

            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(*IMAGE_SIZE, 3)),
                augmentation,
                tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu"),
                tf.keras.layers.MaxPooling2D(),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(128, activation="relu"),
                tf.keras.layers.Dropout(0.50, seed=SEED),
                tf.keras.layers.Dense(1, activation="sigmoid"),
            ], name="crop_weed_cnn")

            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                loss="binary_crossentropy",
                metrics=[
                    "accuracy",
                    tf.keras.metrics.Precision(name="precision"),
                    tf.keras.metrics.Recall(name="recall"),
                    tf.keras.metrics.AUC(name="auc"),
                ],
            )
            model.summary()
            """
        ),
        markdown_cell("## 8 Train and save the best model"),
        code_cell(
            """
            BEST_MODEL_PATH = MODEL_DIR / "best_crop_weed_cnn.keras"

            callbacks = [
                tf.keras.callbacks.ModelCheckpoint(
                    BEST_MODEL_PATH,
                    monitor="val_loss",
                    save_best_only=True,
                ),
                tf.keras.callbacks.EarlyStopping(
                    monitor="val_loss",
                    patience=4,
                    restore_best_weights=True,
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor="val_loss",
                    factor=0.5,
                    patience=2,
                    min_lr=1e-6,
                ),
            ]

            history = model.fit(
                train_ds,
                validation_data=val_ds,
                epochs=20,
                class_weight=CLASS_WEIGHTS,
                callbacks=callbacks,
            )
            """
        ),
        markdown_cell("## 9 Plot accuracy and loss"),
        code_cell(
            """
            epochs_run = range(1, len(history.history["loss"]) + 1)

            plt.figure(figsize=(7, 5))
            plt.plot(epochs_run, history.history["accuracy"], marker="o", label="Training")
            plt.plot(epochs_run, history.history["val_accuracy"], marker="o", label="Validation")
            plt.xlabel("Epoch")
            plt.ylabel("Accuracy")
            plt.title("CNN Training and Validation Accuracy")
            plt.legend()
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "accuracy_graph.png", dpi=200)
            plt.show()

            plt.figure(figsize=(7, 5))
            plt.plot(epochs_run, history.history["loss"], marker="o", label="Training")
            plt.plot(epochs_run, history.history["val_loss"], marker="o", label="Validation")
            plt.xlabel("Epoch")
            plt.ylabel("Binary Cross-Entropy Loss")
            plt.title("CNN Training and Validation Loss")
            plt.legend()
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "loss_graph.png", dpi=200)
            plt.show()
            """
        ),
        markdown_cell(
            """
            ## 10 Final test evaluation

            The test set is used here for the first time. Because label 1 is Weed, Keras precision and recall describe the Weed class. The classification report gives separate values for Crop and Weed.
            """
        ),
        code_cell(
            """
            best_model = tf.keras.models.load_model(BEST_MODEL_PATH)
            evaluation = best_model.evaluate(test_ds, return_dict=True, verbose=1)

            probabilities = best_model.predict(test_ds, verbose=1).ravel()
            predictions = (probabilities >= 0.5).astype(int)
            actual = test_df["label"].to_numpy()

            report = classification_report(
                actual,
                predictions,
                target_names=["Crop", "Weed"],
                output_dict=True,
                zero_division=0,
            )
            report_df = pd.DataFrame(report).transpose()
            report_df.to_csv(OUTPUT_DIR / "classification_report.csv")

            summary = {
                "random_seed": SEED,
                "train_images": int(len(train_df)),
                "validation_images": int(len(val_df)),
                "test_images": int(len(test_df)),
                "epochs_completed": int(len(history.history["loss"])),
                "test_loss": float(evaluation["loss"]),
                "test_accuracy": float(evaluation["accuracy"]),
                "test_auc": float(evaluation["auc"]),
                "crop_precision": float(report["Crop"]["precision"]),
                "crop_recall": float(report["Crop"]["recall"]),
                "crop_f1": float(report["Crop"]["f1-score"]),
                "weed_precision": float(report["Weed"]["precision"]),
                "weed_recall": float(report["Weed"]["recall"]),
                "weed_f1": float(report["Weed"]["f1-score"]),
            }
            (OUTPUT_DIR / "results_summary.json").write_text(
                json.dumps(summary, indent=2), encoding="utf-8"
            )

            print(json.dumps(summary, indent=2))
            display(report_df)
            """
        ),
        markdown_cell("## 11 Confusion matrix"),
        code_cell(
            """
            matrix = confusion_matrix(actual, predictions)
            plt.figure(figsize=(6, 5))
            sns.heatmap(
                matrix,
                annot=True,
                fmt="d",
                cmap="Greens",
                xticklabels=["Crop", "Weed"],
                yticklabels=["Crop", "Weed"],
            )
            plt.xlabel("Predicted label")
            plt.ylabel("Actual label")
            plt.title("Crop and Weed Confusion Matrix")
            plt.tight_layout()
            plt.savefig(OUTPUT_DIR / "confusion_matrix.png", dpi=200)
            plt.show()
            """
        ),
        markdown_cell("## 12 Sample predictions and error analysis"),
        code_cell(
            """
            results = test_df.reset_index(drop=True).copy()
            results["probability_weed"] = probabilities
            results["prediction"] = predictions
            results["predicted_name"] = np.where(predictions == 1, "Weed", "Crop")
            results["correct"] = results["label"].to_numpy() == predictions
            results.to_csv(OUTPUT_DIR / "test_predictions.csv", index=False)

            def plot_examples(frame, filename, title, count=12):
                chosen = frame.head(count)
                if chosen.empty:
                    print(f"No images available for {title}")
                    return
                columns = 4
                rows = int(np.ceil(len(chosen) / columns))
                fig, axes = plt.subplots(rows, columns, figsize=(12, 3.2 * rows))
                axes = np.atleast_1d(axes).ravel()
                for ax in axes:
                    ax.axis("off")
                for ax, row in zip(axes, chosen.itertuples()):
                    ax.imshow(tf.keras.utils.load_img(row.path))
                    ax.set_title(
                        f"Actual: {row.label_name}\\nPredicted: {row.predicted_name}\\n"
                        f"P(Weed): {row.probability_weed:.2f}",
                        color="green" if row.correct else "red",
                    )
                    ax.axis("off")
                fig.suptitle(title, fontsize=15)
                plt.tight_layout()
                plt.savefig(OUTPUT_DIR / filename, dpi=200, bbox_inches="tight")
                plt.show()

            plot_examples(
                results.sample(n=min(12, len(results)), random_state=SEED),
                "sample_predictions.png",
                "Sample Test Predictions",
            )
            plot_examples(
                results.loc[~results["correct"]].sort_values("probability_weed"),
                "misclassified_examples.png",
                "Misclassified Test Images",
            )
            """
        ),
        markdown_cell(
            """
            ## 13 Predict one new image

            Change `IMAGE_TO_PREDICT` to any PNG or JPG. The result is a model prediction, not agricultural advice; field conditions may differ from this controlled dataset.
            """
        ),
        code_cell(
            """
            def predict_one(image_path):
                image = tf.keras.utils.load_img(image_path, target_size=IMAGE_SIZE)
                array = tf.keras.utils.img_to_array(image) / 255.0
                probability_weed = float(best_model.predict(array[None, ...], verbose=0)[0, 0])
                label = "Weed" if probability_weed >= 0.5 else "Crop"
                confidence = probability_weed if label == "Weed" else 1.0 - probability_weed
                return {"prediction": label, "confidence": confidence, "probability_weed": probability_weed}

            IMAGE_TO_PREDICT = test_df.iloc[0]["path"]
            print(predict_one(IMAGE_TO_PREDICT))
            """
        ),
        markdown_cell(
            """
            ## 14 What to copy into the report and PPT

            Use `results_summary.json` for all numbers. Use `accuracy_graph.png`, `loss_graph.png`, `confusion_matrix.png`, `sample_predictions.png`, and `misclassified_examples.png` as figures. State that the system classifies isolated seedling images and has not been validated on crowded real-field scenes.
            """
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"name": "CNN Crop Weed Classification.ipynb", "provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=1), encoding="utf-8")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    tc_pr.append(shading)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = tc_mar.find(qn(f"w:{margin}"))
        if element is None:
            element = OxmlElement(f"w:{margin}")
            tc_mar.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def set_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), "4")
        tag.set(qn("w:color"), "D9D9D9")


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    header = table.rows[0]
    set_repeat_table_header(header)
    for index, text in enumerate(headers):
        cell = header.cells[index]
        cell.text = str(text)
        shade_cell(cell, "1F4E78")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(9.5)
        set_cell_margins(cell)
    for row_index, row_values in enumerate(rows):
        row = table.add_row()
        for index, text in enumerate(row_values):
            cell = row.cells[index]
            cell.text = str(text)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index % 2:
                shade_cell(cell, "EAF2F8")
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)
            set_cell_margins(cell)
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_bullet(doc, text, level=0):
    paragraph = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    paragraph.add_run(text)
    return paragraph


def add_number(doc, text):
    paragraph = doc.add_paragraph(style="List Number")
    paragraph.add_run(text)
    return paragraph


def build_docx() -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.78)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"].paragraph_format.space_after = Pt(6)
    styles["Normal"].paragraph_format.line_spacing = 1.08

    for style_name, size in (("Title", 25), ("Heading 1", 17), ("Heading 2", 13)):
        style = styles[style_name]
        style.font.name = "Aptos Display"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True

    styles["Heading 1"].paragraph_format.space_before = Pt(10)
    styles["Heading 1"].paragraph_format.space_after = Pt(6)
    styles["Heading 1"].paragraph_format.keep_with_next = True
    styles["Heading 2"].paragraph_format.space_before = Pt(8)
    styles["Heading 2"].paragraph_format.space_after = Pt(4)
    styles["Heading 2"].paragraph_format.keep_with_next = True

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer.add_run("CNN Crop and Weed Classification  |  Roll Numbers 41-45")
    footer_run.font.size = Pt(8)
    footer_run.font.color.rgb = RGBColor(89, 89, 89)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("CNN Crop and Weed Classification")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("Team Learning and Implementation Guide")
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(31, 78, 120)
    doc.add_paragraph()
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run("Study Project  |  Roll Numbers 41-45\n").bold = True
    info.add_run("Deep Learning  |  B Tech IV Year I Semester")
    doc.add_paragraph()
    opening = doc.add_paragraph()
    opening.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    opening.add_run(
        "This guide gives the whole team one shared explanation of the project and one reproducible way to build it. "
        "The project trains a binary Convolutional Neural Network to classify isolated seedling images as Crop or Weed. "
        "The accompanying notebook is the source of truth for every graph and result used in the report and presentation."
    )
    doc.add_paragraph()
    add_table(
        doc,
        ["Project decision", "Selected value"],
        [
            ["Dataset", "V2 Plant Seedlings Dataset"],
            ["Task", "Binary image classification"],
            ["Classes", "Crop and Weed"],
            ["Framework", "TensorFlow and Keras"],
            ["Random seed", "42"],
            ["Presentation", "10 minutes"],
        ],
        [2.2, 4.2],
    )

    doc.add_page_break()
    doc.add_heading("Project Overview", level=1)
    doc.add_heading("Problem Statement", level=2)
    doc.add_paragraph(
        "Manual identification of crops and weeds at the seedling stage is time-consuming and can be inconsistent. "
        "This project develops a CNN that receives one RGB seedling image and predicts whether it is a crop or a weed. "
        "The result demonstrates the image-classification step needed in a precision weed-management system."
    )
    doc.add_heading("Objectives", level=2)
    for text in [
        "Prepare a reproducible binary Crop and Weed dataset from 12 labelled plant species.",
        "Build a CNN using convolution, pooling, dense, and dropout layers.",
        "Limit overfitting with augmentation, dropout, early stopping, and learning-rate reduction.",
        "Evaluate unseen images using accuracy, precision, recall, F1-score, AUC, and a confusion matrix.",
        "Save the trained model and all figures needed for the report and presentation.",
    ]:
        add_bullet(doc, text)
    doc.add_heading("What the model does and does not do", level=2)
    doc.add_paragraph(
        "The model classifies a single isolated plant image. It does not locate multiple plants inside a field photograph, "
        "segment leaves, recommend herbicide, or prove real-field performance. Those tasks require additional data and a "
        "different detection or segmentation system."
    )

    doc.add_page_break()
    doc.add_heading("Dataset and Labels", level=1)
    doc.add_paragraph(
        "The V2 Plant Seedlings Dataset contains 5,539 RGB images across 12 species and multiple early growth stages. "
        "The original data was recorded at Aarhus University Flakkebjerg Research Station in collaboration with the "
        "University of Southern Denmark. The dataset is distributed under CC BY-SA 4.0."
    )
    add_table(
        doc,
        ["Binary label", "Original species"],
        [
            ["Crop", "Maize; Common wheat; Sugar beet"],
            [
                "Weed",
                "Black-grass; Charlock; Cleavers; Common chickweed; Fat hen; Loose silky-bent; "
                "Scentless mayweed; Shepherd's purse; Small-flowered cranesbill",
            ],
        ],
        [1.25, 5.15],
    )
    doc.add_heading("Why class imbalance matters", level=2)
    doc.add_paragraph(
        "The dataset contains about 973 crop images and 4,566 weed images. A classifier that predicts Weed for every image "
        "would appear to achieve about 82.4 percent accuracy while failing completely on crops. The notebook therefore "
        "computes balanced class weights and reports metrics for each class instead of relying on accuracy alone."
    )
    doc.add_heading("Data split", level=2)
    add_table(
        doc,
        ["Split", "Purpose", "Share"],
        [
            ["Training", "Learns CNN weights", "70%"],
            ["Validation", "Selects the best epoch and controls overfitting", "15%"],
            ["Testing", "Measures final performance once", "15%"],
        ],
        [1.2, 4.2, 1.0],
    )
    doc.add_paragraph(
        "The split is stratified and uses seed 42. Augmentation is applied after splitting and only to training images. "
        "This prevents augmented versions of a test image from leaking into training."
    )

    doc.add_page_break()
    doc.add_heading("How the CNN Works", level=1)
    doc.add_heading("Convolution", level=2)
    doc.add_paragraph(
        "A convolution filter slides across an image and learns local patterns. Early filters often respond to edges and "
        "colour transitions. Deeper filters combine them into leaf contours, textures, and species-related shapes. The same "
        "filter is reused across the image, making CNNs more efficient than connecting every pixel to every neuron."
    )
    doc.add_heading("Pooling", level=2)
    doc.add_paragraph(
        "Max pooling reduces feature-map width and height while keeping strong responses. It lowers computation and makes "
        "small changes in plant position less important."
    )
    doc.add_heading("Dense output", level=2)
    doc.add_paragraph(
        "After feature extraction, a dense layer combines the learned evidence. Dropout randomly disables half of its units "
        "during training to reduce overfitting. The final sigmoid unit returns the probability of Weed. A value below 0.5 "
        "is Crop and a value at or above 0.5 is Weed."
    )
    doc.add_heading("Architecture", level=2)
    add_table(
        doc,
        ["Stage", "Layer", "Purpose"],
        [
            ["Input", "128 x 128 x 3 RGB", "Standard image size"],
            ["Training only", "Flip, rotation, zoom, translation", "Adds realistic variation"],
            ["Block 1", "Conv2D 32 plus MaxPool", "Learns basic edges and colour patterns"],
            ["Block 2", "Conv2D 64 plus MaxPool", "Learns combinations of simple features"],
            ["Block 3", "Conv2D 128 plus MaxPool", "Learns richer plant features"],
            ["Classifier", "Flatten, Dense 128, Dropout 0.5", "Combines visual evidence"],
            ["Output", "Dense 1 with sigmoid", "Produces Weed probability"],
        ],
        [1.05, 2.3, 3.05],
    )

    doc.add_page_break()
    doc.add_heading("Notebook Walkthrough", level=1)
    steps = [
        "Setup imports, folders, and random seed 42.",
        "Use a local dataset if present; otherwise download the public Kaggle dataset.",
        "Find images inside the 12 species folders and validate that every expected species exists.",
        "Map species to Crop or Weed and generate class-distribution and sample-image figures.",
        "Create stratified 70/15/15 splits and assert that no file overlaps between them.",
        "Build efficient TensorFlow datasets that resize and normalize images.",
        "Compute balanced class weights from training labels.",
        "Build and compile the CNN with Adam and binary cross-entropy.",
        "Train for at most 20 epochs using checkpointing, early stopping, and learning-rate reduction.",
        "Reload the best model and evaluate the untouched test set.",
        "Save metrics, graphs, predictions, errors, and the trained model.",
    ]
    for step in steps:
        add_number(doc, step)
    doc.add_heading("Hyperparameters", level=2)
    add_table(
        doc,
        ["Hyperparameter", "Value", "Reason"],
        [
            ["Input size", "128 x 128 RGB", "Enough shape detail with manageable training cost"],
            ["Batch size", "32", "Stable default for a Colab GPU"],
            ["Maximum epochs", "20", "Early stopping normally ends training sooner"],
            ["Optimizer", "Adam", "Reliable adaptive optimization"],
            ["Learning rate", "0.001", "Standard Adam starting value"],
            ["Loss", "Binary cross-entropy", "Correct for one sigmoid binary output"],
            ["Dropout", "0.50", "Reduces overfitting in the dense classifier"],
            ["Seed", "42", "Standard reproducible experiment seed"],
        ],
        [1.35, 1.3, 3.75],
    )

    doc.add_page_break()
    doc.add_heading("Understanding the Results", level=1)
    add_table(
        doc,
        ["Result", "How to interpret it"],
        [
            ["Training accuracy", "How well the model fits the images used to update its weights"],
            ["Validation accuracy", "How well the current model generalizes during training"],
            ["Training loss", "Prediction error on training data; lower is better"],
            ["Validation loss", "Primary model-selection signal; rising loss can indicate overfitting"],
            ["Precision", "Of images predicted as a class, the fraction that is correct"],
            ["Recall", "Of all true images in a class, the fraction found by the model"],
            ["F1-score", "Balance between precision and recall"],
            ["Confusion matrix", "Counts of correct and incorrect Crop and Weed predictions"],
            ["AUC", "Ability to rank Crop and Weed across classification thresholds"],
        ],
        [1.55, 4.85],
    )
    doc.add_heading("Recognizing overfitting", level=2)
    doc.add_paragraph(
        "If training accuracy continues to improve while validation accuracy stops improving, or if validation loss rises, "
        "the model is memorizing training details. Augmentation, dropout, early stopping, and reduced learning rate help. "
        "The checkpoint keeps the epoch with the lowest validation loss rather than simply keeping the last epoch."
    )
    doc.add_heading("How to write the final result", level=2)
    doc.add_paragraph(
        "Use the generated results_summary.json and classification_report.csv. State the test accuracy, Crop recall, Weed "
        "recall, F1-scores, AUC, number of completed epochs, and the main pattern in the confusion matrix. Never copy a "
        "percentage from the sample report or another notebook."
    )

    doc.add_page_break()
    doc.add_heading("Running the Project", level=1)
    doc.add_heading("Google Colab procedure", level=2)
    for text in [
        "Open Google Colab and upload notebooks/CNN_Crop_Weed_Classification.ipynb.",
        "Choose Runtime, Change runtime type, and select a T4 GPU.",
        "Run all cells in order. The dataset download is approximately 1.7 GB.",
        "Confirm that the notebook finds 5,539 images and all 12 species.",
        "Wait for training and evaluation to finish without changing the test set.",
        "Download the models and outputs folders before the Colab session expires.",
    ]:
        add_number(doc, text)
    doc.add_heading("Generated files", level=2)
    add_table(
        doc,
        ["File", "Use"],
        [
            ["best_crop_weed_cnn.keras", "Saved best model"],
            ["accuracy_graph.png", "Required training and validation accuracy graph"],
            ["loss_graph.png", "Required training and validation loss graph"],
            ["confusion_matrix.png", "Class-wise evaluation"],
            ["sample_predictions.png", "Visual examples for report and PPT"],
            ["misclassified_examples.png", "Error analysis and limitations"],
            ["classification_report.csv", "Precision, recall, and F1-score"],
            ["results_summary.json", "Authoritative final metrics"],
        ],
        [2.55, 3.85],
    )
    doc.add_heading("Common problems", level=2)
    add_table(
        doc,
        ["Problem", "Action"],
        [
            ["Kaggle download fails", "Sign in to Kaggle or manually place the 12 folders under data/raw/plant_seedlings"],
            ["No GPU is shown", "Change the Colab runtime to T4 GPU and restart the session"],
            ["Out of memory", "Reduce batch size from 32 to 16"],
            ["Species assertion fails", "Check that folder names and extraction are complete"],
            ["Validation loss rises", "Keep the checkpointed best model; do not extend training automatically"],
            ["Colab disconnects", "Download outputs after training or copy the project to Google Drive"],
        ],
        [1.8, 4.6],
    )

    doc.add_page_break()
    doc.add_heading("Team Preparation", level=1)
    doc.add_heading("Suggested responsibilities", level=2)
    add_table(
        doc,
        ["Member", "Primary explanation"],
        [
            ["Roll 41", "Problem statement, motivation, and objectives"],
            ["Roll 42", "Dataset, label mapping, split, and augmentation"],
            ["Roll 43", "CNN architecture and hyperparameters"],
            ["Roll 44", "Accuracy, loss, confusion matrix, and metrics"],
            ["Roll 45", "Conclusion, limitations, future work, and file checks"],
        ],
        [1.25, 5.15],
    )
    doc.add_paragraph(
        "Every member should still understand the complete workflow. All students from roll numbers 41-45 should be able to connect all sections, "
        "explain why class weighting was used, and distinguish validation results from final test results."
    )
    doc.add_heading("Ten minute presentation flow", level=2)
    add_table(
        doc,
        ["Slide", "Topic", "Target time"],
        [
            ["1", "Title and team", "20 seconds"],
            ["2", "Problem and objectives", "50 seconds"],
            ["3", "Dataset and labels", "60 seconds"],
            ["4", "Preprocessing and split", "60 seconds"],
            ["5", "CNN architecture", "80 seconds"],
            ["6", "Hyperparameters and training", "50 seconds"],
            ["7", "Accuracy and loss graphs", "90 seconds"],
            ["8", "Confusion matrix and predictions", "70 seconds"],
            ["9", "Conclusion and limitations", "60 seconds"],
            ["10", "Questions", "Remaining time"],
        ],
        [0.7, 4.25, 1.45],
    )

    doc.add_page_break()
    doc.add_heading("Viva Questions", level=1)
    qa = [
        ("Why use a CNN?", "It learns spatial image features with shared filters and far fewer connections than a fully connected network over all pixels."),
        ("Why binary cross-entropy?", "The model has two classes represented by one sigmoid probability."),
        ("Why use class weights?", "Crop is the minority class, so weighting prevents the larger Weed class from dominating the loss."),
        ("Why separate validation and test sets?", "Validation guides training decisions; the untouched test set estimates final generalization."),
        ("Why normalize pixels?", "Scaling values from 0-255 to 0-1 makes optimization more stable."),
        ("Why augment only training images?", "Augmentation teaches variation. Validation and test images must remain fixed for fair measurement."),
        ("What does dropout do?", "It randomly disables units during training to reduce reliance on specific internal features."),
        ("Why early stopping?", "It stops when validation loss no longer improves and avoids unnecessary overfitting."),
        ("What is the main limitation?", "The dataset mainly contains isolated seedlings under controlled conditions rather than crowded field scenes."),
        ("How could the project improve?", "Collect local field images and train an object detector or segmentation model that locates multiple plants."),
    ]
    for question, answer in qa:
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.keep_together = True
        paragraph.add_run(question + " ").bold = True
        paragraph.add_run(answer)

    doc.add_heading("Final Checklist", level=1)
    for text in [
        "All notebook cells ran in order without errors.",
        "All 12 species and both binary classes were found.",
        "The best model and every required graph were downloaded.",
        "Report metrics match results_summary.json exactly.",
        "Accuracy and loss graphs appear in both report and PPT.",
        "The confusion matrix and sample predictions are explained, not merely displayed.",
        "The report stays within 20 one-sided pages.",
        "The team can finish the presentation within 9 minutes.",
    ]:
        add_bullet(doc, text)

    doc.add_heading("References", level=1)
    references = [
        "Aarhus University. Plant Seedlings Dataset. https://vision.eng.au.dk/plant-seedlings-dataset/",
        "Giselsson, T. M. et al. A Public Image Database for Benchmark of Plant Seedling Classification Algorithms. 2017. https://arxiv.org/abs/1711.05458",
        "V2 Plant Seedlings Dataset. Kaggle. https://www.kaggle.com/datasets/vbookshelf/v2-plant-seedlings-dataset",
        "TensorFlow. Image Classification Tutorial. https://www.tensorflow.org/tutorials/images/classification",
    ]
    for reference in references:
        add_bullet(doc, reference)

    doc.core_properties.title = "CNN Crop and Weed Classification Team Learning Guide"
    doc.core_properties.subject = "Deep Learning Study Project"
    doc.core_properties.author = "Roll Numbers 41-45 Project Team"
    DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(DOCX_PATH)


if __name__ == "__main__":
    build_notebook()
    build_docx()
    print(NOTEBOOK_PATH)
    print(DOCX_PATH)

