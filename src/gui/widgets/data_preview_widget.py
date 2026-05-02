"""
数据预览小部件
"""
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFileDialog, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt

from ...models.result import TaskResult


class DataPreviewWidget(QWidget):
    """数据预览小部件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result: Optional[TaskResult] = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 信息区域
        info_layout = QHBoxLayout()
        
        self.task_id_label = QLabel("任务ID: -")
        info_layout.addWidget(self.task_id_label)
        
        self.item_count_label = QLabel("数据条数: 0")
        info_layout.addWidget(self.item_count_label)
        
        info_layout.addStretch()
        
        # 按钮区域
        export_csv_btn = QPushButton("导出CSV")
        export_csv_btn.clicked.connect(self._export_csv)
        info_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("导出JSON")
        export_json_btn.clicked.connect(self._export_json)
        info_layout.addWidget(export_json_btn)
        
        layout.addLayout(info_layout)
        
        # 数据表格
        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.data_table)
    
    def set_result(self, result: TaskResult):
        """设置结果数据"""
        self.result = result
        self._refresh_table()
    
    def _refresh_table(self):
        """刷新表格"""
        if not self.result or not self.result.items:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.task_id_label.setText("任务ID: -")
            self.item_count_label.setText("数据条数: 0")
            return
        
        # 更新标签
        self.task_id_label.setText(f"任务ID: {self.result.task_id}")
        self.item_count_label.setText(f"数据条数: {len(self.result.items)}")
        
        # 获取所有字段名
        fieldnames = set()
        for item in self.result.items:
            fieldnames.update(item.data.keys())
        
        # 添加元数据列
        columns = ["_url", "_scraped_at"] + sorted(fieldnames)
        
        # 设置表格
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        self.data_table.setRowCount(len(self.result.items))
        
        # 填充数据
        for row, item in enumerate(self.result.items):
            # URL列
            self.data_table.setItem(row, 0, QTableWidgetItem(item.url))
            
            # 爬取时间列
            scraped_at = item.scraped_at.strftime("%Y-%m-%d %H:%M:%S") if item.scraped_at else ""
            self.data_table.setItem(row, 1, QTableWidgetItem(scraped_at))
            
            # 数据列
            for col, field in enumerate(sorted(fieldnames), start=2):
                value = item.data.get(field, "")
                if isinstance(value, (dict, list)):
                    import json
                    value = json.dumps(value, ensure_ascii=False)
                self.data_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        # 调整列宽
        self.data_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
    
    def _export_csv(self):
        """导出CSV"""
        if not self.result or not self.result.items:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出CSV", "spider_data.csv", "CSV文件 (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                import json
                
                # 获取所有字段名
                fieldnames = set()
                for item in self.result.items:
                    fieldnames.update(item.data.keys())
                
                columns = ["_url", "_scraped_at"] + sorted(fieldnames)
                
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    
                    for item in self.result.items:
                        row = {
                            "_url": item.url,
                            "_scraped_at": item.scraped_at.isoformat() if item.scraped_at else "",
                        }
                        for field in sorted(fieldnames):
                            value = item.data.get(field, "")
                            if isinstance(value, (dict, list)):
                                value = json.dumps(value, ensure_ascii=False)
                            row[field] = value
                        writer.writerow(row)
                
                QMessageBox.information(self, "成功", f"数据已导出到: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _export_json(self):
        """导出JSON"""
        if not self.result or not self.result.items:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出JSON", "spider_data.json", "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                import json
                
                data = self.result.to_dict()
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "成功", f"数据已导出到: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")