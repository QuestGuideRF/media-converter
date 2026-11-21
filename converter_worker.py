import os
import subprocess
from pathlib import Path
from PyQt6 .QtCore import QObject ,pyqtSignal
class ConverterWorker (QObject ):
    finished =pyqtSignal ()
    progress =pyqtSignal (int )
    log_message =pyqtSignal (str )
    def __init__ (self ,files_to_convert ,output_dir ):
        super ().__init__ ()
        self .files_to_convert =files_to_convert
        self .output_dir =output_dir
        self .is_running =True
    def run (self ):
        total_files =len (self .files_to_convert )
        if total_files ==0 :
            self .finished .emit ()
            return
        for i ,(file_path ,out_format )in enumerate (self .files_to_convert ):
            if not self .is_running :
                break
            base_name =Path (file_path ).stem
            output_file =Path (self .output_dir )/f"{base_name }.{out_format }"
            self .log_message .emit (f"Конвертирую: {Path (file_path ).name } -> {output_file .name }")
            command =['ffmpeg','-i',str (file_path ),'-y']
            if out_format in ['mp4','mkv','avi','mov']:
                command .extend (['-c:v','libx264','-c:a','aac','-preset','fast','-crf','22'])
            else :
                command .extend (['-q:v','0'])
            command .append (str (output_file ))
            try :
                startupinfo =None
                if os .name =='nt':
                    startupinfo =subprocess .STARTUPINFO ()
                    startupinfo .dwFlags |=subprocess .STARTF_USESHOWWINDOW
                process =subprocess .run (command ,check =True ,capture_output =True ,text =True ,startupinfo =startupinfo ,
                encoding ='utf-8')
                self .log_message .emit (f"✅ Успех: {output_file .name }")
            except subprocess .CalledProcessError as e :
                self .log_message .emit (f"❌ Ошибка при конвертации {Path (file_path ).name }:")
                self .log_message .emit (f"FFmpeg stderr: {e .stderr }")
            except Exception as e :
                self .log_message .emit (f"❌ Критическая ошибка: {str (e )}")
            progress_value =int (((i +1 )/total_files )*100 )
            self .progress .emit (progress_value )
        self .log_message .emit ("\n🎉 Конвертация завершена!")
        self .finished .emit ()
    def stop (self ):
        self .is_running =False