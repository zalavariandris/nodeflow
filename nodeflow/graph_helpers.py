from typing import Dict, Any, List

Graph = Dict[Any, List[Any]]

def dfs(G:Graph, start):
    """
    Depth First Search
    iterative version
    source: https://stackoverflow.com/questions/47192626/deceptively-simple-implementation-of-topological-sorting-in-python
    """
    seen = set()  # efficient set to look up nodes in
    path = []     # there was no good reason for this to be an argument in your code
    q = [start]
    while q:
        v = q.pop()   # no reason not to pop from the end, where it's fast
        if v not in seen:
            seen.add(v)
            path.append(v)
            q.extend(G[v]) # this will add the nodes in a slightly different order
                               # if you want the same order, use reversed(graph[v])

    return path


def topological_sort(G:Graph, root: Any):
    """
    Sort Nodes such that every node comes before it dependants
    iterative version
    source: https://stackoverflow.com/questions/47192626/deceptively-simple-implementation-of-topological-sorting-in-python
    """
    seen = set()
    stack:List[Node] = []
    order:List[Node] = []

    q:List[Node] = [root]
    while q:
        v = q.pop()
        if v not in seen:
            seen.add(v) # no need to append to path any more
            q.extend(G[v])

            while stack and v not in G[stack[-1]]: # new stuff here!
                order.append(stack.pop())
            stack.append(v)

    return stack + order[::-1]   # new return value!


def display(G:Graph):
    for node, sources in G.items():
        print(node,sources)

if __name__ == "__main__":
    G:Graph = {
        "a": ["b", "a"],
        "b": []
    }

    display(G)
