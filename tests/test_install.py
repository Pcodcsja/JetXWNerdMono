import sys
import unittest
from unittest.mock import patch

from scripts import install_split


class InstallRegressionTests(unittest.TestCase):
    def test_bad_core_checksum_is_rejected(self):
        self.assertFalse(install_split.valid_core(b"not a verified WASM core"))

    @patch("scripts.install_split.subprocess.run")
    @patch("scripts.install_split.install")
    def test_split_runs_after_installation(self, install, run):
        events = []
        install.side_effect = lambda: events.append("installed")
        run.side_effect = lambda *args, **kwargs: events.append("split")
        with patch.object(sys, "argv", ["install_split.py", "--split"]):
            install_split.main()
        self.assertEqual(events, ["installed", "split"])
        self.assertEqual(run.call_args.args[0], [sys.executable, str(install_split.ROOT / "split.py")])

    @patch("scripts.install_split.subprocess.run")
    @patch("scripts.install_split.install", side_effect=RuntimeError("installation failed"))
    def test_failed_installation_does_not_start_split(self, install, run):
        with patch.object(sys, "argv", ["install_split.py", "--split"]):
            with self.assertRaises(RuntimeError):
                install_split.main()
        run.assert_not_called()
