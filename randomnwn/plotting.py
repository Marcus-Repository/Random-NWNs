#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Functions to plot nanowire networks.
# 
# Author: Marcus Kasdorf
# Date:   June 18, 2021

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def plot_NWN(NWN, intersections=True, rnd_color=False):
    """
    Plots a given nanowire network.

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

    Returns
    -------
    fig : Figure
        Figure object of the plot.

    ax : Axes
        Axes object of the plot.

    """
    fig, ax = plt.subplots(figsize=(8, 6))

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

    plt.show()
    return fig, ax


def draw_NWN(
    NWN: nx.Graph, 
    figsize: tuple = None,
    font_size: int = 8,
    sol: np.ndarray = None
):
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

    Returns
    -------
    fig : Figure
        Figure object of the plot.

    ax : Axes
        Axes object of the plot.

    """
    fig, ax = plt.subplots(figsize=figsize)

    if NWN.graph["type"] == "JDA":
        # Nodes are placed at the center of the wire
        pos = {(i,): np.array(NWN.graph["lines"][i].centroid) for i in range(NWN.graph["wire_num"])}

        # Label node voltages if sol is given, else just label as nodes numbers
        if sol is not None:
            labels = {(key,): str(round(value, 2)) for key, value in zip(range(NWN.graph["wire_num"]), sol)}
        else:
            labels = {(i,): i for i in range(NWN.graph["wire_num"])}

        nx.draw(NWN, ax=ax, node_size=40, pos=pos, labels=labels, font_size=font_size, edge_color="r")

    elif NWN.graph["type"] == "MNR":
        kwargs = {}
        if sol is not None:
            labels = {node: str(round(value, 2)) for node, value in zip(sorted(NWN.nodes()), sol)}
            kwargs.update({"labels": labels})
        else:
            kwargs.update({"with_labels": True})

        nx.draw(NWN, ax=ax, node_size=40, font_size=font_size, edge_color="r", **kwargs)

    else:
        raise ValueError("Nanowire network has invalid type.")

    plt.show()
    return fig, ax