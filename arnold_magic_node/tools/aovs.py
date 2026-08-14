"""AOV 灯光组管理功能编排。"""

from arnold_magic_node.maya.aovs import MayaAovAdapter
from arnold_magic_node._qt_compat import QCoreApplication
from .feedback import FeedbackPrompt


class AovLightGroupTool(object):
    def __init__(self, adapter=None, feedback=None):
        self.adapter = adapter or MayaAovAdapter()
        self.feedback = feedback or FeedbackPrompt(self.adapter)

    def update_light_groups(self, groups):
        """把界面树中的灯光组写回 Maya 灯光节点。"""

        for group in groups:
            group_name = group["text"]
            for child in group.get("children") or ():
                light_name = child["text"]
                try:
                    old_group = self.adapter.get_attr(light_name + ".aiAov")
                    if group_name != old_group:
                        if not isinstance(group_name, str):
                            self.feedback.warn(
                                QCoreApplication.translate(
                                    "AovLightGroupTool",
                                    "Light group name must be a string, got: {0}",
                                ).format(type(group_name))
                            )
                            continue
                        self.adapter.set_attr(
                            light_name + ".aiAov",
                            group_name,
                            value_type="string",
                        )
                except Exception as error:
                    self.feedback.warn(
                        QCoreApplication.translate(
                            "AovLightGroupTool",
                            "Failed to update light group '{0}' of light '{1}': {2}",
                        ).format(light_name, group_name, error)
                    )

    def select_lights(self, light_names):
        valid = [
            light_name
            for light_name in light_names
            if self.adapter.object_exists(light_name)
        ]
        if valid:
            self.adapter.select(valid, replace=True)
        else:
            self.adapter.select(clear=True)
        return valid

    def selected_transforms(self):
        return self.adapter.list_nodes(selection=True, type="transform")

    def aov_exists(self, aov_name):
        return any(
            self.adapter.get_attr(node_name + ".name") == aov_name
            for node_name in self.adapter.list_nodes(type="aiAOV")
        )

    def create_configured_aov(self, aov_name):
        created = self.adapter.create_aov(aov_name)
        node_name = "aiAOV_" + aov_name
        if not self.adapter.object_exists(node_name):
            raise RuntimeError(
                QCoreApplication.translate(
                    "AovLightGroupTool", "Failed to create AOV node {0}"
                ).format(node_name)
            )
        self.adapter.set_attr(node_name + ".type", 6)
        self.adapter.set_attr(node_name + ".enabled", True)
        return created

    def create_light_group_aovs(self, groups, channels):
        created = []
        for group in groups:
            if not group.get("children") or group["text"] == "default":
                continue
            for channel in channels:
                aov_name = "{}_{}".format(channel, group["text"])
                if self.aov_exists(aov_name):
                    continue
                try:
                    self.create_configured_aov(aov_name)
                    created.append(aov_name)
                except Exception as error:
                    self.feedback.warn(
                        QCoreApplication.translate(
                            "AovLightGroupTool", "Failed to create AOV '{0}': {1}"
                        ).format(aov_name, error)
                    )
        return created

    def clear_custom_aovs(self, selected_channels):
        deleted = []
        for node_name in self.adapter.list_nodes(type="aiAOV"):
            try:
                aov_name = self.adapter.get_attr(node_name + ".name")
                if any(
                    aov_name.startswith(channel + "_")
                    for channel in selected_channels
                ):
                    self.adapter.delete(node_name)
                    deleted.append(aov_name)
            except Exception as error:
                self.feedback.warn(
                    QCoreApplication.translate(
                        "AovLightGroupTool", "Failed to clear AOV: {0} - {1}"
                    ).format(node_name, error)
                )
        return deleted


__all__ = ["AovLightGroupTool"]
