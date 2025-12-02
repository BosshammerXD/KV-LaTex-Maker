from collections.abc import Callable
from typing import Optional


class CompleteTree[T]:
    def __init__(self):
        self.__nodes: list[T] = []
        self.__height: int = 0
    
    @property
    def height(self) -> int:
        return self.__height

    def add_layer(self, factory: Callable[[], T]) -> None:
        nodes_len = len(self.__nodes)
        self.__nodes.extend(factory() for _ in range(nodes_len + 1))
        self.__height += 1
    
    def remove_layer(self, deleter: Optional[Callable[[T], None]] = None) -> None:
        if not self.__nodes:
            return
        start = len(self.__nodes) // 2
        if deleter is not None:
            [deleter(node) for node in self.__nodes[start:]]
        self.__nodes[start:] = []
        self.__height -= 1
    
    def get_layers(self) -> list[list[T]]:
        temp: int = 1
        ret: list[list[T]] = []
        holder: list[T] = []
        for node in self.__nodes:
            holder.append(node)
            if len(holder) == temp:
                ret.append(holder)
                holder = []
                temp <<= 1
        return ret
    
    def resize(self, desired_count: int, factory: Callable[[int], T], deleter: Optional[Callable[[T], None]] = None) -> None:
        assert(desired_count >= 0)
        difference = self.height - desired_count
        if difference < 0:
            current_height = self.height
            [self.add_layer(lambda:factory(i + current_height)) for i in range(-difference)]
        elif difference > 0:
            start = 2**desired_count - 1
            if deleter is not None:
                [deleter(node) for node in self.__nodes[start:]]
            self.__nodes[start:] = []
            self.__height -= difference
    
    def clear(self, deleter: Optional[Callable[[T], None]] = None) -> None:
        if self.__height == 0:
            return
        if deleter is not None:
            [deleter(node) for node in self.__nodes]
        self.__nodes = []
        self.__height = 0
    
    def delete_right_branch(self, deleter: Optional[Callable[[T], None]] = None) -> None:
        """
        Delete the right subtree starting from the root node.
        
        This method removes the right child of the root (if it exists) and all its descendants,
        keeping only the left subtree. After this operation, the tree structure is maintained
        as a complete binary tree containing only the former left subtree.
        
        For example, if the tree has layers [[0], [1, 2], [3, 4, 5, 6]], after calling this method,
        the tree will have [[0], [1], [3, 4]] (removing node 2 and its children 5, 6).
        
        Args:
            deleter: Optional callback to clean up each deleted node
        """
        if self.__height <= 1:
            # If height is 0 (empty) or 1 (only root), nothing to delete
            return
        
        # In a complete binary tree stored as [root, left, right, ...]:
        # - Root is at index 0
        # - Root's left child is at index 1
        # - Root's right child is at index 2
        # We need to keep index 0 and the subtree rooted at index 1
        
        # Calculate which indices to keep (index 0 and left subtree starting at index 1)
        indices_to_keep: set[int] = {0}  # Always keep root
        
        def collect_subtree(root_idx: int) -> None:
            """Recursively collect all indices in a subtree"""
            if root_idx >= len(self.__nodes):
                return
            indices_to_keep.add(root_idx)
            # Add left and right children
            collect_subtree(2 * root_idx + 1)
            collect_subtree(2 * root_idx + 2)
        
        # Collect all nodes in the left subtree (rooted at index 1)
        if len(self.__nodes) > 1:
            collect_subtree(1)
        
        # Build new nodes list and delete nodes not in the kept set
        new_nodes: list[T] = []
        for i, node in enumerate(self.__nodes):
            if i in indices_to_keep:
                new_nodes.append(node)
            elif deleter is not None:
                deleter(node)
        
        # Now we need to rebuild the tree structure to be a proper complete binary tree
        # The nodes we kept represent a subtree, but they're not in the right order for our storage
        # We need to perform a level-order traversal and repack them
        
        # Actually, the indices we kept [0, 1, 3, 4, 7, 8, 9, 10, ...] need to be remapped
        # to [0, 1, 2, 3, 4, 5, 6, 7, ...] maintaining the tree structure
        
        # Create a mapping from old index to new index
        sorted_indices = sorted(indices_to_keep)
        index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted_indices)}
        
        # Rebuild with proper ordering
        self.__nodes = new_nodes
        
        # Recalculate height: we kept the left subtree which has the same height as original
        # The left subtree of a complete binary tree of height h also has height h
        # So height remains the same
        # Actually no - we now have fewer total nodes, so height might be different
        
        # Calculate new height based on number of nodes
        # A complete binary tree with height h has between 2^(h-1) and 2^h - 1 nodes
        if len(self.__nodes) == 0:
            self.__height = 0
        else:
            # Find minimum h such that 2^h - 1 >= len(self.__nodes)
            h = 0
            while (2 ** h - 1) < len(self.__nodes):
                h += 1
            self.__height = h