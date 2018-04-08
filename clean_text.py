# remove repeating text
# remove title repeated in description
# strip tags
# https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all

import csv
import json
import load_data
import os
import sys
import constants
import re

NO_TEXT_TAGS = "code", "noformat"
ESCAPE_TAGS = "color", "quote", "anchor", "panel"
ESCAPE_STRINGS = "\\r", "\\n", "\\t", "\\f", "\\v", "\"", "\\\\", "h1. ", "h2. ", "h3. ", "h4. ", "h5. ", "h6. "
LINK_STARTERS = r"\#", r"\^", r"http\:\/\/", r"https\:\/\/", r"malto\:", r"file\:", r"\~"

def escape_tags_and_content(text, tags):

    for tag in tags:
        regex_matching_tag = re.compile("\{%s(.*?)\}(.*?)\{%s\}" % (tag, tag), re.DOTALL)
        text = re.sub(regex_matching_tag, "", text)

    return text

def escape_tags(text, tags):

    for tag in tags:
        text = re.sub("\{%s(.*?)\}" % tag, "", text)

    return text

def escape_strings(text, escape_strings):

    for escape_string in escape_strings:
        text = text.replace(escape_string, " ")

    return text

def escape_links(text, link_starters):

    for link_starter in link_starters:
        text = re.sub("\[(.*?\\|)?%s(.*?)\]" % link_starter, "", text)

    return text

def escape_stack_trace(text):

    text = re.sub(r"(at(\s+(\S+\s+){1,2}?)){3,}", "", text)

    return text

def escape_hex_character_codes(text):

    return re.sub(r"\\x\w\w", "", text)

def escape_non_alphanum(text):

    return re.sub(r"[^a-zA-Z1-9\']", " ", text)

def escape_odd_spaces(text):
    
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text

def calculate_alpha_density(text):

    total = len(text)
    alphas = len(re.findall("[a-zA-Z]", text))
    spaces = len(re.findall("\s", text))
    symnums = total - (spaces + alphas)

    apos = text.count(r"\\'") * 3
    alphas = alphas + apos
    symnums = symnums - apos
    
    return alphas / (symnums + alphas) if (symnums + alphas) > 0 else 0

def clean(text):

    text = escape_tags_and_content(text, NO_TEXT_TAGS)
    text = escape_tags(text, ESCAPE_TAGS)
    text = escape_strings(text, ESCAPE_STRINGS)
    text = escape_links(text, LINK_STARTERS)
    text = escape_stack_trace(text)
    text = escape_hex_character_codes(text)
    text = escape_non_alphanum(text)
    text = escape_odd_spaces(text)
    return text

def load_file(filename):

    if not os.path.isfile(filename):
        print("File %s does not exist" % filename)
        return

    data = load_data.load_csv(filename, constants.FIELD_KEYS)

    if data is None:
        print("Skipping cleaning %s because it does not consist any data" % filename)
        return

    return data

def get_clean_content(filename):

    data = load_file(filename)
    if data is None:
        return

    print("Cleaning %s" % filename)
    for i, datapoint in enumerate(data):
        
        if constants.SUMMARY_FIELD in datapoint:
            datapoint[constants.SUMMARY_FIELD] = clean(datapoint[constants.SUMMARY_FIELD])
        
        if constants.DESCRIPTION_FIELD in datapoint:
            
            clean_description = clean(datapoint[constants.DESCRIPTION_FIELD])
            
            if clean_description != None and clean_description != "":
                datapoint[constants.DESCRIPTION_FIELD] = clean_description
                datapoint["alpha"] = int("%.0f" % (calculate_alpha_density(datapoint[constants.DESCRIPTION_FIELD]) * 100))
            else:
                datapoint.pop(constants.DESCRIPTION_FIELD, None)

        if (i + 1) % 1000 == 0 or (i + 1) == len(data):
            percentage = (i + 1) / len(data) * 100
            print("%d (%.2f%%) of %d records cleaned" % (i + 1, len(data), percentage))

    return sorted(data, key = lambda datapoint: datapoint["alpha"] if "alpha" in datapoint else 101)

def save_content(filename, data):

    with open(filename, 'w') as file:
        json.dump(data, file, indent=constants.JSON_INDENT)

def clean_text(datasets):

    if len(datasets) == 0:
        datasets = [entry for entry in os.listdir(constants.DATA_FOLDER) if os.path.isdir("%s/%s" % (constants.DATA_FOLDER, entry))]
    else:
        for dataset in datasets:
            if not os.path.isdir("%s/%s" % (constants.DATA_FOLDER, dataset)):
                print("Dataset %s does not exist" % dataset)
                datasets.remove(dataset)
    
    if len(datasets) > 0:
        print("Cleaning text in the following dataset%s:" % ("s" if len(datasets) > 1 else ""), ", ".join(datasets))
    else:
        print("No datasets selected")
        return        

    for dataset_name in datasets:

        labeled_data_filename = constants.get_labeled_raw_filename(dataset_name)
        labeled_cleaned_data_filename = constants.get_labeled_cleaned_filename(dataset_name)
        clean_labeled_content = get_clean_content(labeled_data_filename)
        save_content(labeled_cleaned_data_filename, clean_labeled_content)

        unlabeled_data_filename = constants.get_unlabeled_raw_filename(dataset_name)
        unlabeled_cleaned_data_filename = constants.get_unlabeled_cleaned_filename(dataset_name)
        clean_unlabeled_content = get_clean_content(unlabeled_data_filename)
        save_content(unlabeled_cleaned_data_filename, clean_unlabeled_content)

datasets = sys.argv[1:]
clean_text(datasets)