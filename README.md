# 全场景爬虫工具 v1.0

一个功能强大的可视化爬虫工具，支持静态页面、动态页面和API爬取。

## 功能特性

### 核心功能
- **多种爬虫类型支持**：
  - 静态页面爬虫（基于requests）
  - 动态页面爬虫（基于Selenium）
  - API接口爬虫（REST API）

- **灵活的数据解析**：
  - CSS选择器
  - XPath选择器
  - 正则表达式
  - JSON路径提取

- **多种存储方式**：
  - CSV文件
  - JSON文件
  - SQLite数据库
  - MySQL数据库

### 高级功能
- **代理支持**：支持HTTP/HTTPS代理，可配置代理池轮换
- **登录会话管理**：自动处理登录，保存cookies
- **任务调度**：支持定时执行和周期执行
- **数据预览**：可视化查看爬取结果
- **导入/导出**：支持任务配置的导入和导出

## 快速开始

### 方式一：直接运行（推荐）

1. 双击 `start.bat` 启动程序
2. 首次运行会自动：
   - 创建虚拟环境
   - 安装所需依赖
   - 启动程序

### 方式二：打包成EXE

1. 双击 `build.bat` 运行打包脚本
2. 等待打包完成（约5-10分钟）
3. 打包结果在 `dist\全场景爬虫工具\` 目录
4. 双击 `启动爬虫工具.bat` 或 `全场景爬虫工具.exe` 运行

### 方式三：手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 运行程序
python main.py
```

## 使用说明

### 创建爬虫任务

1. 点击"新建任务"按钮
2. 填写任务名称和描述
3. 选择爬虫类型（静态/动态/API）
4. 配置起始URL和解析规则
5. 选择存储方式
6. 点击"保存"

### 配置解析规则

在"解析规则"选项卡中：
| 字段 | 说明 |
|------|------|
| 字段名称 | 数据字段的名称 |
| 选择器 | CSS选择器、XPath或正则表达式 |
| 选择器类型 | css/xpath/regex |
| 属性 | 要提取的属性（text/href/src等） |
| 默认值 | 未匹配时的默认值 |
| 后处理 | strip/lower/upper/int/float等 |

### 运行任务

1. 在任务列表中选择任务
2. 点击"运行"按钮
3. 在"运行日志"选项卡查看进度
4. 完成后在"数据预览"选项卡查看结果

### 导出数据

1. 在"数据预览"选项卡查看结果
2. 点击"导出CSV"或"导出JSON"保存数据

## 配置说明

### 存储配置

| 类型 | 说明 | 示例路径 |
|------|------|----------|
| CSV | 导出为CSV文件 | data/output/result.csv |
| JSON | 导出为JSON文件 | data/output/result.json |
| SQLite | 存储到SQLite数据库 | data/spider.db |
| MySQL | 存储到MySQL数据库 | mysql://user:pass@host/db |

### 代理配置

在"代理配置"选项卡中：
- 启用代理：勾选启用
- HTTP代理：`http://proxy:port`
- HTTPS代理：`https://proxy:port`
- 代理列表：每行一个代理地址，用于轮换

### 登录配置

在"登录配置"选项卡中：
- 登录URL：登录页面地址
- 用户名/密码：登录凭据
- 字段名：表单中用户名和密码的name属性

## 项目结构

```
全场景爬虫/
├── main.py                 # 程序入口
├── start.bat               # 自动安装启动脚本
├── build.bat               # 打包脚本
├── build.py                # PyInstaller打包程序
├── spider_tool.spec        # PyInstaller配置文件
├── requirements.txt        # 依赖列表
├── README.md               # 说明文档
├── src/                    # 源代码
│   ├── core/              # 核心引擎
│   │   ├── engine.py      # 爬虫引擎
│   │   └── spiders/       # 爬虫实现
│   │       ├── base.py        # 基础爬虫
│   │       ├── static_spider.py   # 静态爬虫
│   │       ├── dynamic_spider.py  # 动态爬虫
│   │       └── api_spider.py      # API爬虫
│   ├── storage/           # 存储模块
│   │   ├── csv_storage.py
│   │   ├── json_storage.py
│   │   ├── sqlite_storage.py
│   │   └── mysql_storage.py
│   ├── gui/               # 图形界面
│   │   ├── main_window.py # 主窗口
│   │   ├── widgets/       # 小部件
│   │   └── dialogs/       # 对话框
│   └── models/            # 数据模型
│       ├── task.py        # 任务模型
│       └── result.py      # 结果模型
├── data/                  # 数据目录
│   ├── tasks/             # 任务配置
│   └── output/            # 输出文件
├── config/                # 配置文件
└── assets/                # 资源文件
```

## 常见问题

### Q: 启动时报错"未检测到Python"？
A: 请先安装Python 3.8+，下载地址：https://www.python.org/downloads/

### Q: 依赖安装失败？
A: 尝试以下方法：
1. 检查网络连接
2. 使用管理员权限运行
3. 手动安装：`pip install -r requirements.txt`

### Q: 动态页面爬虫无法运行？
A: 需要安装Chrome或Firefox浏览器，并下载对应的WebDriver。

### Q: 打包后程序无法运行？
A: 确保打包时没有报错，检查`dist\全场景爬虫工具\`目录下的文件是否完整。

### Q: 如何使用代理？
A: 在任务配置的"代理配置"选项卡中启用代理，填入代理地址。

### Q: 如何处理需要登录的网站？
A: 在"登录配置"选项卡中填入登录URL、用户名和密码。

## 系统要求

- Windows 10/11 (64位)
- Python 3.8+
- 2GB+ 内存
- 500MB+ 磁盘空间

## 许可证

MIT License

## 更新日志

### v1.0.0 (2026-05-02)
- 初始版本发布
- 支持静态页面、动态页面、API爬取
- 支持CSV、JSON、SQLite、MySQL存储
- 可视化任务管理界面
- 代理支持和登录会话管理