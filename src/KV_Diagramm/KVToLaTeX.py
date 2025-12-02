from .Dataclasses.KVData import KVData
from .Dataclasses.Edge import Edge

KARNAUGH_TEMPLATE: str = """
\\karnaughmap{{{num_vars}}}{{{title}}}%
{{{my_vars}}}
{{{vals}}}
{{{ovals}}}
"""

OVAL_TEMPLATE: str = """\\put({x},{y}){{\\oval({delta_x},{delta_y}){side}}}"""

COLOR_ITEM: str = "\\textcolor{{{color}}}{{{item}}}"

def color_item(item: str, color: str) -> str:
    return COLOR_ITEM.format(color=color, item=item)

def __calc_position(low: float, high: float, low_bool: bool, high_bool: bool) -> float:
    ret: list[float] = []
    if low_bool:
        ret.append(low)
    if high_bool:
        ret.append(high)
    return sum(ret) / len(ret)

def get_kv_string(kvdata: KVData, title: str) -> str:
    """
    Get the Karnaugh map string representation.
    """
    retval = KARNAUGH_TEMPLATE

    ovals: list[str] = []
    oval: list[str] = []

    for marking in kvdata.markings:
        col = marking.latex_color
        for markingdata in marking.drawables:
            x1 = markingdata.x1
            y1 = markingdata.y1
            x2 = markingdata.x2
            y2 = markingdata.y2
            edges = markingdata.edges

            
            x = __calc_position(x1, x2, Edge.RIGHT in edges, Edge.LEFT in edges)
            y = __calc_position(y1, y2, Edge.BOTTOM in edges, Edge.TOP in edges)

            y = kvdata.height - y

            delta_x = (x2 - x1) * (2 if not (Edge.LEFT in edges and Edge.RIGHT in edges) else 1) - 0.1
            delta_y = (y2 - y1) * (2 if not (Edge.TOP in edges and Edge.BOTTOM in edges) else 1) - 0.1
            side = f"[{edges.kv_str()}]" if ~edges else ""

            oval.append(OVAL_TEMPLATE.format(
                x=x,
                y=y,
                delta_x=delta_x,
                delta_y=delta_y,
                side=side
            ))
        if oval:
            ovals.append(color_item("\n".join(oval), col))
        oval.clear()

    return retval.format(
        num_vars=len(kvdata.vars),
        title=title,
        my_vars="".join(
            map(lambda x: "{{{}}}".format(x), reversed(kvdata.vars))),
        vals="".join(kvdata.vals),
        ovals="%\n".join(ovals)
    )
