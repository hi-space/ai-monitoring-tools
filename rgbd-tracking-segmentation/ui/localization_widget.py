from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.image_viewer import ImageViewer
from utils import title_text

from debug.tracer import pdb_pm


class LocalizationWidget(QDockWidget):
    def __init__(self, parent=None):
        super(LocalizationWidget, self).__init__(parent)

        title_label = title_text("2.5D Localization")

        self.tracking_viewer = ImageViewer(640, 480)
        self.debug_viewer_1 = ImageViewer()
        self.debug_viewer_2 = ImageViewer()
        self.tracking_button = QPushButton('Tracking')
        self.tracking_button.setCheckable(True)
        self.tracking_button.setChecked(True)

        debug_layout = QHBoxLayout()
        debug_layout.addWidget(self.debug_viewer_1)
        debug_layout.addWidget(self.debug_viewer_2)
        
        self.table_widget = QTableWidget(3, 3)
        self.table_widget.setHorizontalHeaderLabels(["pet", "contacts", "safe/unsafe"])

        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setDefaultSectionSize(200)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setFont(self.get_font())
        self.table_widget.verticalHeader().setDefaultSectionSize(50)

        tracking_layout = QVBoxLayout()
        tracking_layout.addWidget(title_label)
        tracking_layout.addWidget(self.tracking_viewer)
        tracking_layout.addLayout(debug_layout)
        tracking_layout.addWidget(self.table_widget)
        tracking_layout.addWidget(self.tracking_button)

        tracking_layout.setAlignment(Qt.AlignCenter)
        
        tracking_widget = QWidget()
        tracking_widget.setLayout(tracking_layout)

        self.tracking_button.setFixedHeight(50)
        self.setFixedHeight(1100)
        # self.setWindowTitle('Tracking')

        self.setWidget(tracking_widget)
    
    def setButtonEvent(self, event):
        self.tracking_button.clicked.connect(event)

    def getImageSignal(self):
        return self.tracking_viewer.setImage

    def getDebugSignal(self):
        return self.debug_viewer_1.setImage, self.debug_viewer_2.setImage

    def isOn(self):
        return self.tracking_button.isChecked()

    def id2prop(self, id):
        if id == 0:
            return 'pet-1', QColor(70, 250, 150)
        elif id == 1:
            return 'pet-2', QColor(190, 205, 225)
        elif id == 2:
            return 'pet-3', QColor(180, 60, 240)
        elif id == 3:
            return 'pet-4', QColor(255, 255, 255)
        else:
            return None, None

    def get_font(self):
        return QFont('Arial', 25)

    def setLocalizationResultOnStatusLabel(self, nearby_classes):

        if type(nearby_classes) != dict:
            raise TypeError("A variable `nearby_classes` should be declared dict.")
        
        self.table_widget.clearContents()

        status_label = ""
        color = 'color: white;'
        table_row_idx = 0
        for cat_id, nearby_classes_in_set in nearby_classes.items():

            if type(nearby_classes_in_set) != set:
                raise TypeError("A variable `nearby_classes_in_set` should be declared set.")

            nearby_classes_in_set = list(nearby_classes_in_set)
            if len(nearby_classes_in_set) != 0:

                cat_name, cat_color = self.id2prop(cat_id)
                if cat_name is None:
                    continue
                
                #TODO
                if 'floor' in nearby_classes_in_set:
                    isSafe = True
                    zone_color = QColor(100, 255, 100)
                else:
                    isSafe = False
                    zone_color = QColor(255, 100, 100)
                    
                cat_name_widget = QTableWidgetItem(cat_name)
                cat_name_widget.setForeground(QBrush(cat_color))
                cat_name_widget.setFont(self.get_font())
                cat_name_widget.setTextAlignment(Qt.AlignCenter)

                nearby_classes_in_set_widget = QTableWidgetItem(", ".join(nearby_classes_in_set))
                nearby_classes_in_set_widget.setFont(self.get_font())
                nearby_classes_in_set_widget.setTextAlignment(Qt.AlignCenter)

                is_safe_widget = QTableWidgetItem("Safe" if isSafe else "Unsafe")
                is_safe_widget.setForeground(QBrush(zone_color))
                is_safe_widget.setFont(self.get_font())
                is_safe_widget.setTextAlignment(Qt.AlignCenter)

                self.table_widget.setItem(table_row_idx, 0, cat_name_widget)
                self.table_widget.setItem(table_row_idx, 1, nearby_classes_in_set_widget)
                self.table_widget.setItem(table_row_idx, 2, is_safe_widget)
                table_row_idx += 1