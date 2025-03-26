#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from menu import ChineseChessMenu

def main():
    """Hàm chính để khởi động ứng dụng cờ tướng"""
    app = QApplication(sys.argv)
    menu = ChineseChessMenu()
    menu.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
