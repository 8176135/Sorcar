# Copyright (C) 2019 Punya Aachman
# aachman98@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
	"name": "Sorcar",
    "author": "Punya Aachman",
    "version": (3, 1, 0),
    "blender": (2, 80, 0),
    "location": "Node Editor",
    "description": "Create procedural meshes using Node Editor",
	"category": "Node"
}

import bpy
import nodeitems_utils
import addon_utils
import importlib
import os

from bpy.types import NodeTree, Operator, PropertyGroup
from bpy.props import BoolProperty, StringProperty
from nodeitems_utils import NodeItem
from .helper import update_each_frame, print_log
from .tree.ScNodeCategory import ScNodeCategory

def import_tree():
    return getattr(importlib.import_module(".tree.ScNodeTree", __name__), "ScNodeTree")

def import_ops(path="./"):
    out = []
    for i in bpy.path.module_names(path + "operators"):
        out.append(getattr(importlib.import_module(".operators." + i[0], __name__), i[0]))
        print_log("IMPORT OP", msg=i[0])
    return out

def import_sockets(path="./"):
    out = []
    for i in bpy.path.module_names(path + "sockets"):
        out.append(getattr(importlib.import_module(".sockets." + i[0], __name__), i[0]))
        print_log("IMPORT SOCKET", msg=i[0])
    return out

def import_nodes(path="./"):
    out = {}
    for cat in [i for i in os.listdir(path + "nodes") if not i.startswith("_")]:
        out[cat] = []
        for i in bpy.path.module_names(path + "nodes/" + cat):
            out[cat].append(getattr(importlib.import_module(".nodes." + cat + "." + i[0], __name__), i[0]))
            print_log("IMPORT NODE", bpy.path.display_name(cat), msg=i[0])
    return out

all_classes = []

def register():
    print("-------------REGISTER SORCAR-------------")
    path = repr([i for i in addon_utils.modules() if i.bl_info['name'] == bpy.path.display_name(__name__)][0]).split("from '")[1].split("__init__.py'>")[0]
    classes_ops = import_ops(path)
    classes_sockets = import_sockets(path)
    classes_nodes = import_nodes(path)

    global all_classes
    all_classes = [import_tree()]
    all_classes.extend(classes_ops)
    all_classes.extend(classes_sockets)

    total_nodes = 0
    node_categories = []
    for cat in classes_nodes:
        total_nodes += len(classes_nodes[cat])
        node_categories.append(ScNodeCategory(identifier="sc_"+cat, name=bpy.path.display_name(cat), items=[NodeItem(i.bl_idname) for i in classes_nodes[cat]]))
        all_classes.extend(classes_nodes[cat])
    
    for i in all_classes:
        bpy.utils.register_class(i)
    nodeitems_utils.register_node_categories("sc_node_categories", node_categories)
    if not (update_each_frame in bpy.app.handlers.frame_change_post):
        bpy.app.handlers.frame_change_post.append(update_each_frame)
    
    print_log("REGISTERED", msg="{} operators, {} sockets & {} nodes ({} categories)".format(len(classes_ops), len(classes_sockets), total_nodes, len(classes_nodes)))

def unregister():
    print("------------UNREGISTER SORCAR----------------")
    global all_classes
    all_classes.reverse()

    for i in all_classes:
        bpy.utils.unregister_class(i)
        print_log("UNREGISTER", i.bl_idname, None, i.bl_label)
    nodeitems_utils.unregister_node_categories("sc_node_categories")
    if (update_each_frame in bpy.app.handlers.frame_change_post):
        bpy.app.handlers.frame_change_post.remove(update_each_frame)

    print_log("UNREGISTERED", msg=str(len(all_classes)) + " classes")