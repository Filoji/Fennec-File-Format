"""Huffmann algorithm."""

from bisect import insort
from abc import ABC, abstractmethod
from enum import Enum

class Mode(Enum):
    ENCODE = 0
    DECODE = 1

class Node(ABC):
    """Node object, basis of Leaf and Branch objects."""
    def __init__(self, score : int) -> None:
        self.score = score
    def get_score(self) -> int:
        """Return the score of the Node object."""
        return self.score
    @abstractmethod
    def create_binary_dict(self, mode : Mode = Mode.DECODE) -> dict[str, str]:
        NotImplementedError()
    @abstractmethod
    def create_header(self) -> bytes:
        NotImplementedError()

class Leaf(Node):
    """Leaf part of a binary tree
See also Branch class."""
    def __init__(self, label: str, score: int) -> None:
        self.score = score
        self.label = label
    def __str__(self) -> str:
        return f"L{self.get_label()}|{self.get_score()}"
    def __repr__(self) -> str:
        return f"<Leaf {str(self)}>"
    def get_label(self) -> str:
        """Return the label of the Leaf object."""
        return self.label
    def create_binary_dict(self, mode : Mode = Mode.DECODE) -> dict[str, str]:
        """Return a dictionnary with null string as key and label
as value."""
        if (mode == Mode.DECODE):
            return {"" : self.get_label()}
        else:
            return {self.get_label() : ""}
    def create_header(self) -> bytes:
        return len(self.get_label()).to_bytes(1, "little") + bytes(self.get_label(), "utf-8")

class Branch(Node):
    """Branch part of a binary tree
See also Leaf class."""
    def __init__(self, left: Node, right : Node) -> None:
        self.left = left
        self.right = right
        self.score = left.get_score() + right.get_score()
    def __str__(self) -> str:
        return f"B{self.get_score()}"
    def __repr__(self) -> str:
        return f"<Branch {str(self)}:{str(self.left)}:{str(self.right)}>"
    def get_children(self) -> tuple[Node, Node]:
        """Return both children of a Branch object."""
        return self.left, self.right
    def create_binary_dict(self, mode : Mode = Mode.DECODE) -> dict[str, str]:
        """Get the dictionnary created by both children and merge them
by adding 0 to the left child key, and 1 to the right one."""
        children = self.get_children()
        if (mode == Mode.DECODE):
            return {"0" + k : v for k, v in children[0].create_binary_dict(mode).items()} \
                |  {"1" + k : v for k, v in children[1].create_binary_dict(mode).items()}
        else:
            return {k : "0" + v for k, v in children[0].create_binary_dict(mode).items()} \
                |  {k : "1" + v for k, v in children[1].create_binary_dict(mode).items()}
    def create_header(self) -> bytes:
        children = self.get_children()
        return b'\x80' + children[0].create_header() + children[1].create_header()

class Decoder():
    def __init__(self, header : bytes) -> None:
        self.header = header
        self.reader = 0
    def CreateTree(self) -> Node:
        if self.header[self.reader:self.reader+1] == b'\x80':
            self.reader += 1
            return Branch(self.CreateTree(), self.CreateTree())
        else:
            length = int.from_bytes(self.header[self.reader:self.reader+1], "big")
            self.reader += length + 1
            return Leaf(self.header[self.reader - length: self.reader].decode("utf-8"), 1)

def CreateLeaves(text : str) -> list[Leaf]:
    """Create a list of Leaf objects with all uniques characters in text."""
    return [Leaf(c, text.count(c)) for c in set(text)]

def CreateTree(AllNodes : list[Node]) -> Node:
    """Create the binary tree based on a list of Node."""
    AllNodes=AllNodes[:] # Copy of AllNodes
    nodeCount = len(AllNodes)
    AllNodes.sort(key=lambda node : node.get_score())
    for _ in range(nodeCount - 1):
        insort(
            AllNodes,
            Branch(AllNodes[0], AllNodes[1]),
            key=lambda node : node.get_score()
        )
        AllNodes = AllNodes[2:]
    return AllNodes[0]

def CreateTreeFromText(text : str) -> Node:
    """Create a Node object that represents the binary tree extracted from the text."""
    return CreateTree(CreateLeaves(text))


def CreateBinaryCodeFromTree(Tree : Node, mode : Mode = Mode.DECODE) -> dict[str, str]:
    """Create a binary to label dictionary from a text."""
    return Tree.create_binary_dict(mode=mode)

def CreateBinaryCodeFromText(text : str, mode : Mode = Mode.DECODE) -> dict[str, str]:
    """Create a binary to label dictionary from a text."""
    return CreateTreeFromText(text).create_binary_dict(mode=mode)

def CreateBinaryTextFromText(text : str) -> str:
    """Create a string representation of the binary compression of the text."""
    Dict = CreateBinaryCodeFromText(text, mode = Mode.ENCODE)
    return "".join([Dict[c] for c in text])

def CreateTextFromBinaryText(binText : str, Tree : Node) -> str:
    """Create the text decompressed from the string representation of the
binary source and the binary tree."""
    Dict = CreateBinaryCodeFromTree(Tree, mode = Mode.DECODE)
    temp = ''
    res = ''
    for c in binText:
        temp += c
        if temp in Dict:
            res +=Dict[temp]
            temp = ''
    return res

if __name__ == "__main__":
    from sys import getsizeof
    filename = __file__
    with open(filename, "r") as file:
        text = file.read()
    # text = "aaaabbbbcccc"
    Tree = CreateTreeFromText(text)
    binText = CreateBinaryTextFromText(text)
    # print(Tree.create_binary_dict())
    # print(binText := CreateBinaryTextFromText(text))
    # print(CreateTextFromBinaryText(binText, Tree))
    print(f"{(textBits := getsizeof(text) * 8)} bits to {(binBits := len(binText))} bits.\
({100 - round(binBits / textBits * 100, 2)}%)")
    header = Tree.create_header()
    decoder = Decoder(header)
    newTree = decoder.CreateTree()
    print(CreateTextFromBinaryText(binText, newTree))
