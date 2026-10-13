import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / ".agents/skills/entireio-setup/scripts/sync.py"
spec = importlib.util.spec_from_file_location("bootstrap", ROOT / "scripts/bootstrap.py")
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class TrustReuse(unittest.TestCase):
    def test_complete_approvals_and_idempotence(self):
        self.exercise("complete")

    def test_partial_source_is_rejected_without_changes(self):
        self.exercise("partial")

    def test_project_denial_is_preserved(self):
        self.exercise("denied")

    def test_hook_disable_is_preserved(self):
        self.exercise("disabled")

    def exercise(self, mode):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            source = base / "source/.codex/hooks.json"
            target = base / "target/.codex/hooks.json"
            config = base / "config.toml"
            for path in (source, target):
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({"hooks": {
                    "SessionStart": [{"hooks": [{"type": "command", "command": "entire start"}]}],
                    "Stop": [{"hooks": [{"type": "command", "command": "entire stop"}]}],
                }}))
            text = f'[hooks.state."{source}:session_start:0:0"]\ntrusted_hash = "sha256:a"\n'
            if mode != "partial":
                text += f'[hooks.state."{source}:stop:0:0"]\ntrusted_hash = "sha256:b"\n'
            if mode == "denied":
                text += f'[projects."{target.parent.parent}"]\ntrust_level = "untrusted"\n'
            if mode == "disabled":
                text += f'[hooks.state."{target}:stop:0:0"]\ntrusted_hash = "sha256:b"\ndisabled = true\n'
            config.write_text(text)
            args = [sys.executable, str(HELPER), "--worktree", str(target.parent.parent)]
            env = dict(os.environ, CODEX_HOME=tmp)
            result = subprocess.run(args + ["--dry-run"], env=env, capture_output=True)
            self.assertEqual(config.read_text(), text)
            if mode != "complete":
                self.assertNotEqual(result.returncode, 0)
                return
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run(args, env=env, check=True, capture_output=True)
            after = config.read_text()
            subprocess.run(args, env=env, check=True, capture_output=True)
            self.assertEqual(config.read_text(), after)
            self.assertIn(f'{target}:session_start:0:0', after)
            self.assertIn(f'{target}:stop:0:0', after)


class CaptureGates(unittest.TestCase):
    def test_remote_checkpoint_mismatch_blocks_hosted_success(self):
        with patch.object(bootstrap, "run", side_effect=[
            '{"checkpoint_id": "cp", "sessions": [{"session_id": "chat"}]}',
            '{"checkpoint_sync_remote": "origin"}',
            'main', 'git@github.com:leej3/example.git',
            'git@github.com:leej3/example.git', 'refs/entire/checkpoints/cp/cp',
            'local-checkpoint', 'code',
            'code\trefs/heads/main', 'other-checkpoint\trefs/entire/checkpoints/cp/cp',
        ]) as run:
            with self.assertRaisesRegex(SystemExit, "checkpoint ref"):
                bootstrap.verify(ROOT, "chat", False)
            self.assertEqual(run.call_count, 10)

    def test_hosted_session_mismatch_is_rejected(self):
        with patch.object(bootstrap, "run", side_effect=[
            '{"checkpoint_id": "cp", "sessions": [{"session_id": "chat"}]}',
            '{"checkpoint_sync_remote": "origin"}',
            'main', 'git@github.com:leej3/example.git',
            'git@github.com:leej3/example.git', 'refs/entire/checkpoints/cp/cp',
            'checkpoint', 'code',
            'code\trefs/heads/main', 'checkpoint\trefs/entire/checkpoints/cp/cp',
            '{"logged_in": true}',
            '{"checkpoint_id": "cp", "sessions": [{"session_id": "other"}]}',
        ]):
            with self.assertRaisesRegex(SystemExit, "hosted checkpoint/session"):
                bootstrap.verify(ROOT, "chat", False, True)

    def test_basic_upload_verification_never_requests_entire_auth(self):
        values = [
            '{"checkpoint_id": "cp", "sessions": [{"session_id": "chat"}]}',
            '{"checkpoint_sync_remote": "origin"}',
            'main', 'git@github.com:leej3/example.git',
            'git@github.com:leej3/example.git', 'refs/entire/checkpoints/cp/cp',
            'checkpoint', 'code', 'code\trefs/heads/main',
            'checkpoint\trefs/entire/checkpoints/cp/cp',
        ]
        with patch.object(bootstrap, "run", side_effect=values) as run:
            bootstrap.verify(ROOT, "chat", False)
            self.assertFalse(any("auth" in call.args for call in run.call_args_list))

    def test_historical_session_does_not_pass_live_gate(self):
        with patch.object(bootstrap, "run", side_effect=[
            '{"checkpoint_id": "old", "sessions": [{"session_id": "old-chat"}]}',
        ]) as run:
            with self.assertRaisesRegex(SystemExit, "requested native session"):
                bootstrap.verify(ROOT, "new-chat", True)
            self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
