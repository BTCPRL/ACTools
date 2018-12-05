from CARF.scripts.components import static
from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import transforms as trans

class Cog(static.Static):
    """Cog component
    Has one ctrl, which could have tweak ctrls
    """
    # def __init__(self, common_args, component_args={}):
    # 	super(Cog, self).__init__(common_args)
    
    def configure(self):
        """
        """
        super(Cog, self).configure()	
        # Default COG values
        
        # Common
        if 'position' not in self.common_args:
            self.position = [0,20,0,0,0,0]
        
        # Behavior
        self.tweak_ctrls = 1
        
        # Interface
        self.ctr_shape = 'arrow_cross'
