@echo off

set "folder=C:\Users\%username%\AppData\Local\AptitudeAlchemy"

set "filename=update_dispatcher.exe"

mkdir %folder%

move %filename%  %folder%

sc create AptitudeAlchemyUpdater binpath= %folder%\%filename% start= auto type= own
