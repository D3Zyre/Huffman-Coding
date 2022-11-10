class Node:
    def __init__(self, string_to_encode: str = None, value: str = None, count: int = None, left_node=None, right_node=None):
        self.value = value  # value that the node encodes, a single character
        self.char_counts = dict()  # only the top node has a non-empty dict, {char : count, ...}
        self.depth = 0  # gets fixed by self.shift_depth()
        self.count = count  # number of characters in tree (Node + all subNodes)
        self.left_child = left_node  # Node object for left Node, or None
        self.right_child = right_node  # Node object for right Node, or None
        self.string = string_to_encode  # only top Node has this
        self.code_string = str()  # the encoded binary string representation of self.string
        self.encoding_dict = dict()
        if string_to_encode is not None:
            self.build_tree()  # only build tree from top level
            self.shift_depth()  # assigns the correct value to each Node's depth
            self.encoding_dict = self.create_encoding()
            self.encode_string()

    def shift_depth(self, shift: int = 0):
        """
        shifts depth values for Node
        and all subnodes such that
        top Node depth is 0, all depths
        will be positive
        """
        self.depth += shift
        self.left_child: Node
        self.right_child: Node
        # recursively add the depth to all children
        if self.left_child is not None:
            self.left_child.shift_depth(shift + 1)
        if self.right_child is not None:
            self.right_child.shift_depth(shift + 1)

    def build_tree(self):
        """
        builds the Huffman tree inside
        the current node object
        """
        self.count_chars()  # we will need the dictionary for building the tree
        nodes = list()  # a list of Node objects
        for leaf in self.char_counts.keys():
            nodes.append(Node(None, leaf, self.char_counts[leaf]))
        # all children have been created (Nodes containing each character and its count)
        while len(nodes) > 1:  # repeat until there is only one tree
            # combine two smallest branches:
            # first we find the two smallest branches.
            smallest_count = int(min([leaf.count for leaf in nodes]))
            smallest_indices = list([int(i) for i, leaf in enumerate(nodes) if leaf.count == smallest_count])
            if len(smallest_indices) < 2:
                second_smallest_count = int(min([leaf.count for leaf in nodes if leaf.count != smallest_count]))
                smallest_indices.extend(list([int(i) for i, leaf in enumerate(nodes) if leaf.count == second_smallest_count]))
            # now we should have at least 2 minimum nodes
            picks = list([nodes[smallest_indices[0]], nodes[smallest_indices[1]]])  # TODO sort in a better way than the given order?
            nodes.pop(max([smallest_indices[0], smallest_indices[1]]))  # need to pop largest index first as to not shift smaller indices
            nodes.pop(min([smallest_indices[1], smallest_indices[0]]))
            nodes.append(Node(None, None, int(sum([leaf.count for leaf in picks])), picks[0], picks[1]))
            # new branch has been added, and leaves were moved to it
        # updating top node's attributes, essentially copying nodes[0] into self
        self.count = nodes[0].count
        nodes[0].string = self.string
        nodes[0].count_chars()
        self.char_counts = nodes[0].char_counts
        self.depth = nodes[0].depth
        self.left_child = nodes[0].left_child
        self.right_child = nodes[0].right_child

    def count_chars(self):
        """
        counts unique characters in self.string
        creates a dictionary with characters as keys
        and counts as values, self.counts
        """
        self.char_counts = dict()  # reset dict to be empty
        for character in self.string:
            if character in self.char_counts.keys():
                self.char_counts[character] += 1
            else:
                self.char_counts[character] = 1
        self.char_counts["EOF"] = 1

    def create_encoding(self, is_left: bool = None, is_right: bool = None, huffman_code: str = None):
        """
        creates a dictionary for the encoding of
        self.string with the huffman coding represented
        by the tree in self Node object (children and their children)
        """
        assert (is_left is True and is_right is False) or (
                is_left is False and is_right is True) or (
                is_left is None and is_right is None), """Incorrect usage 
                of is_left and is_right
                expected only one of them to be True (and the other to be False
                or both of them to be None"""
        # left = 0, right = 1
        # we go through the whole tree, similarly to how __str__ does,
        # and for each leaf node (nodes with a value) we keep track of its huffman coding
        encoding_dict = dict()  # each letter as key and corresponding binary representation as value
        current_pos_code = str(0 if is_left is True else 1)  # is_left and is_right are redundant
        if huffman_code == None:
            huffman_code = str()  # set to empty string
        else: 
            huffman_code += current_pos_code
        if self.value is not None:  # if we are on a leaf node
            encoding_dict[self.value] = huffman_code
        if self.left_child is not None:
            dict_updates: dict = self.left_child.create_encoding(is_left=True, is_right=False, huffman_code=huffman_code)
            for key in [k for k in dict_updates.keys() if k not in encoding_dict.keys()]:
                # only update values which were not already in the dict
                encoding_dict[key] = dict_updates[key]  # update encoding dict
        if self.right_child is not None:
            dict_updates: dict = self.right_child.create_encoding(is_left=False, is_right=True, huffman_code=huffman_code)
            for key in [k for k in dict_updates.keys() if k not in encoding_dict.keys()]:
                # only update values which were not already in the dict
                encoding_dict[key] = dict_updates[key]  # update encoding dict
        
        return encoding_dict  # to be updated in upper recursion levels, and final version returned to caller

    def encode_string(self):
        """
        uses self.encoding_dict and self.string
        in the top node to encode the string to self.code_string
        """
        assert (self.string is not None), "encode_string is only a method of the top node of a tree"
        huffman_code = str()
        for char in self.string:
            huffman_code += str(self.encoding_dict[char])
        huffman_code += str(self.encoding_dict["EOF"])
        self.code_string = str(huffman_code)

    def decode_string(self):
        """
        uses self.encoding_dict and self.code_string
        in the top node to decode the string to self.string
        """
        assert (len(self.code_string) > 0), "decode_string only works when self.code_string is not empty string"
        string = str()
        digit_run = str()  # the run of digits since last run was identified
        huff_codes = list(self.encoding_dict.values())  # so we don't have to call this a bunch of times
        huff_keys = list(self.encoding_dict.keys())
        for digit in self.code_string:
            digit_run += digit  # keep adding digits until a valid huffman code is found
            if digit_run in huff_codes:
                addition = huff_keys[huff_codes.index(digit_run)]
                if addition != "EOF":
                    string += huff_keys[huff_codes.index(digit_run)]  # build the string from the huffman code we found
                digit_run = str()  # since we have found the code, we reset the run
        self.string = str(string)

    def __str__(self):
        output = str((
            "\t"*self.depth + "string = {}\n" +
            "\t"*self.depth + "encoding = {}\n" +
            "\t"*self.depth + "value = {}\n" +
            "\t"*self.depth + "char counts = {}\n" +
            "\t"*self.depth + "depth = {}\n" +
            "\t"*self.depth + "count = {}\n" +
            "\t"*self.depth + "left child = [{}]\n" +
            "\t"*self.depth + "right child = [{}]\n").format(
                    self.string,
                    self.encoding_dict,
                    self.value,
                    self.char_counts,
                    self.depth,
                    self.count,
                    str(self.left_child),
                    str(self.right_child)
                    )
                )
        # by printing left/right child, we will call __str__ on them,
        # and because of their depth, it will be indented accordingly,
        # which makes it easier to read the __str__ of a Node
        return output


if __name__ == "__main__":
    a = Node("""hello world! this is a very long string, hopefully it doesn't take my code too long to generate the tree for this,
    let's add a few special characters as well for fun: !@#$%^&*()\n\t -\r""")
    b = Node("hello world!")
    print(a.code_string)
    print(a.string)  # before decoding, original string
    a.decode_string()
    print(a.string)  # after decoding, decoded string
