from cairo import ANTIALIAS_NONE, Matrix
from gtk.gdk import Color

from gaphas.aspect import PaintFocused, ItemPaintFocused
from gaphas.painter import HandlePainter

from rafcon.mvc.mygaphas.items.connection import ConnectionView, ScopedVariableDataFlowView, DataFlowView
from rafcon.mvc.mygaphas.items.state import StateView
from rafcon.mvc.mygaphas.utils.gap_draw_helper import get_col_rgba

from rafcon.utils import constants


class StateCornerHandlePainter(HandlePainter):
    """
    This class overwrites the default HandlePainter Class in order to be able to adjust the color of the handles.
    """

    def __init__(self, view=None):
        super(HandlePainter, self).__init__(view)

    def _draw_handles(self, state_v, cairo, opacity=None):
        view = self.view
        cairo.save()
        i2v = view.get_matrix_i2v(state_v)
        if not opacity:
            opacity = 1

        fill_color = Color(constants.STATE_RESIZE_HANDLE_FILL_COLOR)
        border_color = Color(constants.STATE_RESIZE_HANDLE_BORDER_COLOR)
        side_length = state_v.port_side_size * self.view.get_zoom_factor() / 1.5

        cairo.set_line_width(self.view.get_zoom_factor() / 4.)

        for h in state_v.corner_handles:
            # Reset the current transformation
            cairo.identity_matrix()
            cairo.set_antialias(ANTIALIAS_NONE)
            # Move to center of handle
            cairo.translate(*i2v.transform_point(*h.pos))
            cairo.rectangle(-side_length / 2., -side_length / 2., side_length, side_length)
            # Fill
            cairo.set_source_rgba(*get_col_rgba(fill_color, alpha=opacity))
            cairo.fill_preserve()
            # Border
            cairo.set_source_rgba(*get_col_rgba(border_color, alpha=opacity))
            cairo.stroke()
        cairo.restore()

    def paint(self, context):
        view = self.view
        canvas = view.canvas
        cairo = context.cairo
        # Order matters here:
        for item in canvas.sort(view.selected_items):
            if isinstance(item, StateView):
                self._draw_handles(item, cairo)
        # Draw nice opaque handles when hovering an item:
        item = view.hovered_item
        if item and item not in view.selected_items and isinstance(item, StateView):
            self._draw_handles(item, cairo, opacity=.25)
        item = view.dropzone_item
        if item and item not in view.selected_items and isinstance(item, StateView):
            self._draw_handles(item, cairo, opacity=.25, inner=True)


@PaintFocused.when_type(ConnectionView)
class LineSegmentPainter(ItemPaintFocused):
    """
    This painter draws pseudo-handles on gaphas.item.Line objects. Each
    line can be split by dragging those points, which will result in
    a new handle.

    ConnectHandleTool take care of performing the user
    interaction required for this feature.
    """

    def paint(self, context):
        view = self.view
        item = view.hovered_item
        if isinstance(item, DataFlowView):
            return
        if item and item is view.focused_item:
            cr = context.cairo
            h = item.handles()
            for h1, h2 in zip(h[:-1], h[1:]):
                p1, p2 = h1.pos, h2.pos
                cx = (p1.x + p2.x) / 2
                cy = (p1.y + p2.y) / 2
                cr.save()
                cr.identity_matrix()
                m = Matrix(*view.get_matrix_i2v(item))

                cr.set_antialias(ANTIALIAS_NONE)
                cr.translate(*m.transform_point(cx, cy))
                cr.rectangle(-3, -3, 6, 6)
                cr.set_source_rgba(0, 0, 0.5, .4)
                cr.fill_preserve()
                cr.set_source_rgba(.25, .25, .25, .6)
                cr.set_line_width(1)
                cr.stroke()
                cr.restore()