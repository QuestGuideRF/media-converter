import os
from PyQt6 .QtWidgets import QMainWindow ,QFileDialog ,QMessageBox
from PyQt6 .QtCore import QThread
from PyQt6 .QtGui import QIcon
from config import STYLESHEET ,IMAGE_EXT ,VIDEO_EXT
from converter_worker import ConverterWorker
from ui_components import create_main_widget
class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("Профессиональный медиаконвертер")
        self .setGeometry (100 ,100 ,1200 ,800 )
        icon_path =os .path .join (os .path .dirname (__file__ ),'assets','icon.png')
        if os .path .exists (icon_path ):
            self .setWindowIcon (QIcon (icon_path ))
        self .IMAGE_EXT =IMAGE_EXT
        self .VIDEO_EXT =VIDEO_EXT
        self .thread =None
        self .worker =None
        central_widget =create_main_widget (self )
        self .setCentralWidget (central_widget )
        self .setStyleSheet (STYLESHEET )
    def add_files_to_list (self ,file_paths ):
        image_paths_to_add =[]
        video_paths_to_add =[]
        current_images ={self .image_list_widget .item (i ).text ()for i in range (self .image_list_widget .count ())}
        current_videos ={self .video_list_widget .item (i ).text ()for i in range (self .video_list_widget .count ())}
        for path in file_paths :
            if os .path .isdir (path ):
                for root ,_ ,files in os .walk (path ):
                    for file in files :
                        self .sort_file (os .path .join (root ,file ),image_paths_to_add ,video_paths_to_add ,current_images ,
                        current_videos )
            else :
                self .sort_file (path ,image_paths_to_add ,video_paths_to_add ,current_images ,current_videos )
        if image_paths_to_add :
            self .image_list_widget .addItems (image_paths_to_add )
        if video_paths_to_add :
            self .video_list_widget .addItems (video_paths_to_add )
    def sort_file (self ,path ,img_list ,vid_list ,current_imgs ,current_vids ):
        if path not in current_imgs and path .lower ().endswith (self .IMAGE_EXT ):
            img_list .append (path )
            current_imgs .add (path )
        elif path not in current_vids and path .lower ().endswith (self .VIDEO_EXT ):
            vid_list .append (path )
            current_vids .add (path )
    def select_output_directory (self ):
        directory =QFileDialog .getExistingDirectory (self ,"Выберите папку для сохранения")
        if directory :
            self .output_dir_line .setText (directory )
    def clear_lists (self ):
        self .image_list_widget .clear ()
        self .video_list_widget .clear ()
        self .log_widget .clear ()
        self .progress_bar .setValue (0 )
        self .log_widget .setPlaceholderText ("Списки очищены. Готов к работе!")
    def start_conversion (self ):
        output_dir =self .output_dir_line .text ()
        if not output_dir or not os .path .isdir (output_dir ):
            QMessageBox .warning (self ,"Ошибка","Пожалуйста, выберите корректную папку для сохранения.")
            return
        image_files =[self .image_list_widget .item (i ).text ()for i in range (self .image_list_widget .count ())]
        video_files =[self .video_list_widget .item (i ).text ()for i in range (self .video_list_widget .count ())]
        if not image_files and not video_files :
            QMessageBox .warning (self ,"Ошибка","Нет файлов для конвертации.")
            return
        files_to_convert =[]
        img_format =self .image_format_combo .currentText ()
        vid_format =self .video_format_combo .currentText ()
        files_to_convert .extend ([(file ,img_format )for file in image_files ])
        files_to_convert .extend ([(file ,vid_format )for file in video_files ])
        self .convert_button .setEnabled (False )
        self .clear_button .setEnabled (False )
        self .progress_bar .setValue (0 )
        self .log_widget .clear ()
        self .thread =QThread ()
        self .worker =ConverterWorker (files_to_convert ,output_dir )
        self .worker .moveToThread (self .thread )
        self .thread .started .connect (self .worker .run )
        self .worker .finished .connect (self .thread .quit )
        self .worker .finished .connect (self .worker .deleteLater )
        self .thread .finished .connect (self .thread .deleteLater )
        self .worker .progress .connect (self .progress_bar .setValue )
        self .worker .log_message .connect (lambda msg :self .log_widget .append (msg ))
        self .thread .finished .connect (self .on_conversion_finished )
        self .thread .start ()
    def on_conversion_finished (self ):
        self .convert_button .setEnabled (True )
        self .clear_button .setEnabled (True )
        QMessageBox .information (self ,"Завершено","Процесс конвертации успешно завершен!")
    def closeEvent (self ,event ):
        if self .thread is not None and self .thread .isRunning ():
            reply =QMessageBox .question (self ,'Выход',
            "Процесс конвертации еще не завершен. Вы уверены, что хотите выйти?",
            QMessageBox .StandardButton .Yes |QMessageBox .StandardButton .No ,
            QMessageBox .StandardButton .No )
            if reply ==QMessageBox .StandardButton .Yes :
                self .worker .stop ()
                self .thread .quit ()
                self .thread .wait ()
                event .accept ()
            else :
                event .ignore ()
        else :
            event .accept ()