from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_public_repository import validate_repository


class PublicRepositoryPolicyTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / "Client Case Studies" / "anonymized-example").mkdir(parents=True)
        (root / "README.md").write_text(
            "GitHub-only portfolio. No GitHub Pages and no web deployment.\n",
            encoding="utf-8",
        )
        (root / ".github" / "workflows" / "ci.yml").write_text(
            "name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
            encoding="utf-8",
        )
        demo_readme = root / "Demo Templates" / "Example Category" / "example-project" / "README.md"
        demo_readme.parent.mkdir(parents=True)
        demo_readme.write_text("**Status: DEMO**\nSynthetic example.\n", encoding="utf-8")
        (root / "Client Case Studies" / "anonymized-example" / "README.md").write_text(
            "**Status: DEMO**\nClient identity is withheld. All records are synthetic.\n",
            encoding="utf-8",
        )

    def validate_temp(self, mutate=None) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repo(root)
            if mutate:
                mutate(root)
            return validate_repository(root)

    def test_accepts_local_only_repository(self):
        self.assertEqual(self.validate_temp(), [])

    def test_rejects_pages_deployment_action(self):
        def mutate(root: Path):
            path = root / ".github" / "workflows" / "ci.yml"
            path.write_text("jobs:\n  deploy:\n    steps:\n      - uses: actions/deploy-pages@v4\n", encoding="utf-8")
        self.assertTrue(any("deploy-pages" in error for error in self.validate_temp(mutate)))

    def test_rejects_pages_write_permission(self):
        def mutate(root: Path):
            path = root / ".github" / "workflows" / "ci.yml"
            path.write_text("permissions:\n  pages: write\n", encoding="utf-8")
        self.assertTrue(any("pages: write" in error for error in self.validate_temp(mutate)))

    def test_rejects_oidc_write_permission(self):
        def mutate(root: Path):
            path = root / ".github" / "workflows" / "ci.yml"
            path.write_text("permissions:\n  id-token: write\n", encoding="utf-8")
        self.assertTrue(any("id-token write" in error for error in self.validate_temp(mutate)))

    def test_rejects_root_hosting_manifest(self):
        def mutate(root: Path):
            (root / "vercel.json").write_text("{}", encoding="utf-8")
        self.assertTrue(any("vercel.json" in error for error in self.validate_temp(mutate)))

    def test_rejects_non_anonymized_case_directory(self):
        def mutate(root: Path):
            old = root / "Client Case Studies" / "anonymized-example"
            old.rename(root / "Client Case Studies" / "named-client-case")
        self.assertTrue(any("must be anonymized" in error for error in self.validate_temp(mutate)))

    def test_rejects_demo_project_without_maturity_label(self):
        def mutate(root: Path):
            path = root / "Demo Templates" / "Example Category" / "example-project" / "README.md"
            path.write_text("Synthetic example without a status.\n", encoding="utf-8")
        self.assertTrue(any("Project README must contain one maturity label" in error for error in self.validate_temp(mutate)))

    def test_rejects_missing_maturity_label(self):
        def mutate(root: Path):
            path = root / "Client Case Studies" / "anonymized-example" / "README.md"
            path.write_text("Client identity is withheld. All records are synthetic.\n", encoding="utf-8")
        self.assertTrue(any("maturity label" in error for error in self.validate_temp(mutate)))

    def test_rejects_case_image_asset(self):
        def mutate(root: Path):
            path = root / "Client Case Studies" / "anonymized-example" / "logo.png"
            path.write_bytes(b"synthetic test bytes")
        self.assertTrue(any("Image/brand asset" in error for error in self.validate_temp(mutate)))

    def test_rejects_missing_scope_statement(self):
        def mutate(root: Path):
            (root / "README.md").write_text("Portfolio documentation.\n", encoding="utf-8")
        self.assertTrue(any("repository boundary" in error for error in self.validate_temp(mutate)))


if __name__ == "__main__":
    unittest.main()
