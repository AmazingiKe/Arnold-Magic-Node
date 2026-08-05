"""插件包与项目根目录的路径引用。"""

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
ICONS_ROOT = PROJECT_ROOT / "icons"
