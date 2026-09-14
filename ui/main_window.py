"""
Main Window - SF-Encryptor Application Main Window.

This module provides the MainWindow class which serves as the primary
application window containing all tabs and core functionality.
"""

import os
import sys
import json
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QButtonGroup, QStatusBar, QMessageBox, QApplication,
    QLabel
)
from PyQt6.QtGui import QIcon, QGuiApplication, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize

from utils.helpers import load_settings, save_settings, setup_directories, get_app_icon_path
from utils.animation_manager import AnimationManager
from utils.localization import LocalizationManager
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.file_integrity_tab import FileIntegrityTab
from ui.tabs.encrypt_tab import EncryptTab
from ui.tabs.decrypt_tab import DecryptTab
from ui.tabs.generate_keys_tab import GenerateKeysTab
from ui.tabs.key_management_tab import KeyManagementTab
from ui.tabs.plugins_tab import PluginsTab
from ui.tabs.logs_tab import LogsTab
from ui.tabs.about_tab import AboutTab

logger = logging.getLogger(__name__)

# Modern UI Theme
THEME_PRIMARY_BG = "#f6f8f7"
THEME_SECONDARY_BG = "#123b3a"
THEME_FOREGROUND = "#183332"
THEME_ACCENT = "#e07a5f"
THEME_ACCENT_DARK = "#bd5c45"
THEME_BORDER = "#dce5e2"
THEME_CARD_BG = "#ffffff"
THEME_MUTED = "#607d7a"

