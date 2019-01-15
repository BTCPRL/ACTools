from CARF.scripts.rigs import rig
class Prop(rig.Rig):
	"""docstring for Prop"""
	def __init__(self, asset_name):
		super(Prop, self).__init__(asset_name)
		
		self.cog = self.add_component(
			component_type='cog',
			common_args = {
				'name': 'cog',
				'side': 'M',
				'driver': 'M_root_JNT',
				'scale_driver': 'M_root_JNT',
				'settings_driver':'M_cog_JNT'
			}
		)

	def build(self):
		self.cog.m_cog_jnt.constrain(
            target = self.geo_grp,
            constraint_type = 'parent'
        )
		self.cog.m_cog_jnt.constrain(
            target = self.geo_grp,
            constraint_type = 'scale'
        )