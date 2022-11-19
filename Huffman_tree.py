def justify_to_8(num):
    """
    return the lowest multiple of 8 that is greater than or equal to num
    """
    just = int(num//8)*8+8
    if num % 8 == 0:
        just -= 8
    return just

class Node:
    def __init__(self, string_to_encode: str = None, value: str = None, count: int = None, left_node=None, right_node=None):
        self.__value = value  # value that the node encodes, a single character
        self.__char_counts = dict()  # only the top node has a non-empty dict, {char : count, ...}
        self.__depth = 0  # gets fixed by self.__shift_depth()
        self.__count = count  # number of characters in tree (Node + all subNodes)
        self.__left_child = left_node  # Node object for left Node, or None
        self.__right_child = right_node  # Node object for right Node, or None
        self.__string = string_to_encode  # only top Node has this
        self.__code_string = str()  # the encoded binary string representation of self.__string
        self.__encoding_dict = dict()
        if string_to_encode is not None:
            self.__build_tree()  # only build tree from top level
            self.__shift_depth()  # assigns the correct value to each Node's depth
            self.__encoding_dict = self.__create_encoding()
            self.__encode_string()

    def set_string(self, string_to_encode: str):
        """
        changes the string and rebuilds tree and all
        """
        self.__string = string_to_encode
        self.__build_tree()
        self.__shift_depth()
        self.__encoding_dict = self.__create_encoding()
        self.__encode_string()
    
    def get_string(self):
        """
        returns self.__string
        """
        return self.__string
    
    def get_huffman_code(self):
        """
        returns self.__code_string
        """
        return self.__code_string
    
    def get_encoding_dict(self):
        """
        returns the huffman encoding pairs as a dict
        self.__encoding_dict
        """
        return self.__encoding_dict

    def __shift_depth(self, shift: int = 0):
        """
        shifts depth values for Node
        and all subnodes such that
        top Node depth is 0, all depths
        will be positive
        """
        self.__depth += shift
        self.__left_child: Node
        self.__right_child: Node
        # recursively add the depth to all children
        if self.__left_child is not None:
            self.__left_child.__shift_depth(shift + 1)
        if self.__right_child is not None:
            self.__right_child.__shift_depth(shift + 1)

    def __build_tree(self):
        """
        builds the Huffman tree inside
        the current node object
        """
        self.__count_chars()  # we will need the dictionary for building the tree
        nodes = list()  # a list of Node objects
        for leaf in self.__char_counts.keys():
            nodes.append(Node(None, leaf, self.__char_counts[leaf]))
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
        self.__count = nodes[0].count
        nodes[0].string = self.__string
        nodes[0].__count_chars()
        self.__char_counts = nodes[0].char_counts
        self.__depth = nodes[0].depth
        self.__left_child = nodes[0].left_child
        self.__right_child = nodes[0].right_child

    def __count_chars(self):
        """
        counts unique characters in self.__string
        creates a dictionary with characters as keys
        and counts as values, self.__counts
        """
        self.__char_counts = dict()  # reset dict to be empty
        for character in self.__string:
            if character in self.__char_counts.keys():
                self.__char_counts[character] += 1
            else:
                self.__char_counts[character] = 1
        self.__char_counts["EOF"] = 1

    def __create_encoding(self, is_left: bool = None, is_right: bool = None, huffman_code: str = None):
        """
        creates a dictionary for the encoding of
        self.__string with the huffman coding represented
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
        if huffman_code is None:
            huffman_code = str()  # set to empty string
        else:
            huffman_code += current_pos_code
        if self.__value is not None:  # if we are on a leaf node
            encoding_dict[self.__value] = huffman_code
        if self.__left_child is not None:
            dict_updates: dict = self.__left_child.__create_encoding(is_left=True, is_right=False, huffman_code=huffman_code)
            for key in [k for k in dict_updates.keys() if k not in encoding_dict.keys()]:
                # only update values which were not already in the dict
                encoding_dict[key] = dict_updates[key]  # update encoding dict
        if self.__right_child is not None:
            dict_updates: dict = self.__right_child.__create_encoding(is_left=False, is_right=True, huffman_code=huffman_code)
            for key in [k for k in dict_updates.keys() if k not in encoding_dict.keys()]:
                # only update values which were not already in the dict
                encoding_dict[key] = dict_updates[key]  # update encoding dict

        return encoding_dict  # to be updated in upper recursion levels, and final version returned to caller

    def __encode_string(self):
        """
        uses self.__encoding_dict and self.__string
        in the top node to encode the string to self.__code_string
        """
        assert (self.__string is not None), "__encode_string is only a method of the top node of a tree"
        assert (self.__string.count("\0") == 0), "NULL character not allowed in string"
        huffman_code = str()
        for char in self.__string:
            huffman_code += str(self.__encoding_dict[char])
        huffman_code += str(self.__encoding_dict["EOF"])
        self.__code_string = str(huffman_code)

    def decode_string(self):
        """
        uses self.__encoding_dict and self.__code_string
        in the top node to decode the string to self.__string
        """
        assert (len(self.__code_string) > 0), "decode_string only works when self.__code_string is not empty string"
        string = str()
        digit_run = str()  # the run of digits since last run was identified
        huff_codes = list(self.__encoding_dict.values())  # so we don't have to call this a bunch of times
        huff_keys = list(self.__encoding_dict.keys())
        addition = str()
        for digit in self.__code_string:
            digit_run += digit  # keep adding digits until a valid huffman code is found
            if digit_run in huff_codes:
                addition = huff_keys[huff_codes.index(digit_run)]
                if addition != "EOF":
                    string += huff_keys[huff_codes.index(digit_run)]  # build the string from the huffman code we found
                digit_run = str()  # since we have found the code, we reset the run
            if addition == "EOF":
                break
        self.__string = str(string)

    def write_to_file(self, file):
        """
        writes the huffman encoding tree
        and the encoded string in binary format
        to file
        returns efficiency (float, <1 is good)
        """
        binary_string = str()  # this will be written to the file, in binary
        # first we need to convert the huffman tree into a binary string
        # options:
        # 1. we write the tree as a list of lists of lists etc. which
        # could be converted by the decoder back to a dict of characters to encodings
        # 2. we just write the dict of characters to encodings
        # let's figure out which one is shorter
        # example for 1:
        # [a, [b, [[c, d], [e, [f, g]]]]]
        # or in a more compact form:
        # [a[b[[cd][e[fg]]]]]
        # the same thing but with method 2:
        # a=0, b=10, c=1100, d=1101, e=1110, f=11110, g=11111
        # more compact:
        # a0b10c1100d1101e1110f11110g11111
        # even more compact
        # a0b2c12d13e14f30g31 <<< NOTE this is the chosen formatting
        # <character><number><character><number><...> the decoder will be able to recognize this
        # well, it appears that for this specific example at least, both formats are equivalent in size
        # for simplicity, let's use option 2, as it is simple to encode and decode
        total_length = int()
        for key in self.__encoding_dict.keys():
            binary_string += str(key) + str(self.__encoding_dict[key])
        binary_string += "\0\n"  # add NULL and newline to signify the end of the tree (NULL isn't allowed in the string)
        total_length += len(binary_string)
        # this part of the string, we will want to write in text mode,
        # the rest will be in binary mode
        with open(file, "w") as f:  # creates/overwrites the file
            f.write(binary_string)
        with open(file, "ab") as f:  # appends to the same file, now in binary mode
            b_array = list()
            code_string = self.__code_string.ljust(justify_to_8(len(self.__code_string)), "0")  # pad with 0s at the end to encode as bytes
            for i in range(0, len(code_string), 8):
                b_array.append(int(code_string[i:i+8], base=2))
            binary_string = bytearray(b_array)
            f.write(binary_string)
        total_length += len(binary_string)
        efficiency = total_length/len(self.__string)

        return efficiency

    def read_from_file(self, file):
        """
        reads the huffman encoding tree
        and the encoded string in binary format
        from file
        """
        with open(file, "r", errors="ignore") as f:  # the beginning of the file was written in text mode
            string = str()
            while string.count("\0") == 0:  # NULL marks the end of the huffman tree and the start of the encoded bytes
                string += f.readline()
        string = string.rstrip("\0\n")
        with open(file, "rb") as f:  # and the rest was written in bytes mode
            encoded_string = bytearray(f.read()).split(bytes("\0", "UTF-8"))[-1]
        encoded_string = encoded_string.lstrip(bytes("\r\n", "UTF-8"))
        tree_dict = dict()
        # rebuilding tree_dict from file data
        current_string = str()
        current_number = str()
        last_char_number = False
        for char in string:
            if not char.isnumeric():
                if last_char_number:
                    tree_dict[current_string] = current_number
                    current_string = str()
                    current_number = str()
                current_string += char
                last_char_number = False
            else:
                last_char_number = True
                current_number += char
        tree_dict[current_string] = current_number  # add the last entry
        # now tree_dict will match exactly the self.__encoding_dict that was used to encode
        binary_string = bin(int.from_bytes(encoded_string, "big"))[2:]
        binary_string = binary_string.rjust(justify_to_8(len(binary_string)), "0")
        # update attributes in Node and decode string
        self.__code_string = binary_string
        self.__encoding_dict = tree_dict
        self.decode_string()

    def __str__(self):
        output = str((
            "\t"*self.__depth + "string = {}\n" +
            "\t"*self.__depth + "encoding = {}\n" +
            "\t"*self.__depth + "value = {}\n" +
            "\t"*self.__depth + "char counts = {}\n" +
            "\t"*self.__depth + "depth = {}\n" +
            "\t"*self.__depth + "count = {}\n" +
            "\t"*self.__depth + "left child = [{}]\n" +
            "\t"*self.__depth + "right child = [{}]\n").format(
                    self.__string,
                    self.__encoding_dict,
                    self.__value,
                    self.__char_counts,
                    self.__depth,
                    self.__count,
                    str(self.__left_child),
                    str(self.__right_child)
                    )
                )
        # by printing left/right child, we will call __str__ on them,
        # and because of their depth, it will be indented accordingly,
        # which makes it easier to read the __str__ of a Node
        return output


if __name__ == "__main__":
    a = Node("""hello world! this is a very long string,
    let's add a few special characters as well for fun: !@#$%^&*()""")
    b = Node("hello world!")
    c = Node("test\ntesting\ntesteroo\ntesterino")
    z = a
    print(z.string)  # before decoding, original string
    #print(z.encoding_dict)
    #print(z.code_string)
    print("compression ratio (lower is better):", z.write_to_file("test.txt"))
    z.read_from_file("test.txt")
    print(z.string)  # after encoding, writing, reading, and decoding
