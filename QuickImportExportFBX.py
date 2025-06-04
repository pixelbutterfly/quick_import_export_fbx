
bl_info = {
    # required
    'name': 'Quick Import/Export FBX',
    'blender': (3, 5, 0),
    'category': 'Object',
    # optional
    'version': (1, 0, 0),
    'author': 'pixelbutterfly.com',
    'description': 'Import/Export FBX from the 3D viewport.',
    'doc_url': 'https://github.com/pixelbutterfly/',
}

import bpy

# == GLOBAL VARIABLES
PROPS = [
    ('export_file_path', bpy.props.StringProperty(name = "Export Location",default = "C:/Users/username/Desktop/",description = "Export Location(nust be absolute!",subtype = 'DIR_PATH')),
    ('export_file_name', bpy.props.StringProperty(name = "File Name",default = "temp.fbx",description = "File Name")),
    ('import_file_path', bpy.props.StringProperty(name = "Import Location",default = "C:/Users/username/Desktop/",description = "Import Location(nust be absolute!",subtype = 'DIR_PATH')),
    ('import_file_name', bpy.props.StringProperty(name = "File Name",default = "temp.fbx",description = "File Name")),
    ('global_scale_export', bpy.props.FloatProperty(name = "Scale",default = 1,description = "Scale all data (Some importers do not support scaled armatures!)")),
    ('apply_unit_scale', bpy.props.BoolProperty(name = "Apply Unit",default = True,description = "Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)")),
    ('apply_scale_options', bpy.props.EnumProperty(name = "Apply Scalings",description = "How to apply custom and units scalings in generated FBX file (Blender uses FBX scale to detect units on import, but many other applications do not handle the same way)", default = 'FBX_SCALE_NONE', items = (('FBX_SCALE_NONE','All Local','All Local'),('FBX_SCALE_UNITS','FBX Units Scale','FBX Units Scale'),('FBX_SCALE_CUSTOM','FBX Custom Scale','FBX Custom Scale'),('FBX_SCALE_ALL','FBX All','FBX All')))),
    ('use_space_transform', bpy.props.BoolProperty(name = "Use Space Transform",default = True ,description = "Use Space Transform, Apply global space transform to the object rotations. When disabled only the axis space is written to the file and all object transforms are left as-is")),
    ('use_subsurf_export', bpy.props.BoolProperty(name = "Export Subdivision Surface",default = False ,description = "Export the last Catmull-Rom subdivision modifier as FBX subdivision (does not apply the modifier even if ‘Apply Modifiers’ is enabled)")),
    ('use_subsurf_import', bpy.props.BoolProperty(name = "Subdivision Data",default = False ,description = "Import FBX subdivision information as subdivision surface modifiers")),
    ('bake_space_transform_export', bpy.props.BoolProperty(name = "Apply Transform",default = False ,description = "Apply Transform, Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risk, known to be broken with armatures/animations)")),
    ('bake_space_transform_import', bpy.props.BoolProperty(name = "Apply Transform",default = False ,description = "Apply Transform, Bake space transform into object data, avoids getting unwanted rotations to objects when target space is not aligned with Blender’s space (WARNING! experimental option, use at own risk, known to be broken with armatures/animations)")),
    ('use_mesh_modifiers', bpy.props.BoolProperty(name = "Apply Modifiers",default = True ,description = "Apply modifiers to mesh objects (except Armature ones) - WARNING: prevents exporting shape keys")),
    ('use_mesh_edges', bpy.props.BoolProperty(name = "Loose Edges",default = False ,description = "Export loose edges (as two-vertices polygons)")),
    ('use_triangles', bpy.props.BoolProperty(name = "Triangulate Faces",default = False ,description = "Convert all faces to triangles)")),
    ('use_tspace', bpy.props.BoolProperty(name = "Tangent Space",default = False ,description = "Add binormal and tangent vectors, together with normal they form the tangent space (will only work correctly with tris/quads only meshes!))")),
    ('mesh_smooth_type', bpy.props.EnumProperty(name = "Smoothing",description = "Smoothing", default = 'OFF', items = (("OFF","Normals Only","export only normals"),("FACE","Face","write face smoothing"),("EDGE","Edge","write edge smoothing")))),
    ('colors_type_export', bpy.props.EnumProperty(name = "Vertex Colors",description = "Export vertex color attributes", default = 'SRGB', items = (("NONE","None","Do not export color attributes."),("SRGB","sRGB","Export colors in sRGB color space."),("LINEAR","Linear","Export colors in linear color space.")))),
    ('colors_type_import', bpy.props.EnumProperty(name = "Vertex Colors",description = "Import vertex color attributes", default = 'SRGB', items = (("NONE","None","Do not import color attributes."),("SRGB","sRGB","Import colors in sRGB color space."),("LINEAR","Linear","Import colors in linear color space.")))),
    ('prioritize_active_color', bpy.props.BoolProperty(name = "Prioritize Active Color",default = False ,description = "Export loose edges (as two-vertices polygons)")),
    ('axis_forward_export', bpy.props.EnumProperty(name = "Axis Forward",description = "Axis Forward", default = '-Z', items = (("X","X Forward","X Forward"),("Y","Y Forward","Y Forward"),("Z","Z Forward","Z Forward"),("-X","-X Forwarc","-X Forward"),("-Y","-Y Forward","-Y Forward"),("-Z","-Z Forward","-Z Forward")))),
    ('axis_up_export', bpy.props.EnumProperty(name = "Axis Up",description = "Axis Up", default = 'Y', items = (("X","X Up","X Up"),("Y","Y Up","Y Up"),("Z","Z Up","Z Up"),("-X","-X Up","-X Up"),("-Y","-Y Up","-Y Up"),("-Z","-Z Up","-Z Up")))),
    ('global_scale_import', bpy.props.FloatProperty(name = "Scale",default = 1,description = "Make sure active color will be exported first. Could be important since some other software can discard other color attributes besides the first one")),
    ('decal_offset', bpy.props.FloatProperty(name = "Decal Offset",default = 0,description = "Displace geometry of alpha meshes")),
    ('use_prepost_rot', bpy.props.BoolProperty(name = "Use Pre/Post Rotation",default = False ,description = "Use pre/post rotation from FBX transform (you may have to disable that in some cases)")),
    ('use_manual_orientation', bpy.props.BoolProperty(name = "Manual Orientation",default = False ,description = "Specify orientation and scale, instead of using embedded data in FBX file)")),
    ('use_custom_normals', bpy.props.BoolProperty(name = "Use Custom Normals",default = True ,description = "Import custom normals, if available (otherwise Blender will recompute them)")),
    ('use_image_search', bpy.props.BoolProperty(name = "Image Search",default = True ,description = "Search subdirs for any associated images (WARNING: may be slow)")),
    ('use_alpha_decals', bpy.props.BoolProperty(name = "Alpha Decals",default = False ,description = "Treat materials with alpha as decals (no shadow casting)")),
    ('use_custom_props', bpy.props.BoolProperty(name = "Use Custom Properties",default = True ,description = "Import user properties as custom properties)")),
    ('use_custom_props_enum_as_string', bpy.props.BoolProperty(name = "Import Enums as Strings",default = True ,description = "Import Enums As Strings, Store enumeration values as strings)")),
    ('axis_forward_import', bpy.props.EnumProperty(name = "Axis Forward",description = "Axis Forward", default = '-Z', items = (("X","X Forward","X Forward"),("Y","Y Forward","Y Forward"),("Z","Z Forward","Z Forward"),("-X","-X Forwarc","-X Forward"),("-Y","-Y Forward","-Y Forward"),("-Z","-Z Forward","-Z Forward")))),
    ('axis_up_import', bpy.props.EnumProperty(name = "Axis Up",description = "Axis Up", default = 'Y', items = (("X","X Up","X Up"),("Y","Y Up","Y Up"),("Z","Z Up","Z Up"),("-X","-X Up","-X Up"),("-Y","-Y Up","-Y Up"),("-Z","-Z Up","-Z Up"))))
]
    
# == OPERATORS
class QuickExportFBX(bpy.types.Operator):
    
    bl_idname = 'opr.quick_export_fbx'
    bl_label = 'Quick Export FBX'
    bl_options = {'REGISTER', "UNDO"}
    
    @classmethod
    def description(cls, context, properties):
        return "Export FBX for selected objects"
    
    def execute(self, context):
        
        final_filepath = context.scene.export_file_path + context.scene.export_file_name
        bpy.ops.export_scene.fbx(filepath= final_filepath, use_selection = True, mesh_smooth_type = context.scene.mesh_smooth_type, use_mesh_edges = context.scene.use_mesh_edges, axis_forward = context.scene.axis_forward_export, axis_up = context.scene.axis_up_export, use_triangles = context.scene.use_triangles, use_tspace = context.scene.use_tspace , use_mesh_modifiers = context.scene.use_mesh_modifiers, global_scale = context.scene.global_scale_export, use_space_transform = context.scene.use_space_transform, bake_space_transform = context.scene.bake_space_transform_export ,apply_unit_scale = context.scene.apply_unit_scale, apply_scale_options = context.scene.apply_scale_options , use_subsurf = context.scene.use_subsurf_export,prioritize_active_color = context.scene.prioritize_active_color, colors_type = context.scene.colors_type_export)
         

        return {'FINISHED'}	
    
class QuickImportFBX(bpy.types.Operator):
    
    bl_idname = 'opr.quick_import_fbx'
    bl_label = 'Quick Import FBX'
    bl_options = {'REGISTER', "UNDO"}
    
    @classmethod
    def description(cls, context, properties):
        return "Import FBX for selected objects"
    
    def execute(self, context):
 
        final_filepath = context.scene.import_file_path + context.scene.import_file_name
        bpy.ops.import_scene.fbx(filepath= final_filepath, use_custom_normals = context.scene.use_custom_normals, global_scale = context.scene.global_scale_import, axis_forward = context.scene.axis_forward_import, axis_up = context.scene.axis_up_import, use_image_search = context.scene.use_image_search , use_custom_props = context.scene.use_custom_props, use_custom_props_enum_as_string = context.scene.use_custom_props_enum_as_string, use_manual_orientation = context.scene.use_manual_orientation,colors_type = context.scene.colors_type_import, use_alpha_decals = context.scene.use_alpha_decals,use_subsurf = context.scene.use_subsurf_import,decal_offset = context.scene.decal_offset, use_prepost_rot = context.scene.use_prepost_rot,bake_space_transform = context.scene.bake_space_transform_import)


        return {'FINISHED'}	
    
class ResetImportSettings(bpy.types.Operator):
    
    bl_idname = 'opr.reset_import_settings'
    bl_label = 'ResetImportSettings'
    bl_options = {'REGISTER', "UNDO"}
    
    @classmethod
    def description(cls, context, properties):
        return "Reset Import Settings"
    
    def execute(self, context):
    
        bpy.context.scene.use_custom_normals = True
        bpy.context.scene.use_subsurf_import = False
        bpy.context.scene.use_custom_props = True
        bpy.context.scene.use_custom_props_enum_as_string = True
        bpy.context.scene.use_image_search = True
        bpy.context.scene.colors_type_import= 'SRGB'
        bpy.context.scene.global_scale_import = 1
        bpy.context.scene.use_alpha_decals = False
        bpy.context.scene.decal_offset =  0
        bpy.context.scene.bake_space_transform_import = False
        bpy.context.scene.use_prepost_rot = False
        bpy.context.scene.use_manual_orientation = False
        bpy.context.scene.axis_forward_import = '-Z'
        bpy.context.scene.axis_up_import = 'Y'

        return {'FINISHED'}	
    
class ResetExportSettings(bpy.types.Operator):
    
    bl_idname = 'opr.reset_export_settings'
    bl_label = 'Reset Export Settings'
    bl_options = {'REGISTER', "UNDO"}
    
    @classmethod
    def description(cls, context, properties):
        return "Reset Export Settings"
    
    def execute(self, context):
    
        bpy.context.scene.global_scale_export = 1.0
        bpy.context.scene.apply_scale_options = 'FBX_SCALE_NONE'
        bpy.context.scene.axis_forward_export = '-Z'
        bpy.context.scene.axis_up_export = 'Y'
        bpy.context.scene.apply_unit_scale = True
        bpy.context.scene.use_space_transform = True
        bpy.context.scene.bake_space_transform_export = False
        bpy.context.scene.mesh_smooth_type = 'OFF'
        bpy.context.scene.use_subsurf_export = False
        bpy.context.scene.use_mesh_modifiers = True
        bpy.context.scene.use_mesh_edges = False
        bpy.context.scene.use_triangles = False
        bpy.context.scene.use_tspace = False
        bpy.context.scene.colors_type_export = 'SRGB'
        bpy.context.scene.prioritize_active_color = False
        return {'FINISHED'}	


# == PANELS
        
class ExportPanel( bpy.types.Panel):
    bl_idname = 'ExportPanel'
    bl_label = "Quick Export FBX"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    #bl_parent_id = "VIEW3D_PT_quick_export_fbx"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = layout.column(align=True)
        
        vis_box = layout.box()
        
        vis_box.operator('opr.quick_export_fbx', text='Quick Export FBX')
        row = vis_box.row()
        row.prop(context.scene, 'export_file_path')
        row = vis_box.row()
        row.prop(context.scene, 'export_file_name')
        
class ImportPanel( bpy.types.Panel):
    bl_idname = 'ImportPanel'
    bl_label = "Quick Import FBX"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    #bl_parent_id = "VIEW3D_PT_quick_export_fbx"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene	   
        row = layout.row()
        vis_box = layout.box()

        vis_box.operator('opr.quick_import_fbx', text='Quick Import FBX')
        row = vis_box.row()
        row.prop(context.scene, 'import_file_path')
        row = vis_box.row()
        row.prop(context.scene, 'import_file_name')

        
class ExportSettingsPanel( bpy.types.Panel):
    bl_idname = 'ExportSettingsPanel'
    bl_label = "Export Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ExportPanel"
    
    def draw(self, context):
        layout = self.layout
        layout.operator('opr.reset_export_settings', text='Reset All')

class ImportSettingsPanel( bpy.types.Panel):
    bl_idname = 'ImportSettingsPanel'
    bl_label = "Import Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ImportPanel"
    
    def draw(self, context):
        layout = self.layout
        layout.operator('opr.reset_import_settings', text='Reset All')



class ExportTransformPanelSettings( bpy.types.Panel):
    bl_idname = 'ExportTransformPanelSettings'
    bl_label = "Transform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ExportSettingsPanel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene	   
        row = layout.row()
        vis_box = layout.box()
        vis_box.prop(context.scene, 'global_scale_export')
        vis_box.prop(context.scene, 'apply_scale_options')
        vis_box.prop(context.scene, 'axis_forward_export')
        vis_box.prop(context.scene, 'axis_up_export')
        vis_box.prop(context.scene, 'apply_unit_scale')
        vis_box.prop(context.scene, 'use_space_transform')
        vis_box.prop(context.scene, 'bake_space_transform_export')

class ExportGeometryPanelSettings( bpy.types.Panel):
    bl_idname = 'ExportGeometryPanelSettings'
    bl_label = "Geometry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ExportSettingsPanel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene	   
        row = layout.row()
        vis_box = layout.box()
        vis_box.prop(context.scene, 'mesh_smooth_type')
        vis_box.prop(context.scene, 'use_subsurf_export')
        vis_box.prop(context.scene, 'use_mesh_modifiers')
        vis_box.prop(context.scene, 'use_mesh_edges')
        vis_box.prop(context.scene, 'use_triangles')
        vis_box.prop(context.scene, 'use_tspace')
        vis_box.prop(context.scene, 'colors_type_export')
        vis_box.prop(context.scene, 'prioritize_active_color')
        
    
        
class ImportIncludePanelSettings( bpy.types.Panel):
    bl_idname = 'ImportIncludePanelSettings'
    bl_label = "Include"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ImportSettingsPanel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene	   
        row = layout.row()
        
        vis_box = layout.box()
        vis_box.prop(context.scene, 'use_custom_normals')
        vis_box.prop(context.scene, 'use_subsurf_import')
        vis_box.prop(context.scene, 'use_custom_props')
        vis_box.prop(context.scene, 'use_custom_props_enum_as_string')
        vis_box.prop(context.scene, 'use_image_search')
        vis_box.prop(context.scene, 'colors_type_import')

class ImportTransformPanelSettings( bpy.types.Panel):
    bl_idname = 'ImportTransformPanelSettings'
    bl_label = "Transform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ImportSettingsPanel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene	   
        row = layout.row()
        vis_box = layout.box()
        
        vis_box.prop(context.scene, 'global_scale_import')
        vis_box.prop(context.scene, 'use_alpha_decals')
        vis_box.prop(context.scene, 'decal_offset')
        vis_box.prop(context.scene, 'bake_space_transform_import')
        vis_box.prop(context.scene, 'use_prepost_rot')
        
class ImportManualOrientationPanelSettings( bpy.types.Panel):
    bl_idname = 'ImportManualOrientationPanelSettings'
    bl_label = "Manual Orientation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quick Export FBX"
    bl_parent_id = "ImportSettingsPanel"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene	   
        row = layout.row()
        row.prop(context.scene, 'use_manual_orientation')
        vis_box = layout.box()
        vis_box.enabled = context.scene.use_manual_orientation
        vis_box.prop(context.scene, 'axis_forward_import')
        vis_box.prop(context.scene, 'axis_up_import')
        

class PanelPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Addon Preferences https://docs.blender.org/api/blender_python_api_2_67_release/bpy.types.AddonPreferences.html

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        box.label(text="Additional Links")
        col = box.column(align=True)
        col.operator("wm.url_open", text="Developer Website", icon='WORDWRAP_ON').url = "https://www.pixelbutterfly.com"


# == MAIN ROUTINE
CLASSES = [
    QuickExportFBX,
    QuickImportFBX,
    ExportPanel,
    ImportPanel,
    ResetImportSettings,
    ResetExportSettings,
    ExportSettingsPanel,
    ExportTransformPanelSettings,
    ExportGeometryPanelSettings,
    ImportSettingsPanel,
    ImportIncludePanelSettings,
    ImportTransformPanelSettings,
    ImportManualOrientationPanelSettings
    
    
]

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for klass in CLASSES:
        bpy.utils.register_class(klass)
        

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
        

if __name__ == '__main__':
    register()
