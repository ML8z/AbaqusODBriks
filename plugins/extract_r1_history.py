# -*- coding: utf-8 -*-
"""Abaqus plugin for extracting R1 history data across open ODB files."""

import csv
import os
import sys
import importlib.util


def _abaqus_modules_available():
    return (
        importlib.util.find_spec("abaqus") is not None
        and importlib.util.find_spec("abaqusGui") is not None
    )


if _abaqus_modules_available():
    from abaqus import session
    from abaqusGui import (
        AFXDataDialog,
        AFXForm,
        AFXMode,
        AFXStringKeyword,
        AFXTextField,
        FXGroupBox,
        FXHorizontalFrame,
        FXLabel,
        FXList,
        FXVerticalFrame,
        FRAME_GROOVE,
        FRAME_SUNKEN,
        FRAME_THICK,
        LAYOUT_FILL_X,
        LAYOUT_FILL_Y,
        LISTBOX_NORMAL,
        getAFXApp,
    )


def _is_r1_region(region_name):
    """Return True when *region_name* corresponds to the target set R1."""

    tokens = region_name.replace("/", " ").split()
    for token in tokens:
        if token.upper() == "R1":
            return True
    return False


def _safe_makedirs(path):
    if path and not os.path.exists(path):
        os.makedirs(path)


    class ExtractR1HistoryForm(AFXForm):
        """Plugin form that coordinates the dialog and extraction logic."""

        def __init__(self, owner):
            AFXForm.__init__(self, owner)

            if hasattr(session, "defaultSavePath"):
                default_dir = session.defaultSavePath
            else:
                default_dir = os.getcwd()
            default_path = os.path.join(default_dir, "r1_history.csv")

            self.output_path_kw = AFXStringKeyword(self, "output_path", True, default_path)

        def getFirstDialog(self):
            return ExtractR1HistoryDialog(self)

        def doOkAction(self):
            app = getAFXApp()
            message_area = app.getAFXMainWindow().writeToMessageArea

            odbs = self._get_open_odbs()
            if not odbs:
                message_area(u"未检测到已打开的 ODB 文件。请先打开一个 ODB。")
                return

            output_path = self.output_path_kw.getValue().strip()
            if not output_path:
                message_area(u"请提供有效的输出文件路径。")
                return

            try:
                rows = self._gather_history_rows(odbs)
                if len(rows) <= 1:
                    message_area(u"未找到包含 R1、LPF 和 U2 历程数据的步骤。")
                    return

                _safe_makedirs(os.path.dirname(output_path))

                if sys.version_info[0] < 3:
                    csv_file = open(output_path, "wb")
                else:
                    csv_file = open(output_path, "w", newline="")
                try:
                    writer = csv.writer(csv_file)
                    writer.writerows(rows)
                finally:
                    csv_file.close()

                message_area(u"已成功导出 R1 历程数据 → %s" % output_path)
            except Exception as err:  # pylint: disable=broad-except
                message_area(u"导出失败: %s" % err)
                raise

        def _get_open_odbs(self):
            try:
                return session.odbs
            except Exception:  # pylint: disable=broad-except
                return {}

        def _gather_history_rows(self, odbs):
            rows = [["ODB", "Step", "History Region", "Index", "FrameValue", "LPF", "U2"]]

            sorted_items = sorted(odbs.items())
            for odb_path, odb in sorted_items:
                odb_name = os.path.basename(odb_path)
                for step_name, step in odb.steps.items():
                    for region_name, region in step.historyRegions.items():
                        if not _is_r1_region(region_name):
                            continue

                        lpf_output = region.historyOutputs.get("LPF")
                        u2_output = region.historyOutputs.get("U2")
                        if lpf_output is None or u2_output is None:
                            continue

                        data_pairs = zip(lpf_output.data, u2_output.data)
                        index = 0
                        for lpf_point, u2_point in data_pairs:
                            frame_val, lpf_val = lpf_point
                            _, u2_val = u2_point
                            rows.append(
                                [
                                    odb_name,
                                    step_name,
                                    region_name,
                                    index,
                                    frame_val,
                                    lpf_val,
                                    u2_val,
                                ]
                            )
                            index += 1

            return rows


    class ExtractR1HistoryDialog(AFXDataDialog):
        """Dialog that shows open ODBs and lets the user configure the export."""

        def __init__(self, form):
            title = u"提取 R1 历程数据"
            AFXDataDialog.__init__(self, form, title, self.OK | self.CANCEL)

            self.form = form

            vf = FXVerticalFrame(
                self,
                FRAME_THICK | FRAME_SUNKEN | LAYOUT_FILL_X | LAYOUT_FILL_Y,
            )

            FXLabel(vf, u"当前已打开的 ODB：")
            self.odb_list = FXList(
                vf,
                opts=LISTBOX_NORMAL | FRAME_SUNKEN | FRAME_THICK | LAYOUT_FILL_X | LAYOUT_FILL_Y,
            )
            self._populate_odb_list()

            group_box = FXGroupBox(
                vf,
                u"输出设置",
                opts=FRAME_GROOVE | LAYOUT_FILL_X,
            )
            hf = FXHorizontalFrame(group_box, LAYOUT_FILL_X)
            FXLabel(hf, u"输出 CSV：")
            AFXTextField(hf, 40, form.output_path_kw, 0)

        def show(self):
            self._populate_odb_list()
            AFXDataDialog.show(self)

        def _populate_odb_list(self):
            self.odb_list.clearItems()
            odbs = self.form._get_open_odbs()
            odb_paths = sorted(odbs.keys())
            if odb_paths:
                for odb_path in odb_paths:
                    self.odb_list.appendItem(odb_path)
            else:
                self.odb_list.appendItem(u"<未检测到 ODB>")


    def register_plugin():
        app = getAFXApp()
        toolset = app.getAFXMainWindow().getPluginToolset()

        toolset.registerGuiMenuButton(
            buttonText=u"提取 R1 历程数据...",
            object=ExtractR1HistoryForm(toolset),
            messageId=AFXMode.ID_CLICK,
            icon=None,
            kernelInitString="import extract_r1_history",
            applicableModules=("Visualization",),
            author="AbaqusODBriks",
            description=(
                u"提取所有已打开 ODB 文件中集合 R1 的 LPF 与 U2 历程数据，并输出为单个 CSV 文件。"
            ),
        )


    register_plugin()
else:
    def register_plugin():
        raise RuntimeError(u"该插件只能在 Abaqus/CAE GUI 中使用。")

    if __name__ == "__main__":
        sys.stderr.write(u"该插件只能在 Abaqus/CAE GUI 中使用。\n")
