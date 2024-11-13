import sys
import io
from offline_folium import offline
import folium # pip install folium
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine
from PySide6 import QtCore
import os

"""
Folium in PyQt5
"""
class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Folium in PyQt Example')
        self.window_width, self.window_height = 1600, 1200
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        coordinate = (37.8199286, -122.4782551)
        m = folium.Map(
            crs='Simple', zoom_start=4
        )

        albasrah_overlay = folium.raster_layers.ImageOverlay(
            image='albasrah.webp',
            bounds=[[0,0], [-3040,3040]],
            zigzag_index=1
        )

        albasrah_overlay.add_to(m)
        m.fit_bounds(bounds=[[0,0], [-3040,3040]])

        # save map data to data object
        data = io.BytesIO()
        m.save(data, close_file=False)


        webView = QWebEngineView()
        webView.load(data.getvalue().decode())
        layout.addWidget(webView)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 35px;
        }
    ''')

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')