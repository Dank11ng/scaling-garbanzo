# 手写数字识别

用 scikit-learn 自带的手写数字数据训练一个 SVM 模型，识别 0 到 9。项目包括训练、保存模型、测试集评估，以及一个可以用鼠标写数字的小画板。

## 运行

需要 Python 3.10 或更新版本。在项目目录执行：

```bash
python -m pip install -r requirements.txt
python digits.py train
python draw.py
```

训练完成后会生成 `model.joblib` 和 `metrics.json`。仓库里也保留了本次训练得到的文件，可以直接运行 `python draw.py`。画板上写一个数字，点 **Recognize** 查看预测结果，点 **Clear** 清空。

也可以识别一张只有单个数字的图片：

```bash
python digits.py predict my-digit.png
```

图片应有明显的数字和干净背景。黑底白字、白底黑字都可以；程序会截取数字区域并缩放到模型需要的 8×8 格式。手写图片与训练数据的风格可能不同，预测错误时可以先试着把数字写大一些、居中一些。

## 模型怎么训练

数据来自 `sklearn.datasets.load_digits`，共 1797 张 8×8 灰度数字图。按数字类别分层，固定随机种子 42，80% 用于训练，20% 用于测试。为了适应画板输入，训练集中每张图还会生成一个经过画板预处理流程的版本；测试集不参与训练。像素先经过 `StandardScaler`，然后训练 RBF 核的 `SVC`。参数为 `C=10`、`gamma="scale"`。

这次运行的原始测试图准确率为 97.22%，经过画板预处理的测试图准确率为 98.89%，详细结果见 [metrics.json](metrics.json)。这些数字只反映内置数据集上的表现，不能当作真实鼠标手写或手机照片的准确率。训练和测试脚本在 [digits.py](digits.py)，更多记录见 [docs/REPORT.md](docs/REPORT.md)。

```bash
python -m unittest -v
```

`joblib` 模型文件只能从可信来源加载；想重新训练可以删除本地模型后运行 `python digits.py train`。
