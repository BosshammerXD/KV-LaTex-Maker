from tkinter import StringVar
from .KVData import KVData


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


def get_kv_string(kvdata: KVData) -> str:
    """
    Get the Karnaugh map string representation.
    """
    retval = KARNAUGH_TEMPLATE

    # TODO: Generator for markings

    ovals: list[str] = []
    oval: list[str] = []

    for marking in kvdata.markings:
        col = marking.latex_color
        if isinstance(col, StringVar):
            col = col.get()
        for markingdata in marking.drawables:
            x1 = markingdata.x1
            y1 = markingdata.y1
            x2 = markingdata.x2
            y2 = markingdata.y2
            openings = markingdata.openings

            x = x1 if "r" in openings else (
                x2 + 1 if "l" in openings else (x2 + x1) / 2 + 0.5)
            y = y1 - \
                1 if "b" in openings else (
                    y2 if "t" in openings else (y2 + y1) / 2 - 0.5)

            print(f"X: {x}, Y: {y}")

            y = kvdata.dimensions[1] - y - 1

            delta_x = (x2 - x1 + 1) * \
                (2 if "l" in openings or "r" in openings else 1) - 0.1
            delta_y = (y2 - y1 + 1) * \
                (2 if "t" in openings or "b" in openings else 1) - 0.1

            side = f"[{openings}]" if openings else ""

            oval.append(OVAL_TEMPLATE.format(
                x=x,
                y=y,
                delta_x=delta_x,
                delta_y=delta_y,
                side=side
            ))

        ovals.append(color_item("\n".join(oval), col))
        oval.clear()

    return retval. format(
        num_vars=len(kvdata.vars),
        title=kvdata.title.get(),
        my_vars="".join(
            map(lambda x: "{{{}}}".format(x), reversed(kvdata.vars))),
        vals="".join(kvdata.vals.get()),
        ovals="%\n".join(ovals)
    )
