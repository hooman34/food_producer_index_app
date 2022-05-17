import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .log import get_logger

logger = get_logger(__name__)

def _plot_data(plot_type, plot_settings):
    """
    Create a plotly figure. The input should be a list of list.
    The inner list should be [dataset, x_column, y_column]

    Args:
        plot_type1(str): type of graph. line or bar
        plot_settings(list): [[dataset, x_column, y_column], [dataset, x_column, y_column], ...]

    Returns:
        fig(plotly.graph_objs._figure.Figure): plot
    """
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    if plot_type=='line':
        for setting in plot_settings:
            trace = _create_trace(plot_type, setting[0], setting[1], setting[2])
            fig.add_trace(trace)
    elif plot_type=='bar':
        logger.info("bar graph not implemented")
        return None
    else:
        logger.info("specified graph type is not implemented")
        return None

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    return fig


def _create_trace(plot_type, data, x, y):
    """
    create trace, which will be a part of the plot
    """
    if plot_type == 'bar':
        trace = go.Bar(x=data[x],
                       y=data[y],
                       name=y)
    if plot_type == 'line':
        trace = go.Scatter(x=data[x],
                           y=data[y],
                           name=y)
    return trace
