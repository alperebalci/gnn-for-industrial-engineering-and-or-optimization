"""Offline checks for notebook integrity validation."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_learning_materials import validate_notebook


class NotebookIntegrityTests(unittest.TestCase):
    def test_valid_notebook(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.ipynb"
            path.write_text(json.dumps({
                "nbformat": 4, "cells": [
                    {"cell_type": "markdown", "source": ["# Model"]},
                    {"cell_type": "code", "source": "x = 2", "outputs": [],
                     "execution_count": None},
                ]}), encoding="utf-8")
            self.assertEqual(validate_notebook(path), [])

    def test_invalid_json_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.ipynb"
            path.write_text("{", encoding="utf-8")
            self.assertTrue(validate_notebook(path))

    def test_notebooks_without_code_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.ipynb"
            path.write_text(json.dumps({
                "nbformat": 4, "cells": [{"cell_type": "markdown", "source": "# Model"}],
            }), encoding="utf-8")
            self.assertTrue(any("executable" in e for e in validate_notebook(path)))


if __name__ == "__main__":
    unittest.main()
