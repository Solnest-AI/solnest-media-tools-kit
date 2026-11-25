"""scripts/update.py: installs only a published release into the kit folder, keeps bin/,
the member's speech models and their own files, and --undo puts the old version back.
Offline: releases are read from a local folder (MEDIA_TOOLS_KIT_RELEASE_DIR)."""
import io
import os
import pathlib
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import update  # noqa: E402

FAKE_ENV = "SOME_KEY=fake_test_" + "0" * 24 + "\n"   # made up, never a real key
KIT_JSON = '{"kit": "media-tools-kit", "tools": ["ffmpeg", "whisper-cpp", "yt-dlp"]}\n'
RUNBOOK = "old runbook\n## SETUP\n### 7. Prove it works (CHECK)\n"


def tarball(folder, version, files, top=None):
    """A GitHub-style source tarball: one top folder, the kit at its root."""
    top = top or f"solnest-media-tools-kit-{version}"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        def add(rel, data):
            info = tarfile.TarInfo(f"{top}/{rel}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        add("VERSION", f"{version}\n".encode())
        for rel, text in files.items():
            add(rel, text.encode())
    (pathlib.Path(folder) / f"v{version}.tar.gz").write_bytes(buf.getvalue())


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = pathlib.Path(self.tmp.name)
        self.rel = base / "releases"
        self.rel.mkdir()
        self.root = base / "solnest" / "media-tools-kit"
        self.root.mkdir(parents=True)
        env = mock.patch.dict(os.environ, {update.LOCAL_RELEASES: str(self.rel)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(self.tmp.cleanup)
        old = {"kit.json": KIT_JSON, "CLAUDE.md": RUNBOOK, "README.md": "old readme\n",
               "scripts/update.py": "x = 1\n", "scripts/dropped.py": "# gone next\n"}
        tarball(self.rel, "1.0.0", old)
        for rel, text in old.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text, encoding="utf-8")
        (self.root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        # the member's own things
        (self.root / ".env").write_text(FAKE_ENV, encoding="utf-8")
        (self.root / "bin").mkdir()
        (self.root / "bin" / "py").write_text("fake launcher\n", encoding="utf-8")
        (self.root / "whisper-models").mkdir()
        (self.root / "whisper-models" / "ggml-base.en.bin").write_bytes(b"\x00fake model\xff")
        (self.root / "ggml-small.en.bin").write_bytes(b"\x01another fake model")
        (self.root / "my-notes.md").write_text("mine\n", encoding="utf-8")
        (self.root / "scripts" / "my-helper.sh").write_text("mine too\n", encoding="utf-8")

    def _new_release(self):
        tarball(self.rel, "1.1.0", {"kit.json": KIT_JSON, "CLAUDE.md": RUNBOOK.replace("old", "new"),
                                    "README.md": "new readme\n", "scripts/update.py": "x = 2\n",
                                    "scripts/new.py": "# brand new\n",
                                    "bin/py": "release must not win\n", ".env": "EVIL=from_release\n",
                                    "whisper-models/ggml-base.en.bin": "evil\n", "ggml-small.en.bin": "evil\n"})

    def _member_files_intact(self):
        self.assertEqual((self.root / ".env").read_text(), FAKE_ENV)
        self.assertEqual((self.root / "bin" / "py").read_text(), "fake launcher\n")
        self.assertEqual((self.root / "whisper-models" / "ggml-base.en.bin").read_bytes(), b"\x00fake model\xff")
        self.assertEqual((self.root / "ggml-small.en.bin").read_bytes(), b"\x01another fake model")
        self.assertEqual((self.root / "my-notes.md").read_text(), "mine\n")
        self.assertEqual((self.root / "scripts" / "my-helper.sh").read_text(), "mine too\n")

    def test_update_keeps_member_files_and_undo_goes_back(self):
        self._new_release()
        r = update.update(self.root)
        self.assertEqual(r["status"], "updated")
        self.assertEqual((self.root / "VERSION").read_text().strip(), "1.1.0")
        self.assertIn("new runbook", (self.root / "CLAUDE.md").read_text())
        self.assertTrue((self.root / "scripts" / "new.py").is_file())
        self.assertFalse((self.root / "scripts" / "dropped.py").exists())   # shipped by 1.0.0, not 1.1.0
        self._member_files_intact()
        self.assertEqual(update.update(self.root)["status"], "current")

        update.undo(self.root)
        self.assertEqual((self.root / "VERSION").read_text().strip(), "1.0.0")
        self.assertIn("old runbook", (self.root / "CLAUDE.md").read_text())
        self.assertTrue((self.root / "scripts" / "dropped.py").is_file())
        self.assertFalse((self.root / "scripts" / "new.py").exists())
        self.assertFalse((self.root / update.BACKUP_DIR).exists())
        self._member_files_intact()

    def test_manifest_lists_what_shipped_and_removal_follows_it(self):
        self._new_release()
        update.update(self.root)
        listed = set(update.load_manifest(self.root))
        self.assertEqual(listed, {"VERSION", "kit.json", "CLAUDE.md", "README.md", "scripts/update.py",
                                  "scripts/new.py"})
        # the next release drops scripts/new.py: the manifest is what gets it removed
        tarball(self.rel, "1.2.0", {"kit.json": KIT_JSON, "CLAUDE.md": RUNBOOK, "README.md": "newer\n",
                                    "scripts/update.py": "x = 3\n"})
        r = update.update(self.root)
        self.assertEqual(r["removed"], ["scripts/new.py"])
        self.assertFalse((self.root / "scripts" / "new.py").exists())
        self._member_files_intact()

    def test_edited_kit_file_is_reported_and_saved(self):
        (self.root / "CLAUDE.md").write_text("the member edited this\n", encoding="utf-8")
        self._new_release()
        r = update.update(self.root)
        self.assertIn("CLAUDE.md", r["edited"])
        self.assertEqual((pathlib.Path(r["backup"]) / "CLAUDE.md").read_text(), "the member edited this\n")

    def test_protected_paths(self):
        want = {".env": True, "sub/.env": True, ".env.local": True, ".env.example": False, "keys.env": True,
                ".cache/x": True, "bin/py": True, "bin/py.cmd": True, "tokens.json": True, "a.token": True,
                "whisper-models/ggml-base.en.bin": True, "models/anything.bin": True, "ggml-base.bin": True,
                ".venv/lib/x.py": True, ".update-backup/1/undo.json": True, update.MANIFEST: True,
                "kit.json": False, "CLAUDE.md": False, "README.md": False, "install.sh": False,
                "scripts/update.py": False, "scripts/solnest_autoupdate.py": False}
        for rel, protected in want.items():
            self.assertEqual(update._protected(rel), protected, rel)

    def test_refuses_a_git_checkout(self):
        (self.root / ".git").mkdir()
        self._new_release()
        with self.assertRaises(update.UpdateError):
            update.update(self.root)
        self.assertEqual((self.root / "VERSION").read_text().strip(), "1.0.0")

    def test_unsafe_release_changes_nothing(self):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            for name in ("top/VERSION", "../evil"):
                info = tarfile.TarInfo(name)
                info.size = 1
                tar.addfile(info, io.BytesIO(b"x"))
        (self.rel / "v1.1.0.tar.gz").write_bytes(buf.getvalue())
        with self.assertRaises(update.UpdateError):
            update.update(self.root)
        self.assertEqual((self.root / "VERSION").read_text().strip(), "1.0.0")
        self.assertIn("old runbook", (self.root / "CLAUDE.md").read_text())

    def test_mislabelled_release_is_refused(self):
        tarball(self.rel, "1.1.0", {"kit.json": KIT_JSON})
        blob = (self.rel / "v1.1.0.tar.gz").read_bytes()
        (self.rel / "v1.1.0.tar.gz").unlink()
        (self.rel / "v1.3.0.tar.gz").write_bytes(blob)     # tag says 1.3.0, VERSION inside says 1.1.0
        with self.assertRaises(update.UpdateError):
            update.update(self.root)
        self.assertEqual((self.root / "VERSION").read_text().strip(), "1.0.0")

    def test_a_release_of_something_else_is_refused(self):
        tarball(self.rel, "1.1.0", {"CLAUDE.md": "no kit.json here\n"})
        with self.assertRaises(update.UpdateError):
            update.update(self.root)
        self.assertEqual((self.root / "VERSION").read_text().strip(), "1.0.0")

    def test_no_release_yet_is_a_plain_error(self):
        for p in self.rel.glob("*"):
            p.unlink()
        with self.assertRaises(update.UpdateError):
            update.update(self.root)

    def test_after_passes_on_good_files_and_fails_on_broken_ones(self):
        self.assertIn("3 tools", update.after(self.root))
        (self.root / "kit.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(update.UpdateError):
            update.after(self.root)
        (self.root / "kit.json").write_text(KIT_JSON, encoding="utf-8")
        (self.root / "CLAUDE.md").write_text("a runbook with no steps\n", encoding="utf-8")
        with self.assertRaises(update.UpdateError):
            update.after(self.root)
        (self.root / "CLAUDE.md").write_text(RUNBOOK, encoding="utf-8")
        (self.root / "scripts" / "update.py").write_text("def broken(:\n", encoding="utf-8")
        with self.assertRaises(update.UpdateError):
            update.after(self.root)

    def test_the_real_kit_passes_after(self):
        self.assertIn("tools in kit.json", update.after(SCRIPTS.parent))


if __name__ == "__main__":
    unittest.main()
