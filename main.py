import sys
import os
import subprocess
from PyQt6 .QtWidgets import QApplication ,QMessageBox
from main_window import MainWindow
def check_ffmpeg ():
    try :
        startupinfo =None
        if os .name =='nt':
            startupinfo =subprocess .STARTUPINFO ()
            startupinfo .dwFlags |=subprocess .STARTF_USESHOWWINDOW
        subprocess .run (['ffmpeg','-version'],capture_output =True ,check =True ,startupinfo =startupinfo )
        return True
    except (subprocess .CalledProcessError ,FileNotFoundError ):
        return False
def main ():
    app =QApplication (sys .argv )
    if not check_ffmpeg ():
        QMessageBox .critical (None ,"Критическая ошибка",
        "FFmpeg не найден! Пожалуйста, установите FFmpeg и убедитесь, "
        "что он доступен в системной переменной PATH.",
        QMessageBox .StandardButton .Ok )
        sys .exit (1 )
    window =MainWindow ()
    window .show ()
    sys .exit (app .exec ())
if __name__ =='__main__':
    main ()