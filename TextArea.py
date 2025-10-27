# TextArea Application using PyQt6
# This application provides a simple TextArea with customizable themes and fonts.
# Author: Rise-KuN
# Version: 1.1.1

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QToolBar, 
    QPushButton, QDialog, QVBoxLayout, QTabWidget,
    QWidget, QLabel, QComboBox, QRadioButton,
    QButtonGroup, QFrame, QHBoxLayout, QSizePolicy,
    QFontComboBox, QSpinBox, QGroupBox, QPlainTextEdit,
    QDockWidget, QCheckBox, QStyle
)
from PyQt6.QtCore import Qt, QSettings, QDir
from PyQt6.QtGui import (
    QFont, QTextCursor, QTextOption, 
    QPalette, QColor, QTextCharFormat, 
    QTextBlockFormat, QIcon
)
import sys
import os
import ctypes
from datetime import datetime

class TextAreaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TextArea")
        
        # Initialize debug console
        self.debug_console = None
        self.debug_dock = None
        
        # Default settings
        self.font_name = "Arial"
        self.font_size = 16
        self.theme_mode = "Dark"
        self.text_content = ""
        self.show_debug = False
        self.always_on_top = False
        
        # Load settings
        self.load_settings()
        self.log_debug("Application initialized")
        
        # Set window icon properly
        self._set_window_icon()
        
        # Initialize debug console if enabled
        if self.show_debug:
            self._init_debug_console()
            self.log_debug("Application started")
            self.log_debug(f"Current Theme: {self.theme_mode}")
        
        # Apply theme based on settings
        self.apply_theme()
        
        # Initialize UI
        self.setup_ui()
        self.apply_font()
        
        # Set text content
        self.text_area.setPlainText(self.text_content)

        # Apply always on top setting immediately
        self.set_always_on_top(self.always_on_top)        

    def _init_debug_console(self):
        """Initialize debug console"""
        try:
            self.debug_console = QPlainTextEdit()
            self.debug_console.setReadOnly(True)
            
            # Apply theme to debug console immediately after creation
            if self.theme_mode == "Dark":
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #1e1e1e;
                        color: white;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)
            elif self.theme_mode == "Light":
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #ffffff;
                        color: black;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)
            else:
                self.log_debug(f"Unknown Theme '{self.theme_mode}' Set, Defaulting To Dark Theme - Console")
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #1e1e1e;
                        color: white;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)
                
            self.debug_dock = QDockWidget("Debug Console", self)
            self.debug_dock.setObjectName("debug_console_dock")
            self.debug_dock.setWidget(self.debug_console)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.debug_dock)
            self.debug_dock.setVisible(self.show_debug)
            
            # Connect the close event to update the checkbox
            self.debug_dock.closeEvent = self.handle_debug_console_close
        except Exception as e:
            print(f"Failed to initialize debug console: {e}")

    def handle_debug_console_close(self, event):
        """Handle debug console close event"""
        self.show_debug = False
        self.save_settings_to_file()
        event.accept()

    def log_debug(self, message):
        """Add a timestamped debug message to the console"""
        if not hasattr(self, 'show_debug') or not self.show_debug or self.debug_console is None:
            return
            
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.debug_console.appendPlainText(f"[{timestamp}] {message}")
            self.debug_console.ensureCursorVisible()
        except Exception as e:
            print(f"Debug logging failed: {e}")

    def _set_window_icon(self):
        """Properly set window icon with multiple fallback options"""
        try:
            icon_paths = [
                os.path.join(os.path.dirname(__file__), "icon.ico"),
                os.path.join(QDir.currentPath(), "icon.ico"),
                os.path.join(QDir.homePath(), "icon.ico"),
                "icon.ico"
            ]
            
            for path in icon_paths:
                if os.path.exists(path):
                    self.setWindowIcon(QIcon(path))
                    self.log_debug(f"Icon loaded from: {path}")
                    return
            
            # Fallback to embedded icon if available
            self.setWindowIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_DesktopIcon))
            self.log_debug("Using fallback system icon")
        except Exception as e:
            self.log_debug(f"Error setting icon: {str(e)}")
        
    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("main_app_toolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Settings button
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.clicked.connect(self.open_settings)
        self.toolbar.addWidget(self.btn_settings)
        
        # TextArea
        self.text_area = QTextEdit()
        self.text_area.setFrameShape(QFrame.Shape.NoFrame)
        self.text_area.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        layout.addWidget(self.text_area)

    def set_always_on_top(self, enable):
            """Toggle the Always On Top state for the main window"""
            self.always_on_top = enable
            
            # Get current window flags
            flags = self.windowFlags()
            
            if enable:
                # Set the flag to keep the window on top
                self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
                self.log_debug("Always On Top: Enabled")
            else:
                # Clear the flag
                self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
                self.log_debug("Always On Top: Disabled")
            
            # Must call show() again to apply the new flags
            self.show()
    
    def apply_theme(self, theme=None):
        if theme is not None:
            self.theme_mode = theme
            self.log_debug(f"Theme Changed To: {self.theme_mode}")
            
        if self.theme_mode == "Dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QToolBar {
                    background-color: #252525;
                    border: none;
                    padding: 5px;
                }
                QTextEdit, QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: white;
                    selection-background-color: #0078d7;
                    selection-color: white;
                    border: none;
                }
                QPushButton {
                    background-color: #333;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
                QPushButton:checked {
                    background-color: #0078d7;
                }
                QDialog {
                    background-color: #252525;
                }
                QLabel {
                    color: white;
                }
                QGroupBox {
                    color: white;
                    border: 1px solid #444;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QComboBox, QSpinBox, QFontComboBox {
                    background-color: #333;
                    color: white;
                    border: 1px solid #555;
                    padding: 3px;
                }
                QTabWidget::pane {
                    border: none;
                }
                QTabBar::tab {
                    background: #252525;
                    color: white;
                    padding: 8px;
                    border: none;
                }
                QTabBar::tab:selected {
                    background: #333;
                }
                QRadioButton {
                    color: white;
                    padding: 5px;
                }
                QDockWidget {
                    background: #252525;
                }
                QGroupBox#debug_group {
                    color: white;
                    border: 1px solid #444;
                }
                QCheckBox {
                    color: white;
                }     
            """)
            
            # Update debug console if Enabled
            if self.debug_console:
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #1e1e1e;
                        color: white;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)

        elif self.theme_mode == "Light":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                }
                QToolBar {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 5px;
                }
                QTextEdit, QPlainTextEdit {
                    background-color: #ffffff;
                    color: black;
                    selection-background-color: #0078d7;
                    selection-color: white;
                    border: none;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: black;
                    border: none;
                    padding: 5px 10px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:checked {
                    background-color: #0078d7;
                    color: white;
                }
                QDialog {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: black;
                }
                QGroupBox {
                    color: black;
                    border: 1px solid #ccc;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QComboBox, QSpinBox, QFontComboBox {
                    background-color: #ffffff;
                    color: black;
                    border: 1px solid #ccc;
                    padding: 3px;
                }
                QTabWidget::pane {
                    border: none;
                }
                QTabBar::tab {
                    background: #f0f0f0;
                    color: black;
                    padding: 8px;
                    border: none;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                }
                QRadioButton {
                    color: black;
                    padding: 5px;
                }
                QDockWidget {
                    background: #f0f0f0;
                }
                QGroupBox#debug_group {
                    color: black;
                    border: 1px solid #ccc;
                }
                QCheckBox {
                    color: black;
                }
            """)

            # Update debug console if Enabled
            if self.debug_console:
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #ffffff;
                        color: black;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)
        else:
            # For now, default to dark theme if an unknown theme is set
            self.log_debug(f"Unknown Theme '{self.theme_mode}' set, Defaulting To Dark Theme")
            self.theme_mode = "Dark"
            self.apply_theme()  # Recursively apply dark theme
    
    def apply_font(self):
        font = QFont(self.font_name, self.font_size)
        if hasattr(self, 'font_weight'):
            font.setWeight(self.font_weight)
        self.text_area.setFont(font)
        self.log_debug(f"Font-Family: {self.font_name}, Font-Size: {self.font_size}, Font-Weight: {getattr(self, 'font_weight', 'Normal')}")

    def open_settings(self):
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_dialog.setMinimumSize(500, 400)

        if hasattr(self, 'settings_dialog_geometry') and self.settings_dialog_geometry:
            settings_dialog.restoreGeometry(self.settings_dialog_geometry)
        
        layout = QVBoxLayout(settings_dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        notebook = QTabWidget()
        layout.addWidget(notebook)

        # General tab
        general_tab = QWidget()
        notebook.addTab(general_tab, "General")
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(5, 5, 5, 5)
        general_layout.setSpacing(10)
        
        # Themes tab
        theme_group = QGroupBox("Theme")
        theme_group_layout = QVBoxLayout()
        theme_group_layout.setContentsMargins(10, 15, 10, 10)
        theme_group_layout.setSpacing(5)
        
        # Theme selection in a group box
        theme_group = QGroupBox("Theme")
        theme_group_layout = QVBoxLayout()
        theme_group_layout.setContentsMargins(10, 15, 10, 10)
        theme_group_layout.setSpacing(5)
        
        self.theme_group = QButtonGroup()
        
        dark_radio = QRadioButton("Dark")
        light_radio = QRadioButton("Light")
        
        self.theme_group.addButton(dark_radio, 1)
        self.theme_group.addButton(light_radio, 2)
        
        theme_group_layout.addWidget(dark_radio)
        theme_group_layout.addWidget(light_radio)
        theme_group.setLayout(theme_group_layout)
        
        general_layout.addWidget(theme_group)
        
        # Set current selection
        if self.theme_mode == "Dark":
            dark_radio.setChecked(True)
        elif self.theme_mode == "Light":
            light_radio.setChecked(True)
        else:
            dark_radio.setChecked(True)
            self.log_debug(f"Unknown Theme '{self.theme_mode}' set, Defaulting To Dark Theme")

        # Always On Top Group
        aot_group = QGroupBox("Window Settings")
        aot_group_layout = QVBoxLayout()
        aot_group_layout.setContentsMargins(10, 15, 10, 10)
        aot_group_layout.setSpacing(5)
        
        self.aot_checkbox = QCheckBox("Keep window always on top")
        self.aot_checkbox.setChecked(self.always_on_top)
        aot_group_layout.addWidget(self.aot_checkbox)
        
        aot_group.setLayout(aot_group_layout)
        general_layout.addWidget(aot_group)
        
        general_layout.addStretch()
        
        # Fonts tab
        fonts_tab = QWidget()
        notebook.addTab(fonts_tab, "Fonts")
        
        font_layout = QVBoxLayout(fonts_tab)
        font_layout.setContentsMargins(5, 5, 5, 5)
        font_layout.setSpacing(10)
        
        font_group = QGroupBox("Font Settings")
        font_group_layout = QVBoxLayout()
        font_group_layout.setContentsMargins(10, 15, 10, 10)
        font_group_layout.setSpacing(5)
        
        # Font family selection
        font_label = QLabel("Font-Family:")
        font_group_layout.addWidget(font_label)
        
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.font_name))
        font_group_layout.addWidget(self.font_combo)
        
        # Font size selection
        size_label = QLabel("Font-Size:")
        font_group_layout.addWidget(size_label)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(self.font_size)
        font_group_layout.addWidget(self.size_spin)
        
        # Font weight selection
        weight_label = QLabel("Font-Weight:")
        font_group_layout.addWidget(weight_label)
        
        self.weight_combo = QComboBox()
        self.weight_combo.addItem("Normal", QFont.Weight.Normal)
        self.weight_combo.addItem("Thin", QFont.Weight.Thin)
        self.weight_combo.addItem("ExtraLight", QFont.Weight.ExtraLight)
        self.weight_combo.addItem("Light", QFont.Weight.Light)
        self.weight_combo.addItem("Medium", QFont.Weight.Medium)
        self.weight_combo.addItem("DemiBold", QFont.Weight.DemiBold)
        self.weight_combo.addItem("Bold", QFont.Weight.Bold)
        self.weight_combo.addItem("ExtraBold", QFont.Weight.ExtraBold)
        self.weight_combo.addItem("Black", QFont.Weight.Black)
        font_group_layout.addWidget(self.weight_combo)

        # Set initial weight selection based on saved value
        weight_index = self.weight_combo.findData(self.font_weight)
        if weight_index >= 0:
            self.weight_combo.setCurrentIndex(weight_index)
        
        # Preview
        preview_label = QLabel("Preview:")
        font_group_layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("This is a preview of the selected font and size.\nهذه معاينة للخط المحدد والحجم.")
        self.preview_text.setMaximumHeight(80)
        font_group_layout.addWidget(self.preview_text)
        
        font_group.setLayout(font_group_layout)
        font_layout.addWidget(font_group)
        font_layout.addStretch()
        
        # New Debug tab
        debug_tab = QWidget()
        notebook.addTab(debug_tab, "Debug")
        
        debug_layout = QVBoxLayout(debug_tab)
        debug_layout.setContentsMargins(5, 5, 5, 5)
        debug_layout.setSpacing(10)
        
        debug_group = QGroupBox("Debug Settings")
        debug_group.setObjectName("debug_group")
        debug_group_layout = QVBoxLayout()
        debug_group_layout.setContentsMargins(10, 15, 10, 10)
        debug_group_layout.setSpacing(10)
        
        self.debug_checkbox = QCheckBox("Show Debug Console")
        self.debug_checkbox.setChecked(self.show_debug)
        debug_group_layout.addWidget(self.debug_checkbox)
        
        debug_group.setLayout(debug_group_layout)
        debug_layout.addWidget(debug_group)
        debug_layout.addStretch()

        # Connect signals
        self.font_combo.currentFontChanged.connect(self.update_preview)
        self.size_spin.valueChanged.connect(self.update_preview)
        self.weight_combo.currentIndexChanged.connect(self.update_preview)
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(lambda: self.save_settings(settings_dialog))
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Set initial preview
        self.update_preview()
        
        def close_event(event):
            self.settings_dialog_geometry = settings_dialog.saveGeometry()
            self.save_settings_to_file()
            settings_dialog.close()
        
        settings_dialog.closeEvent = close_event
        
        # Save geometry when saving settings
        def save_settings_wrapper():
            self.settings_dialog_geometry = settings_dialog.saveGeometry()
            self.save_settings(settings_dialog)
        
        # Update the save button connection
        save_button.clicked.connect(save_settings_wrapper)
        
        settings_dialog.exec()

    def update_preview(self):
        font = self.font_combo.currentFont()
        font.setPointSize(self.size_spin.value())
        weight = self.weight_combo.currentData()
        font.setWeight(weight)
        self.preview_text.setFont(font)

    def save_settings(self, dialog):
        # Save dialog geometry before processing
        self.settings_dialog_geometry = dialog.saveGeometry()

        # Get theme selection
        theme_id = self.theme_group.checkedId()
        if theme_id == 1:
            self.theme_mode = "Dark"
        elif theme_id == 2:
            self.theme_mode = "Light"
        else:
            self.theme_mode = "Dark"

        # Validate theme mode
        if self.theme_mode not in ["Dark", "Light"]:
            self.log_debug(f"Invalid Theme Selected: {self.theme_mode}, Defaulting To Dark")
            self.theme_mode = "Dark"

        self.log_debug(f"Theme Changed To: {self.theme_mode}")

        old_font = self.font_name
        old_size = self.font_size
        old_weight = getattr(self, 'font_weight', QFont.Weight.Normal)
        
        self.font_name = self.font_combo.currentFont().family()
        self.font_size = self.size_spin.value()
        self.font_weight = self.weight_combo.currentData()
        
        if old_font != self.font_name:
            self.log_debug(f"Font-Family Changed From {old_font} To {self.font_name}")
        if old_size != self.font_size:
            self.log_debug(f"Font-Size Changed From {old_size} To {self.font_size}")
        if old_weight != self.font_weight:
            self.log_debug(f"Font-Weight Changed From {old_weight} To {self.font_weight}")

        # Get Always On Top setting
        new_aot_setting = self.aot_checkbox.isChecked()
        aot_setting_changed = (new_aot_setting != self.always_on_top)

        if aot_setting_changed:
            self.set_always_on_top(new_aot_setting)
            self.log_debug(f"Always On Top setting changed to: {self.always_on_top}")
        
        # Get debug setting
        new_debug_setting = self.debug_checkbox.isChecked()
        debug_setting_changed = (new_debug_setting != self.show_debug)
        self.show_debug = new_debug_setting
        
        if debug_setting_changed:
            self.log_debug(f"Debug console setting changed to: {self.show_debug}")
        
        # Update checkbox state to match current setting
        self.debug_checkbox.setChecked(self.show_debug)
        
        # Apply changes
        self.apply_theme()
        self.apply_font()
        
        # Handle debug console visibility
        if debug_setting_changed:
            if self.show_debug:
                self._init_debug_console()
                self.log_debug("Debug console enabled")
            elif self.debug_dock is not None:
                self.debug_dock.setVisible(False)
                self.log_debug("Debug console hidden")

        # Force update the debug console theme immediately
        if self.debug_console:
            if self.theme_mode == "Dark":
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #1e1e1e;
                        color: white;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)
            else:
                self.debug_console.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #ffffff;
                        color: black;
                        selection-background-color: #0078d7;
                        selection-color: white;
                        border: none;
                    }
                """)
        
        # Save Settings
        self.save_settings_to_file()
        self.log_debug("Settings Saved.")
        
        dialog.close()
    
    def save_settings_to_file(self):
        settings = QSettings("TextArea", "Settings")
        settings.setValue("font_name", self.font_name)
        settings.setValue("font_size", self.font_size)
        settings.setValue("font_weight", self.font_weight)
        settings.setValue("theme_mode", self.theme_mode)
        settings.setValue("text_content", self.text_area.toPlainText())
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
        settings.setValue("show_debug", self.show_debug)
        settings.setValue("always_on_top", self.always_on_top)
        if hasattr(self, 'settings_dialog_geometry'):
            settings.setValue("settings_dialog_geometry", self.settings_dialog_geometry)
    
    def load_settings(self):
        settings = QSettings("TextArea", "Settings")
        
        # Load settings with defaults if not found
        self.font_name = settings.value("font_name", "Arial")
        self.font_size = int(settings.value("font_size", 16))
        self.theme_mode = settings.value("theme_mode", "Dark")
        self.text_content = settings.value("text_content", "")
        self.show_debug = settings.value("show_debug", "false") == "true"
        self.font_weight = int(settings.value("font_weight", QFont.Weight.Normal))
        self.settings_dialog_geometry = settings.value("settings_dialog_geometry")
        self.always_on_top = settings.value("always_on_top", "false") == "true"

        self.log_debug(f"Loaded settings - Debug: {self.show_debug}")
        self.log_debug(f"Loaded settings - Always On Top: {self.always_on_top}")
        self.log_debug(f"Loaded settings - Theme: {self.theme_mode}")
        self.log_debug(f"Loaded settings - Font-Family: {self.font_name}, Font-Size: {self.font_size}")
        self.log_debug(f"Loaded settings - Font-Weight: {self.font_weight}")
        
        # Load window geometry and state
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
            self.log_debug("Restored window geometry")
        else:
            self.setGeometry(100, 100, 800, 600)
            self.log_debug("Using default window geometry")
            
        state = settings.value("window_state")
        if state:
            self.restoreState(state)
            self.log_debug("Restored window state")
    
    def closeEvent(self, event):
        # Save current text content before closing
        self.text_content = self.text_area.toPlainText()
        self.save_settings_to_file()
        event.accept()

def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    
    # Set application icon
    try:
        app_icon = QIcon('icon.ico')
        app.setWindowIcon(app_icon)
    except Exception as e:
        print(f"Error setting application icon: {e}")
    
    # Set application ID for Windows
    if sys.platform == 'win32':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                'com.rise.TextArea.1')
        except Exception as e:
            print(f"Error setting AppUserModelID: {e}")
    
    editor = TextAreaApp()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
