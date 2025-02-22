import bpy

from bpy.props import PointerProperty, StringProperty, IntProperty, FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScIcoSphere(Node, ScInputNode):
    bl_idname = "ScIcoSphere"
    bl_label = "Ico Sphere"

    in_subdivision: IntProperty(default=2, min=1, max=10, update=ScNode.update_value)
    in_radius: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketNumber", "Subdivisions").init("in_subdivision", True)
        self.inputs.new("ScNodeSocketNumber", "Radius").init("in_radius", True)
    
    def error_condition(self):
        return (
            super().error_condition()
            or (self.inputs["Subdivisions"].default_value < 1 or self.inputs["Subdivisions"].default_value > 10)
            or self.inputs["Radius"].default_value < 0
        )
    
    def functionality(self):        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions = int(self.inputs["Subdivisions"].default_value),
            radius = self.inputs["Radius"].default_value,
            calc_uvs = self.inputs["Generate UVs"].default_value
        )