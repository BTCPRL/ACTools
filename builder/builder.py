# Python imports
import imp
import json
import os
import sys

# Maya imports
import maya.cmds as cmds
# CARF imports
from CARF.data import global_data as g_data
from CARF.maya_core import controls


class Builder(object):
    """
    Handles the build process of a given asset, requires a session object with
    paths information. It will create a Rig object based on each asset's build
    code.
    """

    def __init__(self, session_obj):

        self.session_obj = session_obj
        self.build_file = '%s_build.py' % session_obj.asset_name
        self.stage = 'init'
        self.rig_base = False
        self.template_data = None
        # Dynamically imports and reload [asset_name]_build.py
        self.asset_module = imp.load_source(
            'imported_asset_module',
            os.path.join(session_obj.paths['asset'], self.build_file)
        )

    def set_stage(self, stage):
        """Changes current stage of the builder.
        Needed for preventing undesired exports/imports
        """
        if stage not in g_data.builder_stages:
            raise Exception('%s is not a valid stage for the builder')
        else:
            self.stage = stage

    def initialize_rig(self):
        """ Creates an instance of the rig object
        """
        # Creates a Rig object from the imported module
        self.rig = self.asset_module.Asset(
            asset_name=self.session_obj.asset_name
        )

    def configure_rig(self):
        """TODO: Still not too sure what's gonna happen here
        """
        self.rig.configure_rig()

    def setup_rig_base(self):
        """ Builds base groups and root controller.
        Sets rig_base attribute
        """
        self.rig.build_base_grps()
        self.rig.build_root()
        self.rig_base = True

    def import_geo(self):
        """Imports the asset geo to the scene.
        If there's a rig base, it parents the imported geo under GEO_GRP
        """
        new_nodes = cmds.file(
            self.session_obj.paths['geo'],
            i=True, returnNewNodes=True
        )

        if self.rig_base:
            cmds.parent(self.session_obj.asset_name, self.rig.geo_grp)

        return new_nodes

    def build_template(self):
        """ Call to rig's template build.
        Will build each component's tempalte
        """
        path = self.session_obj.paths['template']
        template_file = os.path.join(path, 'template.json')
        if os.path.isfile(template_file):
            self.import_template_data()
        self.rig.build_template()

    def assemble_rig(self):
        """ Wrapper for the rig build method.
        Builds all components and then executes the asset's build code
        """
        self.rig.assemble_components()
        self.rig.build()

    def finalize_rig(self):
        """ Wrapper for the rig build method.
        Builds all components and then executes the asset's build code
        """
        self.set_stage('finalize')
        self.rig.final_touches()

    def build_rig_template(self):
        """Builds the rig template
        Sets the current stage to template and forces a new maya scene
        """
        self.set_stage('template')

        cmds.file(newFile=True, force=True)  # New scene

        self.initialize_rig()  # Instanciates rig object

        self.configure_rig()  # Stuff happens here TODO: define said stuff

        self.setup_rig_base()  # Creates base groups and root

        self.import_geo()  # Imports the geo and parents it under the rig

        self.build_template()  # Creates components templates

    def get_template_data(self):
        """ Creates a dictionary with each component's template data
        """
        template_data = {}
        for comp_name in self.rig.components.keys():
            template_data[comp_name] = \
                self.rig.components[comp_name].get_template_data()
        return template_data

    def export_template_data(self):
        """ Gets current template data, saves it in a json file
        """
        if self.stage is 'template':
            data = self.get_template_data()
            path = os.path.join(self.session_obj.paths['template'],
                                'template.json')
            with open(path, 'w') as file:
                json.dump(data, file, indent=4, sort_keys=True)
                print '### Template data succesfully extracted! ###'
        else:
            print "###Warning: Not in the template stage,"\
                "can't export template data"

    def import_template_data(self):
        """ Loads existing template data from template.json file
        """
        path = os.path.join(
            self.session_obj.paths['template'], 'template.json')
        if os.path.isfile(path):
            # Loads json into variable
            try:
                with open(path, 'r') as file:
                    template_data = json.load(file)
            except ValueError:
                raise Exception('There was a problem reading tempalte.json'
                                'check that it jas a valid json format')
            # Stores variable into rig object
            self.rig.set_template_data(template_data)
        else:
            raise Exception('No template data found')

    def build_rig(self):
        """ Builds the final rig.
        This will create a new scene and a new instance of the rig object.
                Don't use this if building step by step.
        Executed steps:
                Makes a new scene
                Creates base groups
                Imports geos
                Assembles all the rig components
                Binds geometry
                Finalizes the rig
        """
        self.set_stage('build')

        cmds.file(newFile=True, force=True)  # New scene

        self.initialize_rig()  # Instanciates rig object

        self.configure_rig()  # Stuff happens here TODO: define said stuff

        self.import_template_data()  # Load saved tempalte data

        self.setup_rig_base()  # Creates base groups and root

        self.import_geo()  # Imports the geo and parents it under the rig

        self.assemble_rig()  # Builds all the components for the rig

        self.import_rig_ctrls()  # Import saved ctrls shapes

        self.finalize_rig()  # Lock attributes, hide grps

        print '###  YUP  ###'

    def pre_publish(self):
        """ Preps the rig for publishing
        Sets most nodes to not historically interesting.
        Runs QC check
        """
        # TODO: implement
        pass

    def export_rig_ctrls_shapes(self):
        """ Creates a json file containing the shape info for the rig ctrls
        """
        # Get all ctrls under CONTROLS_GRP
        all_ls = cmds.listRelatives(self.rig.ctrls_grp,
                                    ad=1, type='transform')
        ctrls_ls = [x for x in all_ls if x.split('_')[-1] == 'CTR']

        # Store their shape information
        rig_ctrls = {}
        for ctr in ctrls_ls:
            rig_ctrls.update(controls.export_ctrl_shape(ctr))

        try:
            file_path = os.path.join(self.session_obj.paths['shapes'],
                                     'shapes.json')
            shapes_file_write = open(file_path, 'w+')
            json.dump(
                rig_ctrls,
                shapes_file_write,
                indent=4,
                sort_keys=True
            )

            shapes_file_write.close()

            print '--- Ctrls shapes exported! ---'
        except:
            print 'ERROR: Could not export ctrls shape'

    def import_rig_ctrls(self):
        """ Loads the ctrl information from shapes.json and applies to the rig
        """
        if self.stage in ['template', 'init']:
            print "###WARNING: Can't import control shapes when working on"\
                "the template o init stages of the rig"
        else:
            file_path = os.path.join(
                self.session_obj.paths['shapes'],
                'shapes.json'
            )
            if os.path.isfile(file_path):
                file_read = open(file_path, 'r')
                ctrls_data = json.load(file_read)
                for ctr in ctrls_data.keys():
                    ctr_shape_info = ctrls_data[ctr]
                    controls.set_ctrl_shape(ctr, ctr_shape_info)
            else:
                print '###WARNING: Could not find shapes.json file'
