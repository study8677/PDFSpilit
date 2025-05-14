# PDF拆分工具

一个简单易用的PDF拆分工具，允许用户上传PDF文件并按需拆分。

## 功能特性

- 上传PDF文件（最大50MB）
- 多种拆分方式：
  - 将每页拆分为单独的PDF文件
  - 按自定义页面范围拆分（如1-3,5,7-10）
  - 按固定页数间隔拆分
- 拆分结果打包为ZIP文件下载

## 安装和运行

1. 克隆或下载此仓库

2. 安装依赖包：

```bash
pip install -r requirements.txt
```

3. 运行应用：

```bash
python app.py
```

4. 在浏览器中访问：http://127.0.0.1:5000

## 技术栈

- Python
- Flask (Web框架)
- PyPDF2 (PDF处理)
- Bootstrap 5 (前端UI)

## 项目结构

```
pdfSplit/
├── app.py                  # 主应用程序
├── requirements.txt        # 依赖列表
├── uploads/                # 上传文件临时存储
├── outputs/                # 输出文件临时存储
└── templates/              # HTML模板
    ├── index.html          # 首页
    └── split_options.html  # 拆分选项页面
```

## 注意事项

- 上传的文件和生成的拆分文件会在处理完成后自动删除
- 请确保上传的PDF文件没有加密或密码保护 