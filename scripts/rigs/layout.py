from CARF.scripts.rigs import rig
reload(rig)
class Layout(rig.Rig):
    """docstring for Layout"""
    def __init__(self, builder, asset_name):
        super(Layout, self).__init__(builder, asset_name)

    def register(self, component):
        super(Layout, self).register()

    def build_template(self):
        super(Layout, self).build_template()

    def build(self):
        super(Layout, self).build()
        self.root.ctrls[0].constrain(
            target = self.builder.geo_grp,
            constraint_type = 'parent'
        )