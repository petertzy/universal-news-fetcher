### 1. 创建 `requirements.txt`

根据你的项目使用的库，`requirements.txt` 文件应该包含以下内容：

```txt
fastapi==0.95.0
uvicorn==0.22.0
requests==2.28.2
beautifulsoup4==4.11.1
```

### 2. 安装依赖

假设你已经将 `requirements.txt` 文件创建并保存在项目根目录中，接下来可以按照以下步骤安装这些依赖：

1. **创建虚拟环境（可选）**：  
   虽然可以直接安装在全局环境中，但推荐使用虚拟环境来隔离项目依赖。在你的项目目录下打开终端并执行以下命令：

   - 创建虚拟环境（适用于 macOS/Linux）：

     ```bash
     python3 -m venv venv
     ```

     - 或者对于 Windows 用户：

     ```bash
     python -m venv venv
     ```

2. **激活虚拟环境**：

   - macOS/Linux：

     ```bash
     source venv/bin/activate
     ```

   - Windows：

     ```bash
     .\venv\Scripts\activate
     ```

   激活后，命令行提示符应该会发生变化，显示虚拟环境的名称。

3. **安装 `requirements.txt` 中的依赖**：

   在终端中运行以下命令，安装 `requirements.txt` 文件中列出的所有依赖：

   ```bash
   pip install -r requirements.txt
   ```

   这会自动下载并安装所有列出的包。

4. **验证安装**：

   安装完依赖后，你可以运行以下命令验证是否成功安装了这些依赖：

   ```bash
   pip freeze
   ```

   如果一切正常，你应该能看到类似以下的输出：

   ```txt
   fastapi==0.95.0
   requests==2.28.2
   uvicorn==0.22.0
   beautifulsoup4==4.11.1
   ```

### 3. 启动后端服务

依赖安装完成后，你就可以启动 FastAPI 后端服务了。继续执行以下命令启动后端服务：

```bash
uvicorn app:app --reload
```

此时，FastAPI 应该会在 `http://localhost:8000` 上运行，你可以在浏览器或 Postman 中访问你的后端 API。

### 总结

1. 创建一个 `requirements.txt` 文件，列出所有必要的包。
2. 使用虚拟环境（推荐）来隔离项目依赖。
3. 执行 `pip install -r requirements.txt` 来安装所有依赖。
4. 启动 FastAPI 后端服务：`uvicorn app:app --reload`。