MODERN_STYLESHEET = f"""
    QWidget {{
        background-color: {THEME_PRIMARY_BG};
        color: {THEME_FOREGROUND};
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 10pt;
    }}
    QLabel {{
        background-color: transparent;
    }}
    QMainWindow {{
        background-color: {THEME_PRIMARY_BG};
    }}
    #MainContainer {{
        background-color: {THEME_PRIMARY_BG};
    }}
    #Sidebar {{
        background-color: #123b3a;
        border: none;
        padding: 12px;
    }}
    #BrandTitle {{
        color: #f7fbf9;
        background-color: transparent;
        font-size: 18pt;
        font-weight: 700;
    }}
    #BrandLogo {{
        background-color: transparent;
        padding: 2px 0 8px;
    }}
    #BrandSubtitle {{
        color: #a9c4bd;
        background-color: transparent;
        font-size: 8pt;
        font-weight: 600;
    }}
    #SectionLabel {{
        color: #82a59d;
        background-color: transparent;
        font-size: 8pt;
        font-weight: 700;
        padding: 18px 12px 6px;
    }}
    #NavButton {{
        background-color: transparent;
        border: none;
        padding: 11px 14px;
        text-align: left;
        border-radius: 6px;
        font-weight: 500;
        color: #c5d9d3;
        font-size: 10pt;
    }}
    #NavButton:hover {{
        background-color: #1d4c49;
        color: #ffffff;
    }}
    #NavButton:checked {{
        background-color: {THEME_ACCENT};
        color: white;
        font-weight: bold;
    }}
    #MainContentArea {{
        background-color: {THEME_PRIMARY_BG};
        border: none;
    }}
    #PageHeader {{
        background-color: {THEME_CARD_BG};
        border-bottom: 1px solid {THEME_BORDER};
        padding: 18px 28px;
    }}
    #PageTitle {{
        color: {THEME_FOREGROUND};
        background-color: transparent;
        font-size: 18pt;
        font-weight: 700;
    }}
    #PageSubtitle {{
        color: {THEME_MUTED};
        background-color: transparent;
        font-size: 9pt;
    }}
    QPushButton {{
        background-color: {THEME_ACCENT};
        color: white;
        border: none;
        padding: 10px 18px;
        border-radius: 6px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {THEME_ACCENT_DARK};
    }}
    QPushButton:pressed {{
        background-color: {THEME_ACCENT_DARK};
    }}
    QPushButton:disabled {{
        background-color: {THEME_BORDER};
        color: {THEME_MUTED};
    }}
    #SidebarFooter {{
        color: #82a59d;
        background-color: transparent;
        font-size: 8pt;
        padding: 10px 12px;
    }}
    QScrollArea, QScrollArea > QWidget > QWidget {{
        background-color: {THEME_PRIMARY_BG};
        border: none;
    }}
    QGroupBox {{
        background-color: {THEME_CARD_BG};
        border: 1px solid {THEME_BORDER};
        border-radius: 8px;
        margin-top: 12px;
        padding: 22px 14px 14px;
        font-weight: 700;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        color: {THEME_FOREGROUND};
        background-color: {THEME_CARD_BG};
    }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox {{
        background-color: #ffffff;
        color: {THEME_FOREGROUND};
        border: 1px solid {THEME_BORDER};
        border-radius: 5px;
        padding: 8px 10px;
        selection-background-color: {THEME_ACCENT};
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 2px solid {THEME_ACCENT};
        padding: 7px 9px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 26px;
    }}
    QCheckBox, QRadioButton {{
        spacing: 7px;
        color: {THEME_FOREGROUND};
    }}
    QListWidget {{
        background-color: #ffffff;
        border: 1px solid {THEME_BORDER};
        border-radius: 6px;
        padding: 4px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 9px;
        border-radius: 4px;
    }}
    QListWidget::item:selected {{
        background-color: #f7d8cf;
        color: {THEME_FOREGROUND};
    }}
    QProgressBar {{
        background-color: #e9efed;
        border: none;
        border-radius: 5px;
        text-align: center;
        color: {THEME_FOREGROUND};
    }}
    QProgressBar::chunk {{
        background-color: {THEME_ACCENT};
        border-radius: 5px;
    }}
    QStatusBar {{
        background-color: #ffffff;
        color: {THEME_MUTED};
        border-top: 1px solid {THEME_BORDER};
    }}
    QScrollBar:vertical {{
        background-color: #edf2f0;
        width: 10px;
        margin: 2px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: #b8c9c4;
        min-height: 36px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {THEME_ACCENT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

class MainWindow(QMainWindow):
    """Main application window for SF-Encryptor."""
    
    log_signal = pyqtSignal(str, str)  # level, message
    
    def __init__(self, plugin_manager, key_manager, localization_manager, app_settings):
        """
        Initialize the main window.
        
        Args:
            plugin_manager: Plugin management instance
            key_manager: Key management instance  
            localization_manager: Localization management instance
            app_settings: Application settings dictionary
        """
        super().__init__()
        
        # Store references to managers
        self.plugin_manager = plugin_manager
        self.key_manager = key_manager
        self.localization_manager = localization_manager
        
        # Load settings if not provided
        if not app_settings:
            from utils.helpers import load_settings
            self.app_settings = load_settings()
        else:
            self.app_settings = app_settings

        self.animation_manager = AnimationManager(self, self.app_settings)
        
        # Get directories
        self.directories = setup_directories()
        
        logger.info("Initializing main window")
        
        # Setup UI
        self.setup_ui()
        self.setup_status_bar()
        self.clear_child_styles()
        self.apply_theme()
        
        # Initialize with welcome message
        self.show_status_message("SF FileManager initialized successfully", 3000)
        
        logger.info("Main window initialized successfully")
    
    def setup_ui(self):
        """Set up the main user interface."""
        # Set window properties
        self.setWindowTitle("SF-Encryptor v3.0.0 - Secure File Encryption")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set application icon
        icon_path = get_app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        
        # Create main container
        main_container = QWidget()
        main_container.setObjectName("MainContainer")
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_container)
        
        # Create sidebar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("Sidebar")
        self.sidebar_widget.setFixedWidth(270)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sidebar_layout.setContentsMargins(14, 24, 14, 14)
        self.create_sidebar_header()
        
        # Create content area
        content_container = QWidget()
        content_container.setObjectName("MainContentArea")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        page_header = QWidget()
        page_header.setObjectName("PageHeader")
        page_header_layout = QVBoxLayout(page_header)
        page_header_layout.setContentsMargins(28, 20, 28, 18)
        page_header_layout.setSpacing(3)
        self.page_title = QLabel("Encrypt")
        self.page_title.setObjectName("PageTitle")
        self.page_subtitle = QLabel("Protect files and folders with your selected encryption method.")
        self.page_subtitle.setObjectName("PageSubtitle")
        page_header_layout.addWidget(self.page_title)
        page_header_layout.addWidget(self.page_subtitle)
        content_layout.addWidget(page_header)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("MainContentArea")
        content_layout.addWidget(self.stacked_widget, 1)
        
        # Create navigation buttons and tabs (simplified for now)
        self.create_navigation_and_tabs()
        
        # Add widgets to main layout
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(content_container, 1)
        
        # Set initial tab
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
            self.stacked_widget.setCurrentIndex(0)
            QTimer.singleShot(80, lambda: self.animation_manager.animate_page(self.tabs[0]))

    def create_sidebar_header(self):
        """Create the application identity block in the sidebar."""
        logo_label = QLabel()
        logo_label.setObjectName("BrandLogo")
        icon_path = get_app_icon_path()
        if icon_path:
            logo_pixmap = QPixmap(icon_path)
            if not logo_pixmap.isNull():
                logo_label.setPixmap(logo_pixmap.scaled(
                    42,
                    42,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))
        brand_title = QLabel("SF Encryptor")
        brand_title.setObjectName("BrandTitle")
        brand_subtitle = QLabel("PRIVATE FILE PROTECTION")
        brand_subtitle.setObjectName("BrandSubtitle")
        section_label = QLabel("WORKSPACE")
        section_label.setObjectName("SectionLabel")
        self.sidebar_layout.addWidget(logo_label)
        self.sidebar_layout.addWidget(brand_title)
        self.sidebar_layout.addWidget(brand_subtitle)
        self.sidebar_layout.addWidget(section_label)
    
    def create_navigation_and_tabs(self):
        """Create navigation buttons and corresponding tabs."""
        # Create fully functional tabs
        self.tabs = []
        tab_configs = [
            ("Encrypt", "encrypt.png"),
            ("Decrypt", "decrypt.png"),
            ("Generate Keys", "fingerprint.png"),
            ("Key Management", "fingerprint.png"),
            ("File Integrity", "fingerprint.png"),
            ("Plugins", "plugins.png"),
            ("Settings", "settings.png"),
            ("Logs", "log.png"),
            ("About", "about.png")
        ]
        
        # Create tabs and navigation buttons
        self.nav_buttons = []
        self.button_group = QButtonGroup(self)
        
        for i, (name, icon_filename) in enumerate(tab_configs):
            # Create fully functional tab content
            if name == "Encrypt":
                # Use the real EncryptTab
                tab_widget = EncryptTab(self.plugin_manager, self.app_settings, self)
            elif name == "Decrypt":
                # Use the real DecryptTab
                tab_widget = DecryptTab(self.plugin_manager, self.app_settings, self)
            elif name == "Generate Keys":
                # Use the real GenerateKeysTab
                tab_widget = GenerateKeysTab(self.plugin_manager, self.key_manager, self.app_settings, self)
            elif name == "Key Management":
                # Use the real KeyManagementTab
                tab_widget = KeyManagementTab(self.key_manager, self.app_settings, self)
            elif name == "Settings":
                # Use the real SettingsTab
                tab_widget = SettingsTab(self.plugin_manager, self.app_settings, self)
            elif name == "File Integrity":
                # Use the real FileIntegrityTab  
                tab_widget = FileIntegrityTab(self)
            elif name == "Plugins":
                # Use the real PluginsTab
                tab_widget = PluginsTab(self.plugin_manager, self.app_settings, self)
            elif name == "Logs":
                # Use the real LogsTab
                tab_widget = LogsTab(self.app_settings, self)
            elif name == "About":
                # Use the real AboutTab
                tab_widget = AboutTab(self.app_settings, self)
            else:
                # Fallback - this should not happen in production
                tab_widget = QWidget()
                tab_layout = QVBoxLayout(tab_widget)
                
                # Load icon for fallback
                icon_path = os.path.join(self.directories['assets'], icon_filename)
                icon_display = ""
                if os.path.exists(icon_path):
                    icon_display = f"[IMG] {name}"
                else:
                    icon_display = f"[FILE] {name}"
                
                error_label = QLabel(f"{icon_display} Tab\n\nTab loading error - please contact support.")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet("""
                    QLabel {
                        font-size: 16pt;
                        color: #dc3545;
                        padding: 40px;
                        background-color: white;
                        border-radius: 10px;
                        border: 1px solid #dc3545;
                    }
                """)
                tab_layout.addWidget(error_label)
            
            self.tabs.append(tab_widget)
            self.stacked_widget.addWidget(tab_widget)
            
            # Create navigation button with icon
            nav_button = QPushButton(f"  {name}")
            nav_button.setObjectName("NavButton")
            nav_button.setCheckable(True)
            nav_button.clicked.connect(lambda checked, index=i: self.switch_tab(index))
            
            # Set button icon
            icon_path = os.path.join(self.directories['assets'], icon_filename)
            if os.path.exists(icon_path):
                nav_button.setIcon(QIcon(icon_path))
                nav_button.setIconSize(QIcon.fromTheme("").actualSize(QIcon.fromTheme("").actualSize(nav_button.size()) or nav_button.size()))
                # Set a reasonable icon size
                nav_button.setIconSize(QSize(20, 20))
            
            self.nav_buttons.append(nav_button)
            self.button_group.addButton(nav_button, i)
            self.sidebar_layout.addWidget(nav_button)
        
        # Add stretch to push buttons to top
        self.sidebar_layout.addStretch()
        footer = QLabel("SF Encryptor 3.0\nSecure by design")
        footer.setObjectName("SidebarFooter")
        self.sidebar_layout.addWidget(footer)
    
    def switch_tab(self, index):
        """Switch to the specified tab."""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            self.animation_manager.animate_page(self.stacked_widget.widget(index))
            
            # Update button states
            for i, button in enumerate(self.nav_buttons):
                button.setChecked(i == index)
            
            # Update status bar
            tab_names = ["Encrypt", "Decrypt", "Generate Keys", "Key Management", 
                        "File Integrity", "Plugins", "Settings", "Logs", "About"]
            tab_subtitles = [
                "Protect files and folders with your selected encryption method.",
                "Restore encrypted files and verify their integrity.",
                "Create strong keys for your encryption workflows.",
                "Organize, inspect, and remove stored key references.",
                "Compare file hashes and confirm files were not changed.",
                "Manage the encryption methods available to the application.",
                "Tune appearance, security, and application preferences.",
                "Review application activity and export diagnostic records.",
                "Learn more about SF Encryptor and the project.",
            ]
            if index < len(tab_names):
                self.page_title.setText(tab_names[index])
                self.page_subtitle.setText(tab_subtitles[index])
                self.show_status_message(f"Switched to {tab_names[index]} tab")
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def apply_theme(self):
        """Apply the modern theme to the application."""
        self.setStyleSheet(MODERN_STYLESHEET)

    def clear_child_styles(self):
        """Remove tab-local styles so the application theme stays consistent."""
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet("")
    
    def show_status_message(self, message, timeout=5000):
        """
        Show a message in the status bar.
        
        Args:
            message (str): Message to display
            timeout (int): Timeout in milliseconds (0 for permanent)
        """
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, timeout)
        logger.info(f"Status: {message}")
    
    def optimize_window_size(self):
        """Optimize window size based on screen resolution."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Calculate optimal window size
            if screen_width >= 1920 and screen_height >= 1080:
                window_width = 1400
                window_height = 900
                min_width = 1200
                min_height = 800
            elif screen_width >= 1366 and screen_height >= 768:
                window_width = min(1200, int(screen_width * 0.8))
                window_height = min(800, int(screen_height * 0.8))
                min_width = 1000
                min_height = 700
            else:
                window_width = min(1000, int(screen_width * 0.9))
                window_height = min(700, int(screen_height * 0.9))
                min_width = 800
                min_height = 600
            
            self.setMinimumSize(min_width, min_height)
            self.resize(window_width, window_height)
            
            # Center window
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings before closing
        save_settings(self.app_settings)
        
        # Ask for confirmation if enabled
        if self.app_settings.get("confirm_on_exit", True):
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                logger.info("Application closing by user request")
                event.accept()
            else:
                event.ignore()
        else:
            logger.info("Application closing")
            event.accept()
    
    def load_settings(self):
        """Load application settings (fallback method)."""
        return load_settings()
    
    def save_settings(self):
        """Save application settings."""
        save_settings(self.app_settings)
        logger.info("Settings saved")
    
    def get_current_tab_index(self):
        """Get the index of the currently active tab."""
        return self.stacked_widget.currentIndex()
    
    def get_localized_string(self, key, **kwargs):
        """Get a localized string."""
        return self.localization_manager.get_string(key, **kwargs)
    
    def log_message(self, level, message):
        """Log a message and emit signal for log viewer."""
        getattr(logger, level.lower(), logger.info)(message)
        self.log_signal.emit(level, message)
