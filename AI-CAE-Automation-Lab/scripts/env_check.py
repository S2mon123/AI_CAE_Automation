from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_cae_lab.env_check import main


if __name__ == "__main__":
    main()
