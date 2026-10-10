# 文档扫描器

一个用 OpenCV 写的文档扫描小项目。输入一张纸张照片，自动找出四个角，做透视校正，再生成黑白扫描图。也可以手动指定角点。

## 效果

下面的图片由 `make_demo.py` 生成，用来检查处理流程。实拍照片的效果还需要另行测试。

| 原图 | 边框检测 |
| --- | --- |
| ![原图](examples/document.jpg) | ![边框](examples/result/detected.jpg) |

| 透视校正 | 黑白扫描 |
| --- | --- |
| ![校正](examples/result/rectified.jpg) | ![扫描](examples/result/scan.png) |

## 运行

需要 Python、OpenCV 和 NumPy。开发时使用 Python 3.12.10、OpenCV 5.0.0、NumPy 2.5.3。

在项目目录下执行：

```bash
python -m pip install -r requirements.txt
python scanner.py examples/document.jpg
```

处理自己的照片：

```bash
python scanner.py "文档.jpg" --output outputs/my-document
```

输出目录里有检测边框图 `detected.jpg`、校正图 `rectified.jpg`、黑白图 `scan.png` 和角点信息 `metadata.json`。自动检测还会保存 `edges.png`，这张边缘图可能经过缩小。同一个输出目录重复运行会覆盖同名文件。

如果没有识别到纸张，可以输入原图中的四个角点坐标：

```bash
python scanner.py examples/document.jpg --corners 210 110 680 180 760 850 120 790 --output outputs/manual
```

每两个数字是一组 x、y 坐标，原点在左上角，x 向右，y 向下。四个点的输入顺序不限，但必须构成凸四边形。

## 实现思路

先把检测图像的最长边缩到不超过 1000 像素，转成灰度图并做高斯滤波。接着用 Canny 提取边缘，再用闭运算连接部分断开的边缘。

轮廓按面积从大到小检查，选择面积占图像至少 15% 的凸四边形。找到四个角后，把坐标还原到原图尺寸，用透视变换把纸张拉正。最后做自适应阈值处理，得到黑白图。

主要参数都在 `scanner.py` 里：Canny 阈值为 50 和 150，闭运算核为 5×5，轮廓近似精度为周长的 2%，自适应阈值窗口为 21、常数为 10。

## 文件

```text
scanner.py          扫描算法和命令行入口
make_demo.py        生成示例图片
test_scanner.py     测试
examples/           示例图片、角点坐标和处理结果
docs/REPORT.md      实现和测试记录
requirements.txt    依赖
```

重新生成示例、运行测试：

```bash
python make_demo.py
python -m unittest -v
```

目前 4 项测试通过，检查了合成图角点误差、角点排序以及异常输入。具体检查内容见 [测试记录](docs/REPORT.md)。

## 目前的问题

程序按面积选择四边形，复杂背景下可能把桌面边框认成纸张。纸张和背景颜色接近、边缘被遮住或阴影太重时，也可能检测失败。透视变换只能处理平面文档，弯曲的书页无法直接校正。

目前只有合成示例，还没有统计实拍成功率。后续可以先补充不同背景和光照下的照片，再考虑加入四角拖动修正界面。
