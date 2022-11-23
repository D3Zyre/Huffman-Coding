import Huffman_tree

choice = input("Encode (E) or Decode? (D): ")
if choice.lower() == "e":
    node = Huffman_tree.Node(input("String to encode to file:\n"))
    ratio = node.write_to_file(input("File to write to:\n"))
    print("compression ratio: {}\nfile written successfully".format(ratio))
elif choice.lower() == "d":
    node = Huffman_tree.Node()
    node.read_from_file(input("File to decode:\n"))
    print(node.get_string())
else:
    print("bad input, try again")