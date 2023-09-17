# Slack Messages Extract Tool
# V1.2.4 - 2023.9.17 
# Created By ChatGPT
# Prompt and Adapted by Milvoid

import sys
import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox, QCheckBox

class ChatExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Slack 消息记录提取工具')
        self.setGeometry(100, 100, 400, 300)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText('选择 JSON 格式的 Slack 消息记录...')
        self.text_edit.setMinimumHeight(300)

        self.browse_button = QPushButton('浏览文件', self)
        self.browse_button.clicked.connect(self.browseFiles)

        self.combine_checkbox = QCheckBox('将消息记录合并到同一个文件', self)

        self.export_dir_text_edit = QTextEdit(self)
        self.export_dir_text_edit.setPlaceholderText('选择 Markdown 文件导出目录...')

        self.export_button = QPushButton('导出目录', self)
        self.export_button.clicked.connect(self.selectExportDir)

        self.confirm_button = QPushButton('确认导出', self)
        self.confirm_button.clicked.connect(self.exportChat)

        copyright_label = QLabel('<br>V1.2.4 By <a href="https://milvoid.com">Milvoid</a>', self)
        copyright_label.setOpenExternalLinks(True)
        copyright_label.setAlignment(Qt.AlignRight)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.browse_button)

        export_layout = QHBoxLayout()
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.confirm_button)

        layout.addWidget(self.export_dir_text_edit)
        layout.addWidget(self.combine_checkbox)
        layout.addLayout(export_layout)
        layout.addWidget(copyright_label)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.export_dir = ''

    def browseFiles(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter('JSON 文件 (*.json)')
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setOptions(options)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                self.text_edit.append(file)

    def selectExportDir(self):
        self.export_dir = QFileDialog.getExistingDirectory(self, '选择导出目录')
        self.export_dir_text_edit.setPlainText(self.export_dir)

    def show_overwrite_confirmation(self,same_name):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f'一个名为 "{same_name}" 的文件已经存在，你想要替换它吗？')
        msg.setWindowTitle("确认覆盖")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg.button(QMessageBox.Yes).setText("确认") 
        msg.button(QMessageBox.Cancel).setText("取消") 
        msg.setDefaultButton(QMessageBox.Cancel)
        return msg.exec_()

    def exportChat(self):
        try:
            input_files = self.text_edit.toPlainText().split('\n')
            input_files = [file.strip() for file in input_files if file.strip() != '']

            if not input_files:
                QMessageBox.warning(self, '未选择文件', '请选择至少一个 JSON 消息记录文件执行导出')
                return

            combine_files = self.combine_checkbox.isChecked()

            if not self.export_dir:
                QMessageBox.warning(self, '找不到目录', '请选择一个有效的导出目录')
                return

            if combine_files:
                combined_output_file = os.path.join(self.export_dir, 'Combined_Output.md')
                if os.path.exists(combined_output_file):
                    reply = self.show_overwrite_confirmation('Combined_Output')
                    if reply == QMessageBox.Cancel:
                        return

                with open(combined_output_file, 'w', encoding='utf-8') as md_file:
                    md_file.write("## Slack Message Combined Output\n\n")
                    for input_file in input_files:
                        base_name = os.path.splitext(os.path.basename(input_file))[0]
                        md_file.write(f'### {base_name}\n')
                        with open(input_file, 'r', encoding='utf-8') as json_file:
                            data = json.load(json_file)
                            for item in data:
                                if 'files' in item and item['files']:
                                    file_info = item['files'][0]
                                    md_file.write(f"\n> 文件: [{file_info['name']}]({file_info['url_private_download']})\n")
                                elif item['type'] == 'message' and 'text' in item:
                                    md_file.write(f"\n> {item['text']}\n")
                QMessageBox.information(self, '导出完成', '消息记录已成功导出')
                
            else:
                for input_file in input_files:
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    markdown_output_file = os.path.join(self.export_dir, f'{base_name}.md')

                    if os.path.exists(markdown_output_file):
                        reply = self.show_overwrite_confirmation(base_name)
                        if reply == QMessageBox.Cancel:
                            continue

                    with open(markdown_output_file, 'w', encoding='utf-8') as md_file:
                        md_file.write(f'### {base_name}\n')

                    with open(input_file, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)
                        with open(markdown_output_file, 'a', encoding='utf-8') as md_file:
                            for item in data:
                                if 'files' in item and item['files']:
                                    file_info = item['files'][0]
                                    md_file.write(f"\n> 文件: [{file_info['name']}]({file_info['url_private_download']})\n")
                                elif item['type'] == 'message' and 'text' in item:
                                    md_file.write(f"\n> {item['text']}\n")
                QMessageBox.information(self, '导出完成', '消息记录已成功导出')
        except Exception as err:
            QMessageBox.critical(self, '错误', f'出现了一个错误：{str(err)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatExtractorApp()
    window.show()
    sys.exit(app.exec_())