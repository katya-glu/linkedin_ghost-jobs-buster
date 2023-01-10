import zlib
import os
import pickle


class TextProcessor:
    # consts
    val_for_text_slicing = 4
    alphabet_str = "abcdefghijklmnopqrstuvwxyz"
    lowest_bits_num = 4
    slice_len = 3
    full_hash_val = True
    partial_hash_val = False
    db_dict_path = 'job_listings_db'

    def __init__(self, input_text):
        self.input_text = input_text
        self.text_slices_list_for_hashing = []
        self.hashed_slices_list = []
        self.data_storage_dict = {}
        self.load_db_dict()

    def calculate_hash_val(self, sequence, full_hash_val):
        sequence = sequence.encode()
        hashed_chars_sequence = zlib.crc32(sequence)
        if full_hash_val:
            return hashed_chars_sequence

        hashed_chars_pair_int_4_lowest_bits = hashed_chars_sequence & ((2 ** self.lowest_bits_num) - 1)
        return hashed_chars_pair_int_4_lowest_bits


    def get_indices_for_slicing(self):
        indices_for_slicing = [0]
        for index in range(0, len(self.input_text)-self.slice_len+1):
            curr_chars_pair = self.input_text[index:index+self.slice_len]
            hashed_chars_seq_lowest_bits = self.calculate_hash_val(curr_chars_pair, self.partial_hash_val)
            if hashed_chars_seq_lowest_bits == self.val_for_text_slicing and indices_for_slicing[-1] <= index-self.slice_len+1:
                indices_for_slicing.append(index)
        print(indices_for_slicing)

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


    def create_hashed_slices_list(self):
        for text_slice in self.text_slices_list_for_hashing:
            curr_slice_hash_val = self.calculate_hash_val(text_slice, self.full_hash_val)
            self.hashed_slices_list.append(curr_slice_hash_val)


    def load_db_dict(self):
        if os.path.exists(self.db_dict_path):   # TODO: consider using try except
            with open(self.db_dict_path, 'rb') as db_file:
                self.data_storage_dict = pickle.load(db_file)


    def update_db_entry(self, company_name, job_listing):   # job_listing is an object
        if company_name in self.data_storage_dict:
            self.data_storage_dict[company_name].append(job_listing)
        else:
            self.data_storage_dict[company_name] = [job_listing]

        with open(self.db_dict_path, "wb") as score_file:       # TODO: check if possible
            pickle.dump(self.data_storage_dict, score_file)


    # for DEBUG
    def get_sequences_for_text_slicing_val(self):
        self.sequences_list = []
        for index_1 in range(len(self.alphabet_str)):
            curr_element1 = self.alphabet_str[index_1]
            for index_2 in range(len(self.alphabet_str)):
                curr_element2 = self.alphabet_str[index_2]
                curr_seq = curr_element1 + curr_element2
                hashed_chars_seq_lowest_bits = self.calculate_hash_val(curr_seq, self.partial_hash_val)
                if hashed_chars_seq_lowest_bits == self.val_for_text_slicing:
                    self.sequences_list.append(curr_seq)


with open('test.txt', 'r') as f:
    text = f.read()
text_processor = TextProcessor(text)
text_processor.create_text_slices_list_for_hashing()
text_processor.get_sequences_for_text_slicing_val()
text_processor.create_hashed_slices_list()
#text_processor.update_db_entry("intel", "hash")
new = TextProcessor("bbbb")
print(new.data_storage_dict)

# Debug Zone
print("Slices list length", len(text_processor.text_slices_list_for_hashing))
print("Text length:", len(text))
"""for item in text_processor.hashed_slices_list:
    print(item)"""

