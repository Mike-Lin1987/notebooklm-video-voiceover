"""Synthetic end-to-end checks; no NotebookLM account or user media needed."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "media_tools.py"
FFMPEG = os.environ.get("TEST_FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("TEST_FFPROBE", "ffprobe")


class MediaToolsTest(unittest.TestCase):
    def setUp(self):
        qa = ROOT / ".qa"
        qa.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="配音 test ", dir=qa)
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.video = base / "影像 test.mp4"
        self.audio = base / "原聲 test.m4a"
        self.output = base / "合成 test.mp4"
        subprocess.run([FFMPEG, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=160x90:r=10",
                        "-t", "2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(self.video)], check=True)
        subprocess.run([FFMPEG, "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
                        "-t", "1", "-c:a", "aac", str(self.audio)], check=True)

    def tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *map(str, args),
                               "--ffprobe", FFPROBE, *(["--ffmpeg", FFMPEG] if args[0] != "inspect" else [])],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_happy_path_and_refusals(self):
        self.assertEqual(self.tool("inspect", self.audio).returncode, 0)
        self.assertEqual(self.tool("mux", self.video, self.audio, self.output).returncode, 0)
        self.assertEqual(self.tool("verify", self.audio, self.output).returncode, 0)
        self.assertNotEqual(self.tool("mux", self.video, self.audio, self.output).returncode, 0)
        self.assertNotEqual(self.tool("mux", self.video, self.audio, self.video).returncode, 0)
        long_audio = Path(self.tmp.name) / "long.m4a"
        subprocess.run([FFMPEG, "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440",
                        "-t", "3", "-c:a", "aac", str(long_audio)], check=True)
        self.assertNotEqual(self.tool("mux", self.video, long_audio, Path(self.tmp.name) / "long.mp4").returncode, 0)
        wav = Path(self.tmp.name) / "not-aac.wav"
        subprocess.run([FFMPEG, "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440",
                        "-t", "1", str(wav)], check=True)
        self.assertNotEqual(self.tool("mux", self.video, wav, Path(self.tmp.name) / "wav.mp4").returncode, 0)
        offset = Path(self.tmp.name) / "offset.mp4"
        subprocess.run([FFMPEG, "-v", "error", "-itsoffset", "0.5", "-i", str(self.audio),
                        "-i", str(self.video), "-map", "1:v:0", "-map", "0:a:0", "-c", "copy", str(offset)], check=True)
        self.assertNotEqual(self.tool("verify", self.audio, offset).returncode, 0)


if __name__ == "__main__":
    unittest.main()
