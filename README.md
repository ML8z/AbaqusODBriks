# Abaqus ODB R1 历程提取插件

该仓库包含一个适用于 Abaqus/CAE 2022 的插件脚本，用于批量提取已打开 ODB 文件中集合 `R1` 的 LPF 与 U2 历程数据。

## 安装

1. 将 `plugins/extract_r1_history.py` 复制到 Abaqus 插件目录（例如 `CAE/plugins`）或其它可被 Abaqus 插件搜索路径访问的位置。
2. 该脚本依赖 Abaqus/CAE 的 GUI 环境，仅能在 Abaqus/CAE 中加载与运行；使用系统 Python 直接执行会提示错误信息。
3. 重新启动 Abaqus/CAE，或在插件管理器中加载该脚本。

## 使用方法

1. 在 Abaqus/CAE 中打开一个或多个包含 `R1` 几何集，并且该集合已经定义了 LPF 与 U2 历程输出的 ODB 文件。
2. 在 Visualization 模块中，通过菜单 **Plug-ins → AbaqusODBriks → 提取 R1 历程数据...** 启动插件。
3. 弹出的对话框会列出当前已打开的所有 ODB 文件，并提供一个文本框让你指定导出 CSV 文件的路径（默认位于 Abaqus 的默认保存目录）。
4. 点击 **OK** 之后，插件会遍历每个 ODB，检索所有包含 `R1` 集合且同时包含 `LPF` 与 `U2` 历程输出的步骤，将其组合为单个 CSV 文件。

导出的 CSV 文件包含以下列：

| 列名 | 含义 |
| ---- | ---- |
| `ODB` | ODB 文件名 |
| `Step` | 历程所在的步骤名称 |
| `History Region` | 匹配的历程输出区域名称 |
| `Index` | 历程点在对应区域内的序号 |
| `FrameValue` | 历程点的时间/步长/弧长标量值 |
| `LPF` | 对应点的弧长法 Load Proportionality Factor 值 |
| `U2` | 对应点的 U2 位移值 |

如果未检测到任何符合条件的历程数据，插件会在消息区提示相关信息。
