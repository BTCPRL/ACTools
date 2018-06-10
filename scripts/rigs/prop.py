from CARF.scripts.rigs import rig
reload(rig)
class Prop(rig.Rig):
	"""docstring for Prop"""
	def __init__(self, builder, asset_name):
		super(Prop, self).__init__(builder, asset_name)
		
		self.cog = self.register(
			common_args = {
				'name': 'cog',
				'side': 'M',
				'type' : 'cog',
				'driver': 'M_root.M_root_CTR',
				'scale_driver': 'M_root.M_root_CTR'
			}
		)

	def build(self):
		self.cog.cog_jnt.constrain(
            target = self.builder.geo_grp,
            constraint_type = 'parent'
        )
		self.cog.cog_jnt.constrain(
            target = self.builder.geo_grp,
            constraint_type = 'scale'
        )