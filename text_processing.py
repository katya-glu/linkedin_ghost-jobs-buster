import zlib

class TextProcessor:
    # consts
    val_for_text_slicing = 4
    alphabet_str = "abcdefghijklmnopqrstuvwxyz"
    lowest_bits_num = 4
    slice_len = 2

    def __init__(self, input_text):
        self.input_text = input_text
        self.text_slices_list_for_hashing = []

    def calculate_hash_val(self, sequence):
        sequence = sequence.encode()
        hashed_chars_pair = zlib.crc32(sequence)
        hashed_chars_pair_int_4_lowest_bits = hashed_chars_pair & ((2 ** self.lowest_bits_num) - 1)
        return hashed_chars_pair_int_4_lowest_bits

    def get_indices_for_slicing(self):
        indices_for_slicing = [0]
        for index in range(0, len(self.input_text)-self.slice_len+1):
            curr_chars_pair = self.input_text[index:index+self.slice_len]
            hashed_chars_pair_int_4_lowest_bits = self.calculate_hash_val(curr_chars_pair)
            if hashed_chars_pair_int_4_lowest_bits == self.val_for_text_slicing and indices_for_slicing[-1] != index-1:
                indices_for_slicing.append(index)
        return indices_for_slicing

    def create_text_slices_list_for_hashing(self):
        indices_for_slicing = self.get_indices_for_slicing()
        for index in range(len(indices_for_slicing)):
            curr_str_index = indices_for_slicing[index]
            try:
                next_str_index = indices_for_slicing[index+1]
            except IndexError:
                next_str_index = len(self.input_text)
            curr_text_slice = self.input_text[curr_str_index:next_str_index]
            self.text_slices_list_for_hashing.append(curr_text_slice)

    # for DEBUG
    def get_sequences_for_text_slicing_val(self):
        self.sequences_list = []
        for index_1 in range(len(self.alphabet_str)):
            curr_element1 = self.alphabet_str[index_1]
            for index_2 in range(len(self.alphabet_str)):
                curr_element2 = self.alphabet_str[index_2]
                curr_seq = curr_element1 + curr_element2
                hashed_chars_pair_int_4_lowest_bits = self.calculate_hash_val(curr_seq)
                if hashed_chars_pair_int_4_lowest_bits == self.val_for_text_slicing:
                    self.sequences_list.append(curr_seq)

with open('test.txt', 'r') as f:
    text = f.read()
text_processor = TextProcessor(text)
text_processor.create_text_slices_list_for_hashing()
text_processor.get_sequences_for_text_slicing_val()

# Debug Zone
print("Slices list length", len(text_processor.text_slices_list_for_hashing))
print("Text length:", len(text))
"""for item in text_processor.text_slices_list_for_hashing:
    print(item)
"""

