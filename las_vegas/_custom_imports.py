""" Custom imports for optional packages. """

__all__ = ["tqdm"]

from warnings import warn

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(_):
        """ Local replacement for `tqdm.tqdm` when not imported. """
        warn("Consider installing `tqdm` to monitor computations.",
             stacklevel=2)
        return _
