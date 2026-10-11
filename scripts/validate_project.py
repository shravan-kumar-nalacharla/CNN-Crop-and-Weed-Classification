from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "CNN_Crop_Weed_Classification.ipynb"


def main() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / "data" / "README.md",
        ROOT / "docs" / "Team_Learning_Guide.md",
        ROOT / "docs" / "Dataset_Sources.md",
        NOTEBOOK,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"Missing required files: {missing}"

    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) >= 15

    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    for index, cell in enumerate(code_cells, start=1):
        source = "".join(cell["source"])
        ast.parse(source, filename=f"notebook-code-cell-{index}")

    joined = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    for required_text in [
        "vbookshelf/v2-plant-seedlings-dataset",
        '"loose_silky_bent": "loose_silkybent"',
        "random_state=SEED",
        "class_weight=CLASS_WEIGHTS",
        "accuracy_graph.png",
        "loss_graph.png",
        "confusion_matrix.png",
        "results_summary.json",
    ]:
        assert required_text in joined, f"Notebook is missing: {required_text}"

    print(f"Validated {NOTEBOOK}")
    print(f"Code cells compiled: {len(code_cells)}")


if __name__ == "__main__":
    main()

