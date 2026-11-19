"""배포할 화면·정적 자산만 public/으로 복사합니다."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'public'
OUT.mkdir(exist_ok=True)
for name in ['index.html','eda.html','insights.html']:shutil.copy2(ROOT/name,OUT/name)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
print('Static output ready: public/')
