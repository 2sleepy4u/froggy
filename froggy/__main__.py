import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSizePolicy, QMenu, QAction, QSystemTrayIcon, QLineEdit, QScrollArea
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread, QPropertyAnimation, QEasingCurve, QTimer
import randfacts
import ollama
from importlib.resources import files

stylesheet = "color: white; font-size: 15px; background-color: rgba(0, 0, 0, 180); border-radius: 15px;   padding: 10px;   border: 2px solid white;  "
frog_png = str(files('froggy').joinpath('images/frog.png'))

class AThread(QThread):
    def __init__(self, parent, text) -> None:
        super().__init__(parent=parent)
        self.text = text

    def run(self):
        try:
            response = ollama.chat(
                model='phi3',
                messages=[
                    {'role': 'system', 'content': "You are a friendly chatbot who always responds in the style of a frog"},
                    {'role': 'user', 'content': self.text}
                    ],
                stream=False,
                )
            self.answer = response["message"]["content"]
        except Exception:
            self.answer = "I'm not able to connect to the mighty llama."


class SpeechWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        # Create a QLabel with long text content
        self.label = QLabel()
        self.label.setText("")  # Long text to show scrolling
        self.label.setWordWrap(True)  # Wrap the text within the label's width
        self.label.setStyleSheet("background-color: rgba(0,0,0,0); border: none;") 
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  

        # Set a fixed size for the label
        self.label.setFixedSize(290, 200)

        # Create a QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)  # To ensure the content can be resized properly
        self.scroll_area.setFixedSize(300, 200)  # Set fixed size for scroll area itself
        self.scroll_area.setStyleSheet("""
            * { 
                color: white;
                font-size: 15px; 
                padding: 10px;   
            }
            QScrollArea {
                background-color: rgba(0, 0, 0, 180); 
                border-radius: 15px;   
                padding: 10px;   
                border: 2px solid white;
            }
            QScrollBar:vertical {
                width: 0px;
            }
        """) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scroll
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set up the layout and add the scroll area
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

    def show_ribbit(self, text, duration = 5000):
        self.scroll_area.setFixedHeight(200)
        self.label.setText(text)
        
        QTimer.singleShot(duration, self.clear_ribbit)  

    def clear_ribbit(self):
        self.label.setText("")
        self.scroll_area.setFixedHeight(0)

class _SpeechWidget(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setWordWrap(True)
        self.setStyleSheet("color: white; font-size: 15px;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        self.setAlignment(Qt.AlignTop)

    def show_ribbit(self, text, duration = 5000, ribbit = True):
        text = text + "\nRibbit!" if ribbit else ""
        self.setText(text)
        self.setStyleSheet(stylesheet)
        self.adjustSize()
        
        QTimer.singleShot(duration, self.clear_ribbit)  

    def clear_ribbit(self):
        self.setText("")
        self.setStyleSheet("color: white; font-size: 15px;") 



class PromptWidget(QLineEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setPlaceholderText("Ask for anything")
        self.setStyleSheet(stylesheet) 
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def show(self):
        self.setText("")
        self.setFocus()
        super().show()

class FrogWidget(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setPixmap(QPixmap(frog_png))  
        self.setFixedSize(self.pixmap().size())
        self.setAlignment(Qt.AlignBottom)

class ReminderWidget(QTimer):
    def __init__(self, text = "", interval = 1000) -> None:
        super().__init__()
        self.text = text
        self.start(interval)

class ReminderManager():
    def __init__(self, callback) -> None:
        self.callback = callback
        self.list = []
    def add(self, reminder: ReminderWidget):
        self.list.append(reminder)
        return self
    def start(self):
        for reminder in self.list:
            reminder.timeout.connect(lambda: self.callback(reminder.text))
    def stop(self):
        for reminder in self.list:
            reminder.stop() 





class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        self.dragging = False
        self.startPos = QPoint(0, 0)
        self.answer_thread = None

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.ribbit_label = SpeechWidget()

        self.text_edit = PromptWidget() 
        self.text_edit.returnPressed.connect(self.send_text)

        self.frog_label = FrogWidget()
        
        self.layout.addWidget(self.ribbit_label)
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.frog_label)
             
        self.setFixedSize(self.frog_label.width() + 210, self.frog_label.height() + 300)  

        screen_geometry = QApplication.desktop().availableGeometry()
        self.move(0, screen_geometry.height() - self.height())

        self.reminder = ReminderManager(lambda x: self.ribbit_label.show_ribbit(x, 2000))
        self.reminder.add(ReminderWidget("It's time to take a break!", 1000 * 60 * 60))
        self.reminder.start()

        # Animation setup (for thinking behavior)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(300)  # Duration of 1 second per pulse (up/down)
        self.animation.setLoopCount(-1)  # Loop indefinitely until stopped

        self.ribbit_label.show_ribbit("Right click on me to view the menu. \nDouble click on me to get a random fun fact!")


    def startThinkingAnimation(self):
        # Set the animation geometry to "pulse" the frog (scaling effect)
        initial_geometry = self.geometry()
        expanded_geometry = self.geometry().adjusted(0, -2, 0, 0)  # Grow the frog's size

        # Animate between original and expanded size
        self.animation.setStartValue(initial_geometry)
        self.animation.setEndValue(expanded_geometry)

        self.animation.start()

    def stopThinkingAnimation(self):
        # Stop the animation and reset to original geometry
        self.animation.stop()



    def contextMenuEvent(self, event):
        # Create the context menu
        context_menu = QMenu(self)

        context_menu.setStyleSheet(stylesheet) 
        # Add actions to the menu
        close_action = QAction("Dismiss", self)
        ask_action = QAction("Inquiry", self)
        context_menu.addAction(ask_action)
        context_menu.addAction(close_action)

        # Connect actions to methods
        close_action.triggered.connect(lambda: QApplication.quit())
        ask_action.triggered.connect(self.text_edit.show)

        # Show the menu at the mouse position
        context_menu.exec_(event.globalPos())

    def send_text(self):
        if self.answer_thread is not None and not self.answer_thread.isFinished():
            return self.ribbit_label.show_ribbit("Wait... I'm thinking...")

        self.text_edit.hide()
        text = self.text_edit.text()

        self.answer_thread = AThread(parent=self, text=text)
        self.answer_thread.finished.connect(self.do_answer)
        self.startThinkingAnimation()
        self.answer_thread.start()
       
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.startPos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.pos() + event.pos() - self.startPos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            text = randfacts.get_fact()
            self.ribbit_label.show_ribbit(text)

    def do_answer(self):
        if self.answer_thread is not None:
            answer = self.answer_thread.answer
            #calculate how many seconds for a reading speed of 130 words per minute
            ms = int(1000 * 60 * len(answer.split()) / 130)
            self.ribbit_label.show_ribbit(answer, ms)
        self.stopThinkingAnimation()

class FroggyApp(QApplication):
    def __init__(self) -> None:
        super().__init__(sys.argv)
        self.tray_icon = QSystemTrayIcon(QIcon(frog_png), self)
        self.tray_icon.setToolTip("Froggy!")
            # Create the right-click menu
        self.menu = QMenu()

        # Add an action to quit the application
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(lambda: sys.exit(self.exec_()))
        self.menu.addAction(self.quit_action)

        # Set the context menu
        self.tray_icon.setContextMenu(self.menu)

        # Show the tray icon
        self.tray_icon.show()

        self.frog_widget = MainWidget()
        self.frog_widget.show()


    def run(self):
        sys.exit(self.exec_())

def main():
    FroggyApp().run()

if __name__ == '__main__':
    main()
