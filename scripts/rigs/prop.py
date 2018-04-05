from CARF.scripts.rigs import rig
reload(rig)
class Prop(rig.Rig):
	"""docstring for Prop"""
	def __init__(self, builder, asset_name):
		super(Prop, self).__init__(builder, asset_name)

	def register(self, component):
		super(Prop, self).register()

	def build_template(self):
		super(Prop, self).build_template()

	def build(self):
		super(Prop, self).build()
		self.root_ctr.constrain(
            target = self.builder.geo_grp,
            constraint_type = 'parent'
        )
