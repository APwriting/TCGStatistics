#!/usr/bin/python

# Script for generating scry, surveil decision tree

from graphviz import Digraph
import os

# For use on different systems graphviz needs to be installed
# and the path maybe needs to be adapted:
os.environ["PATH"] += os.pathsep + r"C:\Program Files (x86)\Graphviz\bin"


tree = Digraph("Card_Tracking")

tree.attr(rankdir="TB")
tree.attr("node", shape="box", style="rounded")


# ================================================================================
# GLOBAL GRAPH SETTINGS
# ================================================================================

tree.attr(
    rankdir="TB",
    bgcolor="white",
    splines="ortho",
    nodesep="0.6",
    ranksep="0.9"
)

tree.attr(
    "node",
    shape="box",
    style="rounded,filled",
    fontname="Arial",
    fontsize="11",
    margin="0.2,0.25"
)

tree.attr(
    "edge",
    fontname="Arial",
    fontsize="10",
    arrowsize="0.7",
    penwidth="1.2",
    labelfloat="true"
)

tree.attr(
    nodesep="0.8",
    ranksep="1.0"
)


# ================================================================================
# EDGE LABEL FUNCTION
# ================================================================================

def edge_label(text):
    return (
        '<<TABLE BORDER="1" CELLBORDER="1" '
        'CELLPADDING="8" BGCOLOR="white">'
        f'<TR><TD ALIGN="CENTER">{text}</TD></TR>'
        '</TABLE>>'
    )


# ================================================================================
# START
# ================================================================================

tree.node("Start", "Card on top of deck")

tree.node("Draw", "Card draw")
tree.node("Scry", "Scry")
tree.node("Surveil", "Surveil")

tree.edge("Start", "Draw")
tree.edge("Start", "Scry")
tree.edge("Start", "Surveil")


# ================================================================================
# CARD DRAW
# ================================================================================

tree.edge(
    "Draw",
    "DrawSeen",
    label=edge_label("Card is seen")
)

tree.node(
    "DrawSeen",
    "Cards seen increases\n= cards drawn"
)

tree.edge(
    "DrawSeen",
    "Unavailable",
    xlabel=edge_label("Card is drawn")
)

tree.node(
    "Unavailable",
    "Card is no longer\navailable in deck"
)


# ================================================================================
# SCRY


tree.edge(
    "Scry",
    "Top",
    label=edge_label("On top")
)

tree.edge(
    "Scry",
    "Bottom",
    label=edge_label("Bottom")
)

tree.node("Top", "Card is seen")

tree.edge(
    "Top",
    "TopSeen"
)

tree.node(
    "TopSeen",
    "Cards seen increases"
)

tree.edge(
    "TopSeen",
    "NextDrawTop",
    label=edge_label("Next draw")
)

tree.node(
    "NextDrawTop",
    "Card is drawn"
)

tree.edge(
    "NextDrawTop",
    "TopNoIncrease"
)

tree.node(
    "TopNoIncrease",
    "Cards seen does NOT increase\n"
    "(card was already seen)"
)


tree.node(
    "Bottom",
    "Card is seen"
)

tree.edge(
    "Bottom",
    "BottomSeen"
)

tree.node(
    "BottomSeen",
    "Cards seen increases"
)

tree.edge(
    "BottomSeen",
    "NextDrawBottom",
    label=edge_label("Next draw")
)

tree.node(
    "NextDrawBottom",
    "Card is drawn"
)

tree.edge(
    "NextDrawBottom",
    "BottomIncrease"
)

tree.node(
    "BottomIncrease",
    "Cards seen increases"
)

tree.edge(
    "BottomIncrease",
    "Shuffle",
    xlabel=edge_label("Shuffle")
)

tree.node(
    "Shuffle",
    "Deck is shuffled"
)

tree.edge(
    "Shuffle",
    "AvailableAgain",
    label=edge_label("Card can be encountered again")
)

tree.node(
    "AvailableAgain",
    "Card is again available\nfor 'cards seen'"
)


# ================================================================================
# SURVEIL


tree.edge(
    "Surveil",
    "SurveilSeen",
    label=edge_label("Card is seen")
)

tree.node(
    "SurveilSeen",
    "Cards seen increases"
)

tree.edge(
    "SurveilSeen",
    "Graveyard",
    xlabel=edge_label("Put into graveyard"),
    #labeldistance="2"
    labelangle="45",
    labeldistance="10"
)

tree.edge(
    "SurveilSeen",
    "SurveilTop",
    label=edge_label("Put on top"),
    #xlp="150,200"
#    labelangle="-90",
 #   labeldistance="2.5"
)

tree.node(
    "Graveyard",
    "Card is no longer\navailable in deck"
)

tree.node(
    "SurveilTop",
    "Card remains on top"
)

tree.edge(
    "SurveilTop",
    "SurveilDraw",
    label=edge_label("Next draw")
)

tree.node(
    "SurveilDraw",
    "Card is drawn"
)

tree.edge(
    "SurveilDraw",
    "SurveilNoIncrease"
)

tree.node(
    "SurveilNoIncrease",
    "Cards seen does NOT increase\n"
    "(card was already seen)"
)


# ================================================================================
# Saving


tree.render(
    "6_8_1_plot_card_tracking_decision_tree",
    format="png",
    cleanup=True,
    view=True
)
