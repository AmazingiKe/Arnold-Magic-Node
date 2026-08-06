"""Maya 选择与场景查询适配器。"""

from collections import defaultdict

from .nodes import MayaNodeAdapter


DEFAULT_SCENE_QUERY = {
    "geometry": True,
    "lights": True,
    "cameras": True,
    "long": True,
    "materials": True,
    "textures": True,
    "assemblies": True,
}


class MayaSceneAdapter(MayaNodeAdapter):
    def selected_nodes_by_type(self):
        return self._group_nodes(self.list_nodes(sl=True))

    def scene_nodes_by_type(self):
        return self._group_nodes(self.list_nodes(**DEFAULT_SCENE_QUERY))

    def _group_nodes(self, nodes):
        result = defaultdict(list)
        for node_name in nodes:
            result[self.node_type(node_name)].append(node_name)
        return dict(result)

    def arnold_lights_and_types(self, light_types):
        result = {}
        for light_type in light_types:
            for shape in self.list_nodes(type=light_type):
                parents = self.list_relatives(shape, parent=True)
                if parents:
                    result[parents[0]] = light_type
        return result

    def group_lights(self, lights):
        result = defaultdict(list)
        for light_name in lights:
            try:
                light_group = self.get_attr(light_name + ".aiAov")
                if not isinstance(light_group, str):
                    light_group = "default"
            except Exception:
                light_group = "default"
            result[light_group].append(light_name)
        return dict(result)

    def file_texture_paths(self, material_node):
        result = {}
        visited = set()

        def traverse(node_name):
            if node_name in visited:
                return
            visited.add(node_name)
            upstream = self.list_connections(
                node_name,
                source=True,
                destination=False,
                skipConversionNodes=True,
            )
            for source_node in upstream:
                if self.node_type(source_node) == "file":
                    attribute = source_node + ".fileTextureName"
                    if self.object_exists(attribute):
                        result[source_node] = self.get_attr(attribute)
                else:
                    traverse(source_node)

        traverse(material_node)
        return result


__all__ = ["DEFAULT_SCENE_QUERY", "MayaSceneAdapter"]
