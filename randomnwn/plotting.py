#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Functions to plot nanowire networks.
# 
# Author: Marcus Kasdorf
# Date:   July 8, 2021

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl

from typing import Tuple
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .calculations import get_edge_indices


def plot_NWN(
    NWN: nx.Graph, 
    intersections: bool = True, 
    rnd_color: bool = False,
    scaled: bool = False,
    grid: bool = True,
    xlabel: str = "",
    ylabel: str = "",
) -> Tuple[Figure, Axes]:
    """
    Plots a given nanowire network and returns the figure and axes.

    Parameters
    ----------
    NWN : Graph
        Nanowire network to plot.

    intersections : bool, optional
        Whether or not to scatter plot the interesections as well.
        Defaults to true.

    rnd_color : bool, optional
        Whether or not to randomize the colors of the plotted lines.
        Defaults to false.

    scaled: bool, optional
        Whether or not to scale the plot by the characteristic values of the
        given nanowire network. Defaults to False.

    grid: bool, optional
        Grid lines on plot. Defaults to true.

    xlabel: str, optional
        x label string.

    ylabel: str, optional
        y label string.

    Returns
    -------
    fig : Figure
        Figure object of the plot.

    ax : Axes
        Axes object of the plot.

    """
    fig, ax = plt.subplots(figsize=(8, 6))
    l0 = NWN.graph["units"]["l0"]

    # Plot intersection plots if required
    if intersections:
        ax.scatter(
            *np.array([(point.x, point.y) for point in NWN.graph["loc"].values()]).T, 
            zorder=10, s=5, c="blue"
        )

    # Defaults to blue and pink lines, else random colors are used.
    if rnd_color:
        for i in range(NWN.graph["wire_num"]):
            ax.plot(*np.array(NWN.graph["lines"][i]).T)
    else:
        for i in range(NWN.graph["wire_num"]):
            if (i,) in NWN.graph["electrode_list"]:
                ax.plot(*np.array(NWN.graph["lines"][i]).T, c="xkcd:light blue")
            else:
                ax.plot(*np.array(NWN.graph["lines"][i]).T, c="pink")

    # Scale axes according to the characteristic values
    if scaled:
        ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{x * l0:.3g}")
        )
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, pos: f"{y * l0:.3g}")
        )

    # Other attributes
    if grid: 
        ax.grid(alpha=0.25)
    if xlabel: 
        ax.set_xlabel(xlabel)
    if ylabel: 
        ax.set_ylabel(ylabel)

    plt.show()
    return fig, ax


def draw_NWN(
    NWN: nx.Graph, 
    figsize: tuple = None,
    font_size: int = 8,
    sol: np.ndarray = None,
    fmt: str = ".2f",
    color_edges: str = "same",
    cmap = plt.cm.RdYlBu_r,
) -> Tuple[Figure, Axes]:
    """
    Draw the given nanowire network as a networkx graph.

    Parameters
    ----------
    NNW : Graph
        Nanowire network to draw.

    figsize : tuple, optional
        Figure size to be passed to `plt.subplots`.

    font_size : int, optional
        Font size to be passed to `nx.draw`.

    sol : ndarray, optional
        If supplied, these values will be display as node labels
        instead of the names of the nodes.

    fmt : str, optional
        String formatting for node labels. Only used if sol is passed.
        Default: ".2f".

    color_edges : str, {"same", "linear", "log"}
        Edge color formatting. When set, edges are colored according to
        the current passing through them. Defaults to "same", that is,
        all edges are colored the same.

    cmap : colormap, optional
        Matplotlib color map to use for the edges.

    tight : bool, optional
        Matplotlib tight layout.

    Returns
    -------
    fig : Figure
        Figure object of the plot.

    ax : Axes
        Axes object of the plot.

    """
    fig, ax = plt.subplots(figsize=figsize)

    if NWN.graph["type"] == "JDA":
        kwargs = dict()

        # Nodes are placed at the center of the wire
        kwargs.update({
            "pos": {(i,): np.array(NWN.graph["lines"][i].centroid) 
                for i in range(NWN.graph["wire_num"])}
        })

        # Label node voltages if sol is given, else just label as nodes numbers
        if sol is not None:
            kwargs.update({
                "labels": {(key,): f"{value:{fmt}}" 
                    for key, value in zip(range(NWN.graph["wire_num"]), sol)}
            })
        else:
            kwargs.update({
                "labels": {(i,): i for i in range(NWN.graph["wire_num"])}
            })

        # Add edges colors corresponding to the current
        if sol is not None and color_edges != "same":
            # Get edges and conductances
            edges, G = zip(*nx.get_edge_attributes(NWN, "conductance").items())

            # Find edges indices
            start_nodes, end_nodes = get_edge_indices(NWN, edges)

            # Find current through each edges
            v0 = sol[start_nodes]
            v1 = sol[end_nodes]
            V_delta = np.abs(v0 - v1)
            edges_I = V_delta * G

            # Log if desired
            if color_edges == "log":
                edges_I[edges_I < 1e-8] = np.nan
                edges_I = np.log10(edges_I)

            # Add a colorbar to the network plot
            norm = mpl.colors.Normalize(
                vmin=np.min(edges_I), vmax=np.max(edges_I))

            cax = fig.add_axes([0.95, 0.2, 0.02, 0.6])
            cb = mpl.colorbar.ColorbarBase(cax, norm=norm, cmap=cmap)
            if color_edges == "log":
                cb.set_label("log10 of Current (arb. units)")
            else:
                cb.set_label("Current (arb. units)")

            kwargs.update({
                "edgelist": edges, "edge_color": edges_I, "edge_cmap": cmap
            })
            
        else:
            kwargs.update({"edge_color": "r"})

        # Add node formatting
        kwargs.update({"ax": ax, "font_size": font_size, "node_size": 40})

        nx.draw(NWN, **kwargs)

    elif NWN.graph["type"] == "MNR":
        kwargs = {}
        if sol is not None:
            labels = {node: f"{value:{fmt}}" for node, value in zip(sorted(NWN.nodes()), sol)}
            kwargs.update({"labels": labels})
        else:
            kwargs.update({"with_labels": True})

        nx.draw(NWN, ax=ax, node_size=40, font_size=font_size, edge_color="r", **kwargs)

    else:
        raise ValueError("Nanowire network has invalid type.")

    plt.show()
    return fig, ax

