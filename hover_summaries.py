def add_hover_summaries(figure, summaries):
    tooltips = {}

    for axes, summary in summaries.items():
        tooltip = axes.annotate(
            summary,
            xy=(0, 0),
            xycoords="data",
            xytext=(14, 14),
            textcoords="offset points",
            fontsize=8,
            color="#172033",
            ha="left",
            va="bottom",
            bbox={
                "boxstyle": "round,pad=0.45",
                "facecolor": "white",
                "edgecolor": "#64748b",
                "alpha": 0.97,
            },
            zorder=100,
            annotation_clip=False,
        )
        tooltip.set_visible(False)
        tooltip.set_wrap(True)
        tooltip.set_clip_on(False)
        tooltips[axes] = tooltip

    def update_tooltip(event):
        active_axes = event.inaxes if event.inaxes in tooltips else None
        redraw = False

        for axes, tooltip in tooltips.items():
            if axes is active_axes and event.xdata is not None and event.ydata is not None:
                tooltip.xy = (event.xdata, event.ydata)
                on_right = event.x > axes.bbox.x0 + axes.bbox.width * 0.65
                on_top = event.y > axes.bbox.y0 + axes.bbox.height * 0.65
                tooltip.set_position((-14 if on_right else 14, -14 if on_top else 14))
                tooltip.set_horizontalalignment("right" if on_right else "left")
                tooltip.set_verticalalignment("top" if on_top else "bottom")
                tooltip.set_visible(True)
                redraw = True
            elif tooltip.get_visible():
                tooltip.set_visible(False)
                redraw = True

        if redraw:
            figure.canvas.draw_idle()

    figure.canvas.mpl_connect("motion_notify_event", update_tooltip)
    return tooltips