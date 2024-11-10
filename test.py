import sys
import folium
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

sys.setrecursionlimit(10000)

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the Folium map
        self.map = folium.Map(location=[51.5074, -0.1278], zoom_start=12)  # Coordinates for London
        folium.Marker([51.5074, -0.1278], popup='London').add_to(self.map)

        # Save the map to an HTML file
        map_path = "simple_map.html"
        self.map.save(map_path)

        # Set up the PySide6 WebEngine to display the map
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(map_path))

        # Set up the main window layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        # Create a QWidget for the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set window title and size
        self.setWindowTitle("Folium Map in PySide6 Window")
        self.setGeometry(100, 100, 800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec())
