from matplotlib.layout_engine import LayoutEngine


class FixedAxesLayoutEngine(LayoutEngine):
    _colorbar_gridspec = False
    _adjust_compatible = False

    def execute(self, fig):
        pass


fixed_axes = FixedAxesLayoutEngine()
