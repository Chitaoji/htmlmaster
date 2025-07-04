"""
Contains the core of htmlmaster: HTMLTableMaker, HTMLTreeMaker, etc.

NOTE: this module is private. All functions and objects are available in the main
`htmlmaster` namespace - use that instead.

"""

from typing import Self

from .abc import HTMLMaker

__all__ = ["HTMLTreeMaker", "HTMLTableMaker"]


class HTMLTreeMaker(HTMLMaker):
    """
    Make an html tree.

    Parameters
    ----------
    value : str, optional
        Value of child node, by default None.
    licls : str, optional
        \\<li\\> class name of the current node, by default "m" ("m" for
        "main").
    ulcls : str | None, optional
        \\<ul\\> class name of the current node, by default `licls`.
    maincls : str, optional
        Main class name, by default "main".
    style : str | None, optional
        Css style, by default None.
    level_open : int, optional
        Specifies how many levels of the tree are defaultly set open, by
        default 3.

    """

    def __init__(
        self,
        value: str | None = None,
        /,
        licls: str = "m",
        ulcls: str | None = None,
        maincls: str = "main",
        style: str | None = None,
        level_open: int = 3,
    ) -> None:
        super().__init__(maincls, style)
        self.__val = value
        self.__licls = licls
        self.__ulcls = licls if ulcls is None else ulcls
        self.__level_open = level_open
        self.__children: list[Self] = []

    def add(
        self,
        value: str | Self,
        /,
        licls: str | None = None,
        ulcls: str | None = None,
    ) -> None:
        """
        Add a child node.

        Parameters
        ----------
        value : str | Self | list[Self]
            Node value or an instance of the child node.
        licls : str | None, optional
            \\<li\\> class name, by default None.
        ulcls : str | None, optional
            \\<ul\\> class name, by default None.

        Returns
        -------
        Self
            The new node.

        """
        if isinstance(value, str):
            self.__children.append(
                self.__class__(value, "m" if licls is None else licls, ulcls)
            )
        else:
            if not isinstance(value, self.__class__):
                raise TypeError(
                    f"object of type {value.__class__.__name__} is not allowed "
                    "to be a child node"
                )
            if licls:
                value.setcls(licls, ulcls)
            self.__children.append(value)

    def discard(self, index: int, /) -> None:
        """Discard the n-th child node."""
        self.__children = self.__children[:index] + self.__children[index:]

    def get(self, index: int, /) -> Self:
        """Get the n-th child node."""
        return self.__children[index]

    def setval(self, value: str, /) -> None:
        """Set the node value."""
        self.__val = value

    def getval(self) -> str | None:
        """Get the node value."""
        return self.__val

    def setcls(self, licls: str, ulcls: str | None = None, /) -> None:
        """Set the node class names."""
        self.__licls = licls
        self.__ulcls = licls if ulcls is None else ulcls

    def getcls(self) -> tuple[str, str]:
        """Get the node class names."""
        return self.__licls, self.__ulcls

    def setlevel(self, level: int, /) -> None:
        """Set the open level."""
        self.__level_open = level

    def getlevel(self) -> int:
        """Get the open level."""
        return self.__level_open

    def has_child(self) -> bool:
        """Return whether there is a child node."""
        return bool(self.__children)

    def make(self) -> str:
        """
        Make a string representation of the html tree.

        Returns
        -------
        str
            String representation.

        """
        maincls = self.get_maincls()
        style = self.getstyle("").format(maincls)
        return f'{style}<ul class="{maincls}">\n{self.make_node(0)}\n</ul>'

    def make_node(self, level: int, /) -> str:
        """Make a string representation of the current node."""
        if not self.__children:
            return f'<li class="{self.__licls}"><span>{self.__val}</span></li>'
        children_str = "\n".join(x.make_node(level + 1) for x in self.__children)
        if self.__val is None:
            return children_str
        details_open = " open" if level < self.__level_open else ""
        return (
            f'<li class="{self.__licls}"><details{details_open}><summary>{self.__val}'
            f'</summary>\n<ul class="{self.__ulcls}">\n{children_str}\n</ul>\n'
            "</details></li>"
        )


class HTMLTableMaker(HTMLMaker):
    """
    Make an HTML table.

    Parameters
    ----------
    index : list
        Table index.
    columns : list
        Table columns.
    maincls : str, optional
        Main class name, by default "main".
    style : str | None, optional
        Css style, by default None.

    """

    def __init__(
        self,
        index: list,
        columns: list,
        maincls: str = "main",
        style: str | None = None,
    ):
        super().__init__(maincls, style)
        self.__index = index
        self.__columns = columns
        self.__data = [
            ["" for _ in range(len(self.__columns))] for _ in range(len(self.__index))
        ]

    def __getitem__(self, __key: tuple[int, int]) -> str:
        return self.__data[__key[0]][__key[1]]

    def __setitem__(self, __key: tuple[int, int], __value: str) -> None:
        self.__data[__key[0]][__key[1]] = __value

    def make(self) -> str:
        """
        Make a string representation of the html table.

        Returns
        -------
        str
            String representation.

        """
        style = self.getstyle("").format(self.get_maincls())
        thead = "\n".join(f"<th>{x}</th>" for x in self.__columns)
        rows = []
        for x in self.__data:
            row = "</td>\n<td>".join(x)
            rows.append("<tr>\n<td>" + row + "</td>\n</tr>\n")
        tbody = "".join(rows)
        return (
            f'{style}<table class="{self.get_maincls()}">\n<thead>\n'
            f"<tr>\n{thead}\n</tr>\n</thead>\n<tbody>\n{tbody}</tbody>\n</table>"
        )
