"""
PyQt5 Chrome-like Browser
Features:
- Chrome look with tabs
- Default DuckDuckGo search
- Copy/Share links
- Fullscreen toggle
- Keyboard shortcuts
- Favicon support
Compatible with PyQt5 5.15.x
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl, Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QClipboard, QKeySequence, QPixmap, QPainter, QPalette, QColor, QFont

DEFAULT_SEARCH = "https://duckduckgo.com/?q={}"

class ChromeLookBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChromeLookBrowser")
        self.setGeometry(100, 100, 1200, 800)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)

        # Toolbar
        self.create_toolbar()

        # Add initial tab
        self.add_new_tab("about:blank", "New Tab")
        self.show()

    def create_toolbar(self):
        self.navbar = QToolBar()
        self.navbar.setMovable(False)
        self.navbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.navbar)

        # Back button
        self.back_btn = QAction("←", self)
        self.back_btn.triggered.connect(self.navigate_back)
        self.back_btn.setShortcut(QKeySequence("Alt+Left"))
        self.navbar.addAction(self.back_btn)

        # Forward button
        self.forward_btn = QAction("→", self)
        self.forward_btn.triggered.connect(self.navigate_forward)
        self.forward_btn.setShortcut(QKeySequence("Alt+Right"))
        self.navbar.addAction(self.forward_btn)

        # Reload button
        self.reload_btn = QAction("↻", self)
        self.reload_btn.triggered.connect(self.reload_tab)
        self.reload_btn.setShortcut(QKeySequence("F5"))
        self.navbar.addAction(self.reload_btn)

        # Copy link button
        self.copy_btn = QAction("Copy Link", self)
        self.copy_btn.triggered.connect(self.copy_link)
        self.navbar.addAction(self.copy_btn)

        # Share button
        self.share_btn = QAction("Share", self)
        self.share_btn.triggered.connect(self.share_link)
        self.navbar.addAction(self.share_btn)

        self.navbar.addSeparator()

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or type URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Go button
        self.go_btn = QAction("Go", self)
        self.go_btn.triggered.connect(self.navigate_to_url)
        self.navbar.addAction(self.go_btn)

        # New Tab button
        self.new_tab_btn = QAction("+", self)
        self.new_tab_btn.triggered.connect(lambda: self.add_new_tab("about:blank", "New Tab"))
        self.new_tab_btn.setShortcut(QKeySequence("Ctrl+T"))
        self.navbar.addAction(self.new_tab_btn)

        # Fullscreen toggle
        self.fullscreen_btn = QAction("Fullscreen", self)
        self.fullscreen_btn.setCheckable(True)
        self.fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        self.navbar.addAction(self.fullscreen_btn)

    # Navigation functions
    def navigate_back(self):
        self.current_tab().back()

    def navigate_forward(self):
        self.current_tab().forward()

    def reload_tab(self):
        self.current_tab().reload()

    def navigate_to_url(self):
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        qurl = QUrl.fromUserInput(url_text)
        if not qurl.isValid():
            qurl = QUrl(DEFAULT_SEARCH.format(url_text))
        self.current_tab().setUrl(qurl)

    # Tabs
    def add_new_tab(self, url, label):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # Connect signals
        browser.urlChanged.connect(lambda qurl, b=browser: self.update_urlbar(qurl, b))
        browser.loadFinished.connect(lambda _: self.update_nav_buttons())
        browser.urlChanged.connect(lambda _: self.update_nav_buttons())
        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(title, b))
        browser.iconChanged.connect(lambda icon, b=browser: self.update_tab_icon(icon, b))

    def close_tab(self, index):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    def current_tab(self):
        return self.tabs.currentWidget()

    # Update URL bar and tab title
    def update_urlbar(self, qurl, browser):
        if browser != self.current_tab():
            return
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, title)
        if browser == self.current_tab():
            self.setWindowTitle(f"{title} - ChromeLookBrowser")

    def update_tab_icon(self, icon, browser):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabIcon(index, icon)

    # Enable/Disable back/forward buttons
    def update_nav_buttons(self):
        b = self.current_tab()
        if b:
            self.back_btn.setEnabled(b.history().canGoBack())
            self.forward_btn.setEnabled(b.history().canGoForward())

    # Copy link with temporary notification
    def copy_link(self):
        url = self.current_tab().url().toString()
        QApplication.clipboard().setText(url)
        self.show_temp_message("✔ Link copied")

    # Share link
    def share_link(self):
        url = self.current_tab().url().toString()
        QApplication.clipboard().setText(url)
        self.show_temp_message("✔ Link ready to share")

    # Temporary overlay message (no animation)
    def show_temp_message(self, message):
        label = QLabel(message, self)
        label.setStyleSheet(
            "background-color: black; color: white; padding: 5px; border-radius: 5px; font-weight: bold;"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(180)
        label.move((self.width() - label.width()) // 2, 50)
        label.show()

        # Remove after 1 second
        QTimer.singleShot(1000, label.deleteLater)

    # Fullscreen toggle
    def toggle_fullscreen(self, checked):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

# Main
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ChromeLookBrowser")

    # Set global User-Agent after QApplication exists
    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    )

    window = ChromeLookBrowser()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
