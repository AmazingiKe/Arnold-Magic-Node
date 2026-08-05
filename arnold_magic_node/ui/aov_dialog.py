"""AOV 灯光组管理窗口。"""

from contextlib import contextmanager
import os

import maya.cmds as cmds
import mtoa.aovs as aovs

from ..application import (
    SoftwareState,
    SoftwareVersion,
    aov_cache_path,
    icon_path,
)
from ..arnold_magic_core import DataManager, FeedbackPrompt, GetNodeData
from .qt import QtCore, QtGui, QtWidgets
from .workspace import delete_window_if_existe, get_maya_main_window


@contextmanager
def block_updates_and_signals(widget):
    widget.setUpdatesEnabled(False)
    widget.blockSignals(True)
    try:
        yield
    finally:
        widget.blockSignals(False)
        widget.setUpdatesEnabled(True)
        widget.viewport().update()

class AOVLightGroupTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(AOVLightGroupTreeWidget, self).__init__(parent)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
        self.setUniformRowHeights(True)
        self.itemClicked.connect(self.enable_drag_drop_flags)

    def enable_drag_drop_flags(self, item):
        if item.parent() is None:
            flags = item.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable
        else:
            flags = item.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable
            flags &= ~QtCore.Qt.ItemIsDropEnabled
        item.setFlags(flags)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction("添加父级")
        add_action.triggered.connect(self.add_parent)

        selected = self.selectedItems()
        delete_action = menu.addAction("删除父级")
        if len(selected) == 1 and selected[0].parent() is None:
            delete_action.triggered.connect(lambda: self.delete_parent(selected[0]))
            delete_action.setEnabled(True)
        else:
            delete_action.setEnabled(False)
        menu.exec_(event.globalPos())

    def add_parent(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return

        new_parent = QtWidgets.QTreeWidgetItem()
        new_parent.setText(0, "new_light_group")
        new_parent.setFlags(new_parent.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable)
        self.addTopLevelItem(new_parent)

        new_parent.setIcon(0, QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png')))

        with block_updates_and_signals(self):
            sorted_items = sorted(selected_items, key=self.get_item_index, reverse=True)
            for item in sorted_items:
                # 仅移动子级项，跳过父级项
                if item.parent() is None:
                    continue
                old_parent = item.parent()
                old_parent.removeChild(item)
                new_parent.addChild(item)
        new_parent.setExpanded(True)

    def delete_parent(self, parent_item):
        if parent_item.parent() is not None:
            return

        children = []
        while parent_item.childCount() > 0:
            child = parent_item.takeChild(0)
            children.append(child)

        with block_updates_and_signals(self):
            for child in children:
                self.addTopLevelItem(child)
            index = self.indexOfTopLevelItem(parent_item)
            if index != -1:
                self.takeTopLevelItem(index)

    def get_item_index(self, item):
        parent = item.parent()
        return parent.indexOfChild(item) if parent else self.indexOfTopLevelItem(item)

    def _is_ancestor(self, item, target):
        parent = target.parent() if target else None
        while parent:
            if parent == item:
                return True
            parent = parent.parent()
        return False

    # 合并两个validate_drop方法为一个更完善的版本
    def validate_drop(self, target, items, drop_indicator_pos):
        """
        验证拖放操作是否符合以下规则：
        1. 禁止拖拽到自身或祖先
        2. 若拖放到某项（OnItem），则只允许拖到顶级项
        3. 若拖放到项上方/下方，新位置的父项必须为顶级项
        4. 父级项不能拖放到子级项内部或成为子级项
        """
        # 禁止拖拽到自身或祖先
        for item in items:
            if self._is_ancestor(item, target):
                return False

        # 处理 OnItem 放置
        if drop_indicator_pos == QtWidgets.QAbstractItemView.OnItem:
            # 仅允许拖放到顶级父级
            if target and self.get_item_depth(target) >= 1:
                return False

        # 处理 Above/Below 放置
        elif drop_indicator_pos in (QtWidgets.QAbstractItemView.AboveItem, QtWidgets.QAbstractItemView.BelowItem):
            # 如果目标存在且是子级，检查其父级是否允许放置
            if target and target.parent() is not None:
                parent = target.parent()
                # 确保父级是顶级项
                if parent.parent() is not None:
                    return False

        # 检查被拖动的父级项是否被非法放置
        for item in items:
            if item.parent() is None:  # 父级项
                # 禁止将父级拖放到其他项内部
                if drop_indicator_pos == QtWidgets.QAbstractItemView.OnItem:
                    return False
                # 禁止将父级拖放到子级附近（会成为子级）
                if target and target.parent() is not None:
                    return False

        return True

    def dropEvent(self, event):
        # 在原有基础上增加更新逻辑
        expanded_state = self._get_expanded_state()
        super(AOVLightGroupTreeWidget, self).dropEvent(event)

        # 获取被移动的项及其新父级
        moved_items = self.selectedItems()
        new_parent = self.itemAt(event.pos())

        with block_updates_and_signals(self):
            for item in moved_items:
                # 如果移动到新的父级下
                if new_parent and new_parent.parent() is None:
                    self.update_light_group(item, new_parent.text(0))
                # 如果移动到顶层
                elif new_parent is None:
                    self.update_light_group(item, "")

        self._restore_expanded_state(expanded_state)

        # 在enable_drag_drop_flags中确保父级可编辑

    def _get_expanded_state(self):
        state = {}
        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            state[id(item)] = item.isExpanded()
            iterator += 1
        return state

    def _restore_expanded_state(self, state):
        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            item.setExpanded(state.get(id(item), False))
            iterator += 1

    def startDrag(self, supported_actions):
        """
        开始拖动操作，构造 QDrag 对象，
        并使用选中项的 MIME 数据启动拖动。
        """
        drag = QtGui.QDrag(self)
        mime_data = self.model().mimeData(self.selectedIndexes())
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.MoveAction)


    def get_item_depth(self, item):
        """
        计算项在树中的深度，根节点深度为 0。
        遍历项的父链，计数每一级父项。
        """
        depth = 0
        parent = item.parent()
        while parent:
            depth += 1
            parent = parent.parent()
        return depth

class AOVLightGroupManager(QtWidgets.QDialog):

    def __init__(self, parent = get_maya_main_window()):

        super(AOVLightGroupManager, self).__init__(parent)

        # 创建实例类
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData()  # 提取数据模块
        self.dataM = DataManager()  # 储存模块


        self.WINDOWS_NAME = f"AOV灯光组管理器  {SoftwareState} : {SoftwareVersion}"


        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('AOVLightGroupManager')

        self.setObjectName('AOVLightGroupManager')
        self.setWindowTitle(self.WINDOWS_NAME)

        # ...窗口长宽
        self.setMinimumSize(1200, 800)  # 设置一个比较小的最小尺寸
        self.setWindowIcon(QtGui.QIcon(icon_path + "\\LightManagerShelf_200.png"))

        # 窗口标志（隐藏放大/缩小按钮）
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        # 初始化数据
        self._initial_settings()
        self._create_widgets()
        self._create_menu()
        self._create_layouts()

    def _initial_settings(self):
        # 缓存文件
        cache = ["RGBA"]

        self.cache_path = aov_cache_path

        # 如果缓存文件不存在则创建
        if not os.path.exists(self.cache_path):
            self.dataM.save_json(self.cache_path, cache)

    def _create_widgets(self):
        # 刷新按钮
        self.refresh_light_group_tree_button = QtWidgets.QPushButton()
        self.refresh_light_group_tree_button.setIcon(QtGui.QIcon(os.path.join(icon_path, "ResetMode_200.png")))
        self.refresh_light_group_tree_button.setFixedHeight(40)
        self.refresh_light_group_tree_button.setFixedWidth(40)
        self.refresh_light_group_tree_button.setIconSize(QtCore.QSize(32, 32))
        self.refresh_light_group_tree_button.clicked.connect(lambda *args : self._refresh_light_group_tree(icon_path))

        # 选择场景中的灯光
        self.select_lights_button = QtWidgets.QPushButton()
        self.select_lights_button.setIcon(QtGui.QIcon(os.path.join(icon_path, "aiAreaLight.svg")))
        self.select_lights_button.setFixedHeight(40)
        self.select_lights_button.setFixedWidth(40)
        self.select_lights_button.setIconSize(QtCore.QSize(32, 32))
        self.select_lights_button.clicked.connect(lambda *args: self._get_selected_lights_in_group())
        # 灯光搜索框
        self.light_group_search_input = QtWidgets.QLineEdit()
        self.light_group_search_input.setFixedWidth(480)
        self.light_group_search_input.setFixedHeight(40)

        # 添加搜索框文本变化信号连接
        self.light_group_search_input.textChanged.connect(lambda *args :self._filter_light_group_tree())


        # 使用QtreeWidget控件创建一个类似Maya的节点树
        self.light_group_tree_widget = AOVLightGroupTreeWidget(self)
        self.light_group_tree_widget.setHeaderLabels(['AOV灯光组'])

        # 设置灯光树的大小
        self.light_group_tree_widget.setFixedWidth(600)
        # self.light_group_tree_widget.setFixedHeight(700)

        # 刷新灯光组树
        self._refresh_light_group_tree(icon_path)

        # 节点树连接的函数
        self.light_group_tree_widget.itemChanged.connect(
            lambda *args:(
                self.update_light_group_data(),
                self._select_lights()))

        # 节点树的缩放滑轨
        self.light_group_tree_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.light_group_tree_slider.setFixedWidth(600)
        # 获取默认大小
        light_group_tree_slider_font = self.light_group_tree_widget.font().pixelSize()
        # 计算出默认值的的最小一倍和最大一倍
        self.light_group_tree_slider.setMinimum(1)
        self.light_group_tree_slider.setMaximum(light_group_tree_slider_font + light_group_tree_slider_font)
        # 并设置成材质列表的默认大小到滑杆上
        self.light_group_tree_slider.setValue(light_group_tree_slider_font - 8)
        # 滑杆绑定函数
        self.light_group_tree_slider.valueChanged.connect(lambda *args: self.handle_zoom_change())

        AOV_list = ['RGBA', 'coat', 'coat_direct', 'coat_indirect', 'diffuse', 'diffuse_direct', 'diffuse_indirect',
         'direct', 'indirect', 'sheen', 'sheen_albedo', 'sheen_direct', 'sheen_indirect', 'specular', 'specular_albedo',
         'specular_direct', 'specular_indirect', 'sss', 'sss_albedo',
         'sss_direct', 'sss_indirect', 'transmission', 'transmission_albedo', 'transmission_direct',
         'transmission_indirect', 'volume', 'volume_Z', 'volume_albedo', 'volume_direct',
         'volume_indirect', 'volume_opacity']

        # AOV选择列表
        self.aov_select_list_widget = QtWidgets.QListWidget(self)

        # 把aov列表加入到aov列表控件中
        self.aov_select_list_widget.addItems(AOV_list)

        self.aov_select_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.aov_select_list_widget.setFixedWidth(600)

        self.aov_select_list_widget.currentItemChanged.connect(lambda *args: self._modify_aov_select_list_cache())
        # 设置初始选中项
        self._select_aov_select_list_texts(self.dataM.load_json(self.cache_path))


        # 功能按钮
        self.every_cerate_aov_group_button = QtWidgets.QPushButton("创建所有AOV灯光组")
        self.every_cerate_aov_group_button.clicked.connect(lambda *args:(self._create_parent_for_child_items()))
        self.clear_all_lighet_group_button = QtWidgets.QPushButton("清除所有灯光组")
        self.clear_all_lighet_group_button.clicked.connect(lambda *args: self._clear_all_light_groups())
        self.clear_aov_button = QtWidgets.QPushButton("清除AOV中的灯光组")

        self.clear_aov_button.clicked.connect(lambda *args: self._clear_custom_aovs())
        self.create_aov_button = QtWidgets.QPushButton("创建AOV灯光组")
        self.create_aov_button.clicked.connect(lambda *args: self._create_aov_light_group())

    def _create_menu(self):
        pass

    def _create_layouts(self):
        Main_Layout = QtWidgets.QHBoxLayout()




        # 灯光组树布局
        light_group_tree_layout = QtWidgets.QVBoxLayout()
        light_group_tree_function_layout = QtWidgets.QHBoxLayout()
        light_group_tree_function_layout.addWidget(self.refresh_light_group_tree_button)
        light_group_tree_function_layout.addWidget(self.select_lights_button)
        light_group_tree_function_layout.addWidget(self.light_group_search_input)
        light_group_tree_layout.addLayout(light_group_tree_function_layout)
        light_group_tree_layout.addWidget(self.light_group_tree_slider)
        light_group_tree_layout.addWidget(self.light_group_tree_widget)


        aov_select_list_layout = QtWidgets.QVBoxLayout()


        aov_select_list_button_layout_01 = QtWidgets.QHBoxLayout()
        aov_select_list_layout.addLayout(aov_select_list_button_layout_01)
        aov_select_list_button_layout_01.addWidget(self.every_cerate_aov_group_button)
        aov_select_list_button_layout_01.addWidget(self.clear_all_lighet_group_button)

        aov_select_list_layout_02 = QtWidgets.QHBoxLayout()
        aov_select_list_layout.addLayout(aov_select_list_layout_02)
        aov_select_list_layout_02.addWidget(self.aov_select_list_widget)

        aov_select_list_button_layout_03 = QtWidgets.QVBoxLayout()
        aov_select_list_layout.addLayout(aov_select_list_button_layout_03)
        aov_select_list_button_layout_03.addWidget(self.clear_aov_button)
        aov_select_list_button_layout_03.addWidget(self.create_aov_button)

        Main_Layout.addLayout(light_group_tree_layout)
        Main_Layout.addLayout(aov_select_list_layout)

        self.setLayout(Main_Layout)

    # 刷新灯光组树的内容
    def _refresh_light_group_tree(self, icon_path=None):
        """按AOV灯光组结构刷新树控件"""

        # 获取场景中的阿诺德灯光
        lights_and_type = self.getnodedata.get_scene_arnold_lights_and_type()
        light_groups = self.getnodedata.get_light_group(lights_and_type)

        # 清空当前 QTreeWidget 内容
        self.light_group_tree_widget.clear()

        # 图标路径字典 (可以替换为实际的图标路径)
        icon_paths = {
            'aiAreaLight': os.path.join(icon_path, 'aiAreaLight.svg'),
            'aiSkyDomeLight': os.path.join(icon_path, 'aiSkyDomeLight.svg'),
            'aiPhotometricLight': os.path.join(icon_path, 'aiPhotometricLight.svg'),
            'aiMeshLight': os.path.join(icon_path, 'aiMeshLight.svg'),
            'aiLightPortal': os.path.join(icon_path, 'aiLightPortal.svg'),
            'directionalLight' :  os.path.join(icon_path, 'directionalLight'),
            'spotLight' :  os.path.join(icon_path, 'spotLight'),
            'areaLight' :  os.path.join(icon_path, 'areaLight'),
            'pointLight': os.path.join(icon_path, 'pointLight'),
            'default': os.path.join(icon_path, 'aiAreaLight.svg')  # 如果找不到对应的图标就用这个
        }

        # 父级节点的通用图标
        parent_icon = QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png'))

        # 创建树形结构
        for light_group, lights in light_groups.items():


            parent_item = QtWidgets.QTreeWidgetItem(self.light_group_tree_widget, [light_group])
            parent_item.setIcon(0, parent_icon)  # 设置父级节点图标
            parent_item.setFlags(
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsDropEnabled
            )

            # 添加子节点
            for light in lights:
                child_item = QtWidgets.QTreeWidgetItem(parent_item, [light])
                child_item.setFlags(
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable |
                    QtCore.Qt.ItemIsDragEnabled
                )

                # 设置子节点的图标
                light_type = lights_and_type[light]
                icon_path = icon_paths.get(light_type, icon_paths['default'])
                child_item.setIcon(0, QtGui.QIcon(icon_path))

        self.light_group_tree_widget.expandAll()

    # aov搜索框函数
    def _filter_light_group_tree(self):
        """根据搜索框内容过滤灯光组树"""
        keyword = self.light_group_search_input.text().lower().strip()

        # 遍历所有顶级项（父级灯光组）
        for i in range(self.light_group_tree_widget.topLevelItemCount()):
            parent_item = self.light_group_tree_widget.topLevelItem(i)
            parent_matched = keyword in parent_item.text(0).lower()
            any_child_matched = False

            # 遍历子级灯光项
            for j in range(parent_item.childCount()):
                child_item = parent_item.child(j)
                child_matched = keyword in child_item.text(0).lower()
                child_item.setHidden(not child_matched)

                if child_matched:
                    any_child_matched = True

            # 设置父级可见性：父级匹配或任意子级匹配时显示
            parent_visible = parent_matched or any_child_matched
            parent_item.setHidden(not parent_visible)

            # 自动展开匹配的父级
            if parent_visible:
                parent_item.setExpanded(True)

        # 处理空关键字情况
        if not keyword:
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                parent_item = self.light_group_tree_widget.topLevelItem(i)
                parent_item.setHidden(False)
                parent_item.setExpanded(True)  # 恢复默认展开状态
                for j in range(parent_item.childCount()):
                    parent_item.child(j).setHidden(False)

    #  获取灯光组树控件有什么内容
    def _get_all_items(self):
        def traverse_items(item):
            data = {
                "text": item.text(0),  # 获取第0列的文本
                "children": []
            }
            for i in range(item.childCount()):
                child_item = item.child(i)
                data["children"].append(traverse_items(child_item))
            return data

        root_data = []
        for i in range(self.light_group_tree_widget.topLevelItemCount()):
            root_item = self.light_group_tree_widget.topLevelItem(i)
            root_data.append(traverse_items(root_item))

        return root_data

    # 更新场景灯光的组
    def update_light_group_data(self,):
        """更新灯光组数据，根据当前树状结构同步到 Maya 灯光节点。"""

        # 获取灯光组树的数据
        items = self._get_all_items()

        # 对灯光组进行更新
        for item in items:
            if item['children']:  # 父级节点存在子节点
                current_light_group = item['text']  # 当前灯光组的名称

                for light_child_item in item['children']:
                    light_name = light_child_item['text']  # 灯光名称
                    try:
                        old_light_group = cmds.getAttr(f"{light_name}.aiAov")  # 获取旧灯光组

                        if current_light_group != old_light_group:
                            if isinstance(current_light_group, str):
                                cmds.setAttr(f"{light_name}.aiAov", current_light_group, type="string")
                            else:
                                self.feedback.CPW(f"灯光组名称必须为字符串，当前为：{type(current_light_group)}")

                    except Exception as e:
                        self.feedback.CPW(f"更新灯光 '{light_name}' 的灯光组 '{current_light_group}' 失败: {e}")

    # 选择到灯光
    def _select_lights(self):
        """选择"""
        # 获取灯光组树的所有选中项
        selected_items = self.light_group_tree_widget.selectedItems()

        # 创建一个列表来存储所有选中的灯光名称
        selected_lights = []

        for item in selected_items:
            try:
                light_name = item.text(0)
                if cmds.objExists(light_name):  # 检查对象是否存在
                    selected_lights.append(light_name)
            except Exception as e:
                print(f"错误：无法选择 {item.text(0)} - {e}")

        # 如果存在有效的灯光对象列表，则一次性选择
        if selected_lights:
            cmds.select(selected_lights, replace=True)  # 全选
        else:
            cmds.select(clear=True)  # 如果列表为空，清除选择

    # 处理滑动条变化事件
    def handle_zoom_change(self):
        """处理滑动条变化事件"""
        # 假设滑动条范围是 50-200（表示50%到200%）
        scale_factor = self.light_group_tree_slider.value()
        font = QtGui.QFont()
        font.setPointSize(scale_factor)
        self.light_group_tree_widget.setFont(font)
        # 设置图标大小
        icon_size = scale_factor* 2
        self.light_group_tree_widget.setIconSize(QtCore.QSize(icon_size, icon_size))

    # 获取到场景选择灯光然后在选择灯光组
    def  _get_selected_lights_in_group(self):
        """
        获取当前场景中选择的灯光，并根据其所属的灯光组进行分类。
        返回一个列表，包含选中灯光组中与当前选择灯光匹配的灯光。
        """
        selected_lights = cmds.ls(selection=True, type='transform')  # 获取当前选择的物体

        matching_lights = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self.light_group_tree_widget)

        while iterator.value():
            item = iterator.value()
            item.setSelected(False)  # 取消所有节点的选择状态

            light_group_name = item.text(0)  # 假设灯光组名称在第 0 列

            # 如果节点名称与选中灯光匹配，就把它加入列表
            if light_group_name in selected_lights:
                item.setSelected(True)
                matching_lights.append(light_group_name)

            iterator += 1

        return matching_lights  # 返回一个列表，包含匹配的灯光名称

    # 选择aov
    def _select_aov_select_list_texts(self, texts):  # texts 是一个字符串列表
        self.aov_select_list_widget.clearSelection()  # 清除所有选择
        for text in texts:
            items = self.aov_select_list_widget.findItems(text, QtCore .Qt.MatchExactly)  # 查找完全匹配的项
            for item in items:
                item.setSelected(True)  # 标记为选中

    # 创建AOV灯光组
    def _create_aov_light_group(self):
        """
        创建AOV灯光组系统，将选中的灯光分组绑定到指定AOV通道
        流程：
        1. 获取用户选择的灯光组和AOV通道配置
        2. 遍历每个灯光组，为其创建对应的AOV通道
        3. 避免重复创建已存在的AOV节点
        4. 设置AOV节点参数
        """
        # 获取用户选择的灯光组配置
        selected_groups = self._get_all_items()
        # 从缓存加载AOV通道配置数据
        aov_channels = self.dataM.load_json(self.cache_path)

        # 遍历每个灯光组配置
        for group in selected_groups:
            # 跳过空组（根据业务逻辑需要可以调整）
            if not group['children']:
                continue

            # 获取当前灯光组名称
            light_group_name = group['text']

            # 跳过默认灯光组（根据业务逻辑需要可以调整）
            if light_group_name == 'default':
                continue

            # 为每个AOV通道创建对应的灯光组AOV
            for channel in aov_channels:
                # 生成符合规范的AOV名称（通道_灯光组）
                aov_name = f"{channel}_{light_group_name}"

                # 检查AOV是否已存在（优化后的检查方式）
                if self._aov_exists(aov_name):
                    print(f"AOV '{aov_name}' 已存在，跳过创建")
                    continue

                try:
                    # 创建AOV节点并配置参数
                    self._create_configured_aov(aov_name)
                    print(f"成功创建AOV：{aov_name}")
                except Exception as e:
                    print(f"创建AOV '{aov_name}' 失败：{str(e)}")
                    continue

    # 检查AOV是否存在
    def _aov_exists(self, aov_name):
        """
        检查指定名称的AOV是否已存在
        :param aov_name: 需要检查的AOV名称
        :return: bool - 是否存在
        """
        # 获取场景中所有aiAOV节点
        existing_aovs = cmds.ls(type='aiAOV') or []

        # 检查名称是否匹配（比遍历属性更高效）
        return any(cmds.getAttr(f"{aov}.name") == aov_name for aov in existing_aovs)

    # 创建并配置AOV节点
    def _create_configured_aov(self, aov_name):
        """
        创建并配置单个AOV节点
        :param aov_name: 需要创建的AOV名称
        """
        # 创建AOV节点（使用Arnold API接口）
        aov_interface = aovs.AOVInterface()
        new_aov = aov_interface.addAOV(aov_name)

        # 构造节点名称（arnold默认命名规则）
        aov_node = f"aiAOV_{aov_name}"

        # 参数配置（根据需求可扩展更多参数）
        # 6 = RGBA类型（根据实际需要确认数值是否正确）
        # 注意：Maya 2020+版本建议使用aov_interface.set_aov_type(...)方法
        if cmds.objExists(aov_node):
            cmds.setAttr(f"{aov_node}.type", 6)  # 设置AOV类型
            cmds.setAttr(f"{aov_node}.enabled", True)  # 启用AOV
        else:
            raise RuntimeError(f"AOV节点 {aov_node} 创建失败")
        # 储存配置文件


    # 为所有没有父级的子级项创建同名父级，并将子级移动至其下
    def _create_parent_for_child_items(self):
        """
        为没有父级的子级项或default组内的子级项创建同名父级，并将子级移动至其下
        规则：
        1. 为没有父级的灯光项创建同名父级组
        2. 为default组内的灯光项创建同名父级组（即使它们已经有父级）
        3. 其它已有父级的灯光项保持不变
        4. 确保有default父级组存在
        5. 删除除default外的空父级组
        """
        self.update_light_group_data()  # 同步数据到Maya
        parent_icon = QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png'))  # 父级图标

        with block_updates_and_signals(self.light_group_tree_widget):
            # 查找default父级
            default_parent = None
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                top_item = self.light_group_tree_widget.topLevelItem(i)
                if top_item.text(0) == "default":
                    default_parent = top_item
                    break

            # 如果default父级不存在，创建一个
            if not default_parent:
                default_parent = QtWidgets.QTreeWidgetItem()
                default_parent.setText(0, "default")
                default_parent.setIcon(0, parent_icon)
                self.light_group_tree_widget.addTopLevelItem(default_parent)
                default_parent.setExpanded(True)

            # 收集需要处理的子级项（无父级的项或default组内的项）
            items_to_process = []
            default_children = []

            # 先收集所有顶级项（没有父级的灯光项）
            top_level_items = []
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                item = self.light_group_tree_widget.topLevelItem(i)
                # 检查是否为灯光项（无子项的项）
                if item.childCount() == 0:
                    top_level_items.append(item)

            # 收集default组内的子级项
            for j in range(default_parent.childCount()):
                default_children.append(default_parent.child(j))

            # 合并需要处理的项
            items_to_process.extend(top_level_items)
            items_to_process.extend(default_children)

            # 处理每个需要移动的子级项
            for child_item in items_to_process:
                child_name = child_item.text(0)

                # 跳过处理名为"default"的子项，防止循环引用
                if child_name == "default":
                    continue

                # 查找是否已有同名父级
                existing_parent = None
                for i in range(self.light_group_tree_widget.topLevelItemCount()):
                    top_item = self.light_group_tree_widget.topLevelItem(i)
                    if top_item.text(0) == child_name and top_item != child_item:
                        existing_parent = top_item
                        break

                # 处理找到的同名父级或创建新父级
                if existing_parent:
                    # 父级已存在则移动子项
                    current_parent = child_item.parent()
                    if current_parent:
                        current_parent.removeChild(child_item)
                    else:  # 顶级项
                        index = self.light_group_tree_widget.indexOfTopLevelItem(child_item)
                        if index != -1:
                            self.light_group_tree_widget.takeTopLevelItem(index)
                    existing_parent.addChild(child_item)
                else:
                    # 创建新父级并设置属性
                    new_parent = QtWidgets.QTreeWidgetItem()
                    new_parent.setText(0, child_name)
                    new_parent.setIcon(0, parent_icon)

                    # 先处理从原父级移除
                    current_parent = child_item.parent()
                    if current_parent:
                        current_parent.removeChild(child_item)
                    else:  # 顶级项
                        index = self.light_group_tree_widget.indexOfTopLevelItem(child_item)
                        if index != -1:
                            self.light_group_tree_widget.takeTopLevelItem(index)

                    # 添加到新父级并将新父级添加到树
                    new_parent.addChild(child_item)
                    self.light_group_tree_widget.addTopLevelItem(new_parent)
                    new_parent.setExpanded(True)

            # 删除空父级（排除"default"）
            for i in range(self.light_group_tree_widget.topLevelItemCount() - 1, -1, -1):
                top_item = self.light_group_tree_widget.topLevelItem(i)
                if top_item.childCount() == 0 and top_item.text(0) != "default":
                    self.light_group_tree_widget.takeTopLevelItem(i)

        # 完成后同步更新
        self.update_light_group_data()

    # 清除所有父级并将灯光移动到默认default组
    def _clear_all_light_groups(self):
        """
        清除非default父级的所有灯光组，将子项移动到default父级下
        流程：
        1. 确保default父级存在
        2. 收集所有非default父级
        3. 将子项移动到default父级下
        4. 删除空父级
        """
        self.update_light_group_data()  # 同步初始数据
        with block_updates_and_signals(self.light_group_tree_widget):
            # 获取或创建default父级
            default_parent = None
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                item = self.light_group_tree_widget.topLevelItem(i)
                if item.text(0) == "default":
                    default_parent = item
                    break
            # 若不存在则创建default父级
            if not default_parent:
                default_parent = QtWidgets.QTreeWidgetItem()
                default_parent.setText(0, "default")
                default_parent.setIcon(0, QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png')))
                self.light_group_tree_widget.addTopLevelItem(default_parent)
                default_parent.setExpanded(True)
            # 收集所有需要删除的非default父级
            parents_to_remove = []
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                item = self.light_group_tree_widget.topLevelItem(i)
                if item.text(0) != "default":
                    parents_to_remove.append(item)
            # 处理每个待删除父级的子项
            for parent in parents_to_remove:
                # 移动所有子项到default父级
                while parent.childCount() > 0:
                    child = parent.takeChild(0)  # 取出第一个子项
                    default_parent.addChild(child)
                # 删除空父级
                index = self.light_group_tree_widget.indexOfTopLevelItem(parent)
                if index != -1:
                    self.light_group_tree_widget.takeTopLevelItem(index)
            # 确保default父级至少有一个子项
            if default_parent.childCount() == 0:
                default_child = QtWidgets.QTreeWidgetItem()
                default_child.setText(0, "default_light")
                default_parent.addChild(default_child)
        self.update_light_group_data()  # 最终数据同步

    # 清除通过插件创建的所有自定义AOV通道
    def _clear_custom_aovs(self):
        """
        清除通过插件创建的所有自定义AOV通道
        - 仅删除名称符合"通道_灯光组"格式的AOV节点
        - 保留RGBA/P/Z/N等基础通道
        - 支持同时清理多个灯光组配置
        """
        # 获取用户选择的通道配置（从缓存加载）
        selected_channels = self.dataM.load_json(self.cache_path)

        # 获取场景中所有aiAOV节点
        all_aovs = cmds.ls(type='aiAOV') or []

        # 遍历处理每个AOV节点
        deleted_aovs = []
        for aov_node in all_aovs:
            try:
                aov_name = cmds.getAttr(f"{aov_node}.name")
                # 匹配规则：通道名_任意字符 且通道名在用户选择列表中
                if any(aov_name.startswith(f"{channel}_") for channel in selected_channels):
                    cmds.delete(aov_node)
                    deleted_aovs.append(aov_name)
            except Exception as e:
                self.feedback.CPW(f"清理AOV失败: {aov_node} - {str(e)}")

        # 反馈清理结果
        result_msg = f"已清理自定义AOV通道 [{len(deleted_aovs)}个]:\n" + "\n".join(deleted_aovs)
        self.feedback.CPW(result_msg if deleted_aovs else "未找到需要清理的自定义AOV通道")


    # 异步保存 AOV 选择列表的缓存数据到指定文件路径中
    def _modify_aov_select_list_cache(self):
        """
        异步保存 AOV 选择列表的缓存数据到指定文件路径中。

        此方法使用 QtCore.QTimer.singleShot(0, ...) 进行异步调用，
        确保在 UI 操作（例如点击或选择改变）完成后再执行保存操作，
        避免阻塞或数据不完整的情况。

        工作流程：
        1. 获取 QListWidget 中所有被选中的项。
        2. 提取每个选中项的文本内容并生成列表。
        3. 使用 self.dataM.save_json() 方法将数据保存到缓存文件路径。
        """

        def modify_cache():
            # 从 QListWidget 中获取当前选中的项列表
            selected_items = self.aov_select_list_widget.selectedItems()

            # 提取每个选中项的文本内容，组成新的缓存数据列表
            new_cache_data = [item.text() for item in selected_items]

            # 将缓存数据保存到指定路径 (self.cache_path)
            self.dataM.save_json(self.cache_path, new_cache_data)

        # 使用 Qt 的定时器单次调用机制来延迟执行保存操作
        QtCore.QTimer.singleShot(0, lambda *args: modify_cache())

def  AOVLightGroupManagerInstance():
    aov_light_group_manager = AOVLightGroupManager()
    aov_light_group_manager.show()
