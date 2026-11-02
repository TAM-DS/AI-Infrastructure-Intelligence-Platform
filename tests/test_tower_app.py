"""Launch the Streamlit script headlessly to catch dashboard runtime errors."""
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


class TowerSmokeTest(unittest.TestCase):
    def test_dashboard_runs_with_committed_synthetic_data(self):
        app = AppTest.from_file(str(APP), default_timeout=90).run()
        self.assertFalse(app.exception, str([str(x.message) for x in app.exception]))
        self.assertGreaterEqual(len(app.metric), 8)


if __name__ == "__main__":
    unittest.main()
