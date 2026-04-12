@echo off
setlocal
python -m PyInstaller --noconfirm --windowed --name SyanaTek app/main.py ^
  --collect-all pyvista ^
  --collect-all pyvistaqt ^
  --collect-all vtkmodules
endlocal
