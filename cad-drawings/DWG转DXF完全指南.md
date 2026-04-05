# 柳林桥DWG→DXF转换指南

## 目标
将72张DWG图纸转换为DXF格式，使Web API能自动读取图纸内部尺寸。

---

## 方案A：Windows上转换（最简单，15分钟）

### 步骤1：下载安装ODA File Converter（3分钟）

1. 打开浏览器访问：
   ```
   https://www.opendesign.com/guestfiles/oda_file_converter
   ```

2. 点击 **"Download for Windows"**

3. 运行安装程序，一直点"下一步"即可

4. 记住安装路径（默认是 `C:\Program Files\ODA\ODAFileConverter`）

### 步骤2：运行批量转换脚本（10分钟）

1. 打开文件资源管理器，进入你的GitHub仓库文件夹：
   ```
   CAD/
   └── 柳林桥CAD图纸/
       ├── 主桥/
       ├── 智慧桥梁/
       └── ...
   ```

2. 把 `批量转换.bat` 放到 `CAD/` 文件夹下（和"柳林桥CAD图纸"同级）

3. **双击运行** `批量转换.bat`

4. 等待转换完成（72张图约5-10分钟）

5. 转换完成后会生成：
   ```
   CAD/
   ├── 柳林桥CAD图纸/     ← 原始DWG
   └── 柳林桥DXF图纸/     ← 新生成的DXF
       ├── 主桥/
       ├── 智慧桥梁/
       └── ...
   ```

### 步骤3：上传DXF到GitHub（2分钟）

```bash
cd CAD
git add 柳林桥DXF图纸/
git commit -m "Add DXF files for API dimension parsing"
git push
```

### 步骤4：服务器拉取更新（我帮你做）

完成！API立即具备尺寸识别能力。

---

## 方案B：Linux/Mac上转换

### 步骤1：下载ODA File Converter AppImage

```bash
# 访问网页下载 AppImage 版本
# https://www.opendesign.com/guestfiles/oda_file_converter
# 选择 Linux → AppImage

wget "https://download.opendesign.com/guestfiles/ODAFileConverter_lnxX64_8.3dll.AppImage"
chmod +x ODAFileConverter.AppImage
sudo mv ODAFileConverter.AppImage /usr/local/bin/
```

### 步骤2：运行转换脚本

```bash
cd /path/to/CAD
chmod +x 批量转换.sh
./批量转换.sh
```

---

## 方案C：分批转换（如果一次转不完）

如果72张太多，可以先转**最关键的20张**：

```bash
# 只转拱肋节段（Z1-Z10, C1-C5）
odafileconverter './柳林桥CAD图纸/主桥/1图纸' './柳林桥DXF图纸/主桥/1图纸' ACAD2018 DXF 0 1
```

优先级：
1. 拱肋节段构造图（Z1-Z10, C1-C5）- 最关键
2. 主梁节段构造图
3. 下部结构图
4. 其他

---

## 方案D：在线转换（无安装，适合少量）

如果不想安装软件，可以用在线工具：

1. 访问 https://anyconv.com/dwg-to-dxf-converter
2. 上传单张DWG
3. 下载DXF
4. 放到 `柳林桥DXF图纸/` 对应位置

⚠️ 缺点：需要一张张手动操作，72张会比较耗时

---

## 转换完成后验证

### 测试1：检查DXF文件
```bash
ls 柳林桥DXF图纸/主桥/1图纸/ | grep .dxf | wc -l
# 应该显示 50+ 个文件
```

### 测试2：API尺寸解析
```bash
curl http://localhost:8000/drawings/S2-1-2-5/dimensions

# 应该返回：
{
  "status": "parsed",
  "dimensions": {
    "summary": { "totalDimensionsExtracted": 45, ... },
    ...
  }
}
```

### 测试3：AI问答尺寸
```bash
curl "http://localhost:8000/ai/query?question=Z1节段尺寸多少？"

# 应该返回具体尺寸数值
```

---

## 常见问题

**Q: 转换后文件大小？**
A: DXF通常比DWG大2-5倍，72张图约200-500MB

**Q: 转换会丢失信息吗？**
A: 几何信息和尺寸标注完整保留，某些AutoCAD特有高级特性可能丢失，但对施工图纸完全够用

**Q: 可以只转部分图纸吗？**
A: 可以！API会优先找DXF，找不到就返回DWG元数据

**Q: 转换失败怎么办？**
A: 检查：1) 文件路径是否有中文 2) 磁盘空间是否充足 3) 文件是否损坏

---

## 转换脚本说明

### Windows脚本：批量转换.bat
- 双击运行
- 自动找 `柳林桥CAD图纸` 文件夹
- 输出到 `柳林桥DXF图纸` 文件夹
- 递归转换子文件夹

### Linux脚本：批量转换.sh
- `chmod +x` 后运行
- 自动检测ODA安装位置
- 提示安装指导（如果未安装）

---

## 下一步

转换完成并上传GitHub后，告诉我，我会：
1. 在服务器拉取更新
2. 重启API服务
3. 测试尺寸识别功能
4. 给你测试报告

**需要我做什么调整吗？**
