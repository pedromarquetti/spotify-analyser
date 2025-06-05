from matplotlib.axes import Axes


def add_text(x, y, ax: Axes, text, ha='center', va='center'):
    """Helper function for adding text to graph"""
    ax.text(x, y, text, color='white', ha=ha, va=va)
