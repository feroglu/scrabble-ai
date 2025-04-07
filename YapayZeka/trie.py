class Trie:
    """
    A Trie data structure for efficient word lookups.
    Used for fast word validation in the Scrabble game.
    """
    def __init__(self, word_list_file):
        """
        Initialize the Trie with words from a file.
        
        Args:
            word_list_file: Path to a file containing words, one per line
        """
        self.root = TrieNode(False)

        # Load words from file and build the trie
        with open(word_list_file, 'r', encoding='utf-8') as word_list:
            for line in word_list:
                # Process the word (convert 'i' to 'İ' and uppercase)
                word = line.strip().replace('i', 'İ').upper()
                
                # Add word to trie
                cur_node = self.root
                for letter in word:
                    if letter not in cur_node.children.keys():
                        new_node = TrieNode(False)
                        cur_node.children[letter] = new_node
                    cur_node = cur_node.children[letter]
                
                # Mark the end of a word
                cur_node.word = word
                cur_node.is_word = True
        
    def lookup_string(self, word):
        """
        Find the trie node corresponding to a word.
        
        Args:
            word: The word to look up
            
        Returns:
            The TrieNode at the end of the path for the word, or None if not found
        """
        cur_node = self.root
        for letter in word:
            if letter not in cur_node.children.keys():
                return None
            cur_node = cur_node.children[letter]
        return cur_node
    
    def is_word(self, word):
        """
        Check if a word exists in the trie.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word exists in the trie, False otherwise
        """
        final_node = self.lookup_string(word)
        if final_node is not None and final_node.is_word:
            return True
        return False


class TrieNode:
    """
    A node in the Trie data structure.
    Each node represents a letter in a word path.
    """
    def __init__(self, is_word):
        """
        Initialize a TrieNode.
        
        Args:
            is_word: Whether this node marks the end of a valid word
        """
        self.is_word = is_word  # True if this node represents the end of a valid word
        self.word = "?"         # The complete word if is_word is True
        self.children = dict()  # Dictionary mapping letters to child nodes {letter: node}