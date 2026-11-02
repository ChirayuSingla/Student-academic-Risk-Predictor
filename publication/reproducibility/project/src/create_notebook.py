"""Create a clean optional notebook that reads real data and executed result artifacts."""
import json
from .config import ROOT


def main():
    cells = []

    def markdown(source):
        cells.append({"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)})

    def code(source):
        cells.append({"cell_type": "code", "metadata": {}, "source": source.splitlines(keepends=True),
                      "execution_count": None, "outputs": []})

    markdown("# UCI student academic risk: inspect the real experiment\n"
             "This optional notebook reads the original data and actual saved results. "
             "Outputs are intentionally cleared. Run `python -m src.run_pipeline` from the project root first. "
             "No synthetic data is created. All grade columns are excluded from model inputs.")
    code("from pathlib import Path\nimport sys, json\nimport pandas as pd\n"
         "root = Path.cwd().resolve()\nif not (root / 'src').exists():\n    root = root.parent\n"
         "sys.path.insert(0, str(root))\nfrom src.data import load_data, split_data\n"
         "from src.config import FEATURES, EXCLUDED\nframe, X, y = load_data()\n"
         "assert not set(EXCLUDED) & set(X.columns)\nprint(frame.shape, y.value_counts().sort_index())\nX.head()")
    markdown("## Training-only exploration\nThe test labels are not used for feature selection, preprocessing or tuning.")
    code("X_train, X_test, y_train, y_test = split_data(X, y)\n"
         "print('Training / test:', len(X_train), len(X_test))\n"
         "X_train.assign(at_risk=y_train).groupby('failures').at_risk.agg(['count', 'mean'])")
    markdown("## Actual held-out metrics and training-only selection\n"
             "Precision, recall and F1 are for At Risk. F2 was used for CV selection; test outcomes do not choose the default.")
    code("metadata = json.loads((root / 'models/metadata.json').read_text(encoding='utf-8'))\n"
         "print('Training CV selected:', metadata['selected_model'])\n"
         "pd.read_csv(root / 'results/metrics_summary.csv')")
    code("pd.read_csv(root / 'results/logistic_regression_cv_results.csv').sort_values('mean_test_f2', ascending=False).head()")
    code("from IPython.display import Image, display\n"
         "for name in ['class_distribution.png', 'roc_curves.png', 'precision_recall_curves.png',\n"
         "             'logistic_regression_coefficients.png', 'decision_tree_feature_importance.png']:\n"
         "    display(Image(filename=str(root / 'results/figures' / name)))")
    markdown("## Verify results and read limitations\nUCI feature timing is not established, especially total absences. "
             "Coefficients and tree importance show associations, not causes. Probabilities are uncalibrated. "
             "This prototype must not be the sole basis for academic decisions. "
             "See `results/report.md` for the full executed report and dataset/paper citations.")
    code("from src.verify import verify\nverify()")
    notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.12"}}, "nbformat": 4, "nbformat_minor": 5}
    for i, cell in enumerate(cells):
        cell["id"] = f"cell-{i:02d}"
    (ROOT / "notebooks").mkdir(exist_ok=True)
    (ROOT / "notebooks" / "01_explore_results.ipynb").write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
