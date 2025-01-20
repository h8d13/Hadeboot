import os
import ast
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                            QVBoxLayout, QWidget, QSplitter, QTextEdit, QStyle)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QColor

class FileAnalyzer:
    def analyze_python_file(self, file_path: Path) -> list:
        """Returns a list of symbols/components in VS Code outline style"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            tree = ast.parse(content)
            symbols = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.ImportFrom, ast.Import)):
                    symbol = {
                        'type': type(node).__name__,
                        'name': '',
                        'lineno': node.lineno,
                        'args': []
                    }
                    
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        symbol['name'] = node.name
                        if isinstance(node, ast.FunctionDef):
                            symbol['args'] = [arg.arg for arg in node.args.args]
                    
                    elif isinstance(node, ast.ImportFrom):
                        symbol['name'] = f"from {node.module} import {', '.join(n.name for n in node.names)}"
                    
                    elif isinstance(node, ast.Import):
                        symbol['name'] = f"import {', '.join(n.name for n in node.names)}"
                    
                    symbols.append(symbol)
            
            return sorted(symbols, key=lambda x: x['lineno'])
            
        except Exception as e:
            return [{'type': 'Error', 'name': str(e), 'lineno': 0}]

class ProjectViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Project Outline")
        self.setGeometry(100, 100, 1000, 900)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create outline tree
        self.outline = QTreeWidget()
        self.outline.setHeaderLabels(["Symbol", "Type"])
        self.outline.setColumnWidth(0, 400)
        
        # Set font
        font = QFont("Consolas" if os.name == 'nt' else "Monospace")
        font.setPointSize(10)
        self.outline.setFont(font)
        
        # Style improvements
        self.outline.setAlternatingRowColors(True)
        self.outline.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
            }
            QTreeWidget::item:hover {
                background-color: #3c3c3c;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #d4d4d4;
                padding: 5px;
                border: 1px solid #3c3c3c;
            }
        """)
        
        layout.addWidget(self.outline)
        
        self.analyzer = FileAnalyzer()
        self.icon_provider = self.style()
        
        # Scan directory
        self.scan_directory()

    def scan_directory(self, path: str = '.'):
        """Recursively scan directory for Python files"""
        self.outline.clear()
        root_item = QTreeWidgetItem(self.outline)
        root_item.setText(0, "Project Root")
        root_item.setText(1, "Root")
        root_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        self._scan_directory_recursive(Path(path), root_item)
        root_item.setExpanded(True)

    def _scan_directory_recursive(self, path: Path, parent_item: QTreeWidgetItem):
        """Helper method for recursive directory scanning"""
        try:
            for entry in os.scandir(path):
                if entry.is_file() and entry.name.endswith('.py'):
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, entry.name)
                    file_item.setText(1, "File")
                    file_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
                    
                    # Analyze file content
                    symbols = self.analyzer.analyze_python_file(Path(entry.path))
                    self.add_symbols(file_item, symbols, entry.path)
                    file_item.setExpanded(True)
                
                elif entry.is_dir() and not entry.name.startswith('.'):
                    dir_item = QTreeWidgetItem(parent_item)
                    dir_item.setText(0, entry.name)
                    dir_item.setText(1, "Directory")
                    dir_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                    self._scan_directory_recursive(Path(entry.path), dir_item)
                    dir_item.setExpanded(True)
        
        except Exception as e:
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, f"Error: {str(e)}")
            error_item.setText(1, "Error")

    def add_symbols(self, parent: QTreeWidgetItem, symbols: list, file_path: str):
        """Add symbols to the outline tree"""
        symbols_by_class = {}
        
        for symbol in symbols:
            if symbol['type'] in ('ImportFrom', 'Import'):
                imports_header = self._get_or_create_header(parent, "Imports")
                item = QTreeWidgetItem(imports_header)
                item.setText(0, symbol['name'])
                item.setText(1, "Import")
                item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
                
            elif symbol['type'] == 'ClassDef':
                class_item = QTreeWidgetItem(parent)
                class_item.setText(0, symbol['name'])
                class_item.setText(1, "Class")
                class_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                symbols_by_class[symbol['name']] = class_item
                
            elif symbol['type'] == 'FunctionDef':
                is_method = False
                for node in ast.walk(ast.parse(open(file_path).read())):
                    if (isinstance(node, ast.ClassDef) and 
                        symbol['lineno'] > node.lineno and 
                        symbol['lineno'] < node.end_lineno):
                        if node.name in symbols_by_class:
                            is_method = True
                            item = QTreeWidgetItem(symbols_by_class[node.name])
                            break
                
                if not is_method:
                    item = QTreeWidgetItem(parent)
                
                args_str = f"({', '.join(symbol['args'])})"
                item.setText(0, symbol['name'] + args_str)
                item.setText(1, "Method" if is_method else "Function")
                item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))

    def _get_or_create_header(self, parent: QTreeWidgetItem, header_text: str) -> QTreeWidgetItem:
        """Get existing header or create new one"""
        for i in range(parent.childCount()):
            if parent.child(i).text(0) == header_text:
                return parent.child(i)
        
        header = QTreeWidgetItem(parent)
        header.setText(0, header_text)
        header.setText(1, "Section")
        header.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        return header

def main():
    app = QApplication(sys.argv)
    viewer = ProjectViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()