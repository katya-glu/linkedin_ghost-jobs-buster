import zlib
import os
import pickle
import crawler
import time

class TextProcessor:
    # consts
    val_for_text_slicing = 4
    alphabet_str = "abcdefghijklmnopqrstuvwxyz"
    lowest_bits_num = 4
    slice_len = 3
    full_hash_val = True
    partial_hash_val = False
    approximate_match_db_dict_path = 'job_listings_db'
    exact_match_db_dict_path = 'job_listings_exact_match_db'
    approximate_match_db_dict_val = True
    exact_match_db_dict_val = False

    def __init__(self):
        self.input_text = ""    # TODO: change to input list with job listings
        self.text_slices_list_for_hashing = []
        self.hashed_slices_list = []
        self.approximate_match_db_dict = {}
        self.exact_match_db_dict = {}
        self.load_db_dict(self.approximate_match_db_dict, self.approximate_match_db_dict_path)
        self.load_db_dict(self.exact_match_db_dict, self.exact_match_db_dict_path)


        # DEBUG
        self.debug_linkedin_list = []


    def calculate_hash_val(self, sequence, full_hash_val):
        sequence = sequence.encode()
        hashed_chars_sequence = zlib.crc32(sequence)
        if full_hash_val:
            return hashed_chars_sequence

        hashed_chars_pair_int_4_lowest_bits = hashed_chars_sequence & ((2 ** self.lowest_bits_num) - 1)
        return hashed_chars_pair_int_4_lowest_bits


    def get_indices_for_slicing(self, input_text):
        indices_for_slicing = [0]
        for index in range(0, len(input_text)-self.slice_len+1):
            curr_chars_pair = self.input_text[index:index+self.slice_len]
            hashed_chars_seq_lowest_bits = self.calculate_hash_val(curr_chars_pair, self.partial_hash_val)
            if hashed_chars_seq_lowest_bits == self.val_for_text_slicing and indices_for_slicing[-1] <= index-self.slice_len+1:
                indices_for_slicing.append(index)
        #print("DEBUG: indices_for_slicing: ", indices_for_slicing)

        return indices_for_slicing


    def create_text_slices_list_for_hashing(self, input_text):
        indices_for_slicing = self.get_indices_for_slicing(input_text)
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


    def load_db_dict(self, db_dict, db_dict_path):
        # func loads db_dict from pickle file
        if os.path.exists(db_dict_path):   # TODO: consider using try except
            with open(db_dict_path, 'rb') as db_file:
                db_dict = pickle.load(db_file)


    def update_db_entry(self, update_approximate_db, company_name, job_title, job_details1, job_details2, job_description):  # TODO: debug func
        # func updates desired db_dict - exact db is updated with EntryExactDB object,
        if update_approximate_db:
            self.create_text_slices_list_for_hashing(job_description)
            self.create_hashed_slices_list()
            if company_name in self.approximate_match_db_dict:
                self.approximate_match_db_dict[company_name].append(self.hashed_slices_list)
            else:
                self.approximate_match_db_dict[company_name] = [self.hashed_slices_list]
            with open(self.approximate_match_db_dict_path, "wb") as db_dict_file:  # TODO: check if possible, check if needed to separate
                pickle.dump(self.approximate_match_db_dict, db_dict_file)

        else:       # update exact db
            job_title_hash = self.calculate_hash_val(job_title, self.full_hash_val)
            job_description_hash = self.calculate_hash_val(job_description, self.full_hash_val)
            job_title_description_hash_tuple = (job_title_hash, job_description_hash)
            job_exact_db_entry = EntryExactDB(job_title, job_details1, job_details2, job_description, job_title_description_hash_tuple)
            if company_name in self.exact_match_db_dict:
                self.exact_match_db_dict[company_name].append(job_exact_db_entry)
            else:
                self.exact_match_db_dict[company_name] = [job_exact_db_entry]

            with open(self.exact_match_db_dict_path, "wb") as db_dict_file:       # TODO: check if possible, check if needed to separate
                pickle.dump(self.exact_match_db_dict, db_dict_file)


    def update_list_of_entries_in_exact_match_db(self, list_of_db_entries):
        for index in range(len(list_of_db_entries)):
            curr_element = list_of_db_entries[index]
            curr_job_title = curr_element[0].split('\n', 1)[0]
            curr_company_name = curr_element[0].split('\n', 2)[1]
            curr_job_details1 = curr_element[0]                     # TODO: find better var name
            curr_job_details2 = curr_element[1]                     # TODO: find better var name
            curr_job_description = curr_element[2]
            self.update_db_entry(self.exact_match_db_dict_val, curr_company_name, curr_job_title, curr_job_details1,
                                 curr_job_details2, curr_job_description)


    def save_db_dict_to_pickle_file(self, db_dict, db_dict_path):
        # func saves db_dict to pickle file
        if not os.path.exists(db_dict_path):  # TODO: consider using try except
            with open(db_dict_path, 'wb') as db_dict_file:
                pickle.dump(db_dict, db_dict_file)


    """DEBUG SECTION"""
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


    def save_debug_list_to_pickle_file(self, debug_list, filename):
        with open(filename, "wb") as debug_list_file:
            pickle.dump(debug_list, debug_list_file)


    def load_debug_list(self):
        # func loads debug_list from pickle file
        if os.path.exists("linkedin_list_for_debug"):   # TODO: consider using try except
            with open("linkedin_list_for_debug", 'rb') as debug_list_file:
                self.debug_linkedin_list = pickle.load(debug_list_file)


    def print_job_entry(self, entry):
        job_title = entry.split('\n', 1)[0]
        company_name = entry.split('\n', 2)[1]
        print("company name is:", company_name)
        print("job title is:", job_title)
        print("\n")


class EntryExactDB:
    # class contains attributes of exact DB entries - title, details, description and calculated
    # job_title_description_hash_tuple that is used for fast comparison between new job and jobs already in DB
    def __init__(self, job_title, job_details1, job_details2, job_description,  job_title_description_hash_tuple):
        self.job_title = job_title
        self.job_details1 = job_details1
        self.job_details2 = job_details2
        self.job_description = job_description
        self.title_and_total_hash_tuple = job_title_description_hash_tuple


if __name__ == "__main__":
    with open('test.txt', 'r') as f:
        text = f.read()
    text_processor = TextProcessor()
    #text_processor.create_text_slices_list_for_hashing()
    text_processor.get_sequences_for_text_slicing_val()
    text_processor.create_hashed_slices_list()
    #print("DEBUG: testing load from pickle file:   data_storage_dict: ", new.data_storage_dict)

    # run crawler to create debug Linkedin list
    if not os.path.exists("linkedin_list_for_debug"):
        new_crawler = crawler.Crawler()
        new_crawler.login()
        new_crawler.is_security_check()
        if not new_crawler.security_check_on_login:
            new_crawler.job_search()
            time.sleep(2)
            new_crawler.filter()
            time.sleep(2)
            new_crawler.find_offers()
        else:
            print("Security check active..")        # TODO: add code that deals with security check
            time.sleep(10)
            new_crawler.pass_security_check()

        if len(new_crawler.jobs_with_description) > 0:      # no security check and some jobs were found
            text_processor.save_debug_list_to_pickle_file(new_crawler.jobs_with_description, "linkedin_list_for_debug")

    text_processor.load_debug_list()
    print("Jobs num in debug_list is: ", len(text_processor.debug_linkedin_list))
    #print("Jobs in debug_list:\n ", text_processor.debug_linkedin_list)
    #print(text_processor.debug_linkedin_list[:5])
    text_processor.update_list_of_entries_in_exact_match_db(text_processor.debug_linkedin_list[:5])
    print("\nexact_match_db_dict: ", text_processor.exact_match_db_dict)
    print("\nLen of exact_match_db_dict: ", len(text_processor.exact_match_db_dict))

    # Debug Zone
    #print("DEBUG: Slices list length", len(text_processor.text_slices_list_for_hashing))
    #print("DEBUG: Text length:", len(text))

