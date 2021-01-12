import sys
import os
from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidgetItem, QDialog
import sqlite3


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('library.ui', self)
        self.con = sqlite3.connect('library.db')

        self.pushButton.clicked.connect(self.search)

    def search(self):
        self.statusBar.showMessage('')
        self.listWidget.clear()
        if self.comboBox.currentText() == 'Автор':
            books = list(map(lambda x: x[0], list(self.con.cursor().execute("""SELECT title FROM books WHERE author_id in
             (SELECT id FROM authors WHERE name LIKE ?)""", ('%' + self.lineEdit.text() + '%', )))))
        else:
            books = list(map(lambda x: x[0], list(self.con.cursor().execute("""SELECT title FROM books WHERE
             title LIKE ?""", ('%' + self.lineEdit.text() + '%', )))))
        if not books:
            self.statusBar.showMessage('В библиотеке нет подходящих книг')
        else:
            for i in books:
                newButton = QPushButton(i)
                newButton.clicked.connect(self.show_info)
                listWidgetItem = QListWidgetItem()
                listWidgetItem.setSizeHint(newButton.sizeHint())
                self.listWidget.addItem(listWidgetItem)
                self.listWidget.setItemWidget(listWidgetItem, newButton)

    def show_info(self):
        title = self.sender().text()
        image = list(map(lambda x: x[0], list(self.con.cursor().execute("""SELECT image FROM books WHERE title == ?""",
                                                                        (title, )))))[0]
        if image is None:
            image = 'standart.jpg'
        image =  os.path.join('data', image)
        author = list(map(lambda x: x[0], list(self.con.cursor().execute("""SELECT name FROM authors WHERE id in
         (SELECT author_id FROM books WHERE title == ?)""", (title,)))))[0]
        year = list(map(lambda x: x[0], list(self.con.cursor().execute("""SELECT year FROM books WHERE title == ?""",
                                                                       (title,)))))[0]
        genre = list(map(lambda x: x[0], list(self.con.cursor().execute("""SELECT genre FROM genres WHERE id in
                 (SELECT genre_id FROM books WHERE title == ?)""", (title,)))))[0]
        self.dialog = Dialog(image, title, author, year, genre)
        self.dialog.show()
        self.dialog.exec_()


class Dialog(QDialog):
    def __init__(self, image, title, author, year, genre):
        super().__init__()
        uic.loadUi("lib_dialog.ui", self)
        self.setModal(True)
        im = Image.open(image)
        im = im.resize((211, 281))
        im.save('res.jpg')
        self.pixmap = QPixmap('res.jpg')
        self.label.setPixmap(self.pixmap)
        self.plainTextEdit.setPlainText(title)
        self.plainTextEdit_2.setPlainText(author)
        self.plainTextEdit_3.setPlainText(str(year))
        self.plainTextEdit_4.setPlainText(genre)


app = QApplication(sys.argv)
w = App()
w.show()
sys.exit(app.exec_())
