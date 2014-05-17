"""Process Troupe Data

This takes in an ODS file of troupe applications to the Hideout Theatre,
collates them into a single dictionary of troupes->troupe data, and then
converts that to a set of files for the AIC Wiki.

Command line usage:
$ python ProcessTroupeData.py filename
"""


def load_troupe_info(filename):
    from ODSReader import ODSReader
    doc = ODSReader(filename)
    troupeDatabase = doc.getSheet("avail")
    return troupeDatabase[1:]  # remove headers


def is_url(string):
    return 'www' in string or 'http' in string


def set_first_valid_url(data, field_name, new_string):
    if not field_name in data and is_url(new_string):
        data[field_name] = new_string


def collect_valid_urls(data, field_name, new_string):
    if is_url(new_string):
        new_item_set = set([new_string])
        if field_name in data:
            data[field_name] = data[field_name] | new_item_set
        else:
            data[field_name] = new_item_set


def set_longest_string(data, field_name, new_string):
    if not new_string:
        return False
    if field_name in data and len(data[field_name]) > len(new_string):
        return False
    data[field_name] = new_string
    return True


def collate_cast(data, field_name, new_string):
    import re
    if not new_string:
        return
    # Handle AND
    new_string = re.sub(r'\sAND\s', ' & ', new_string, flags=re.IGNORECASE)
    new_cast_set = set(re.split('[&,\n]', new_string))  # set of split-up names
    new_cast_set = {name.strip() for name in new_cast_set}  # strip whitespace
    new_cast_set = {name for name in new_cast_set if name}  # kill empty

    if field_name in data:
        data[field_name] = data[field_name] | new_cast_set
    else:
        data[field_name] = new_cast_set


def set_start_year(data, field_name, new_string):
    if not new_string:
        return

    if not field_name in data or int(data[field_name]) > int(new_string):
        data[field_name] = new_string


def set_end_year(data, field_name, new_string):
    if not new_string:
        return

    if not field_name in data or int(data[field_name]) < int(new_string):
        data[field_name] = new_string


def set_yes_no_field(data, field_name, new_string):
    if not new_string:
        return
    if new_string.find('n') != -1:  # "no"
        return
    if new_string.find('m') != -1:  # "maybe"
        return
    if new_string.find('y') == -1:  # no "yes"
        return
    data[field_name] = 'y'


def process_row(troupe_dict, row):
    if row[1] in troupe_dict:
        data = troupe_dict[row[1]]
    else:
        data = {}

    set_first_valid_url(data, 'site', row[2])
    set_first_valid_url(data, 'photo', row[19])
    collect_valid_urls(data, 'video', row[20])

    if set_longest_string(data, 'blurb', row[7]):
        data['blurb_year'] = row[22]
    if set_longest_string(data, 'deal', row[13]):
        data['deal_year'] = row[22]

    collate_cast(data, 'cast', row[4])

    set_start_year(data, 'start_year', row[22])
    set_end_year(data, 'end_year', row[22])

    set_yes_no_field(data, 'performed_before', row[11])

    return data


def process_troupe_data(filename):
    table = load_troupe_info(filename)
    troupe_dict = {}
    for row in table:
        if row[1]:
            troupe_dict[row[1]] = process_row(troupe_dict, row)
    return troupe_dict


def load_template_files():
    import os
    import glob
    templates = {}
    saved_path = os.getcwd()
    os.chdir(".\\templates")
    for file_name in glob.glob("*_template.wiki"):
        field_name = file_name.replace("_template.wiki", "")
        file_handle = open(file_name)
        templates[field_name] = file_handle.read()
    os.chdir(saved_path)
    return templates


def create_troupe_page(troupe_name, troupe_data, templates):
    troupe_data['name'] = troupe_name
    troupe_data['blurb_section'] = ""
    troupe_data['deal_section'] = ""
    troupe_data['summary_section'] = ""
    troupe_data['cast_list'] = ""
    troupe_data['media_section'] = ""
    troupe_data['more_info_section'] = ""

    show_summary = False

    if 'blurb' in troupe_data and troupe_data['blurb']:
        show_summary = True
        troupe_data['blurb_section'] = \
            templates['blurb'].format(**troupe_data)

    if 'deal' in troupe_data and troupe_data['deal']:
        show_summary = True
        troupe_data['deal_section'] = \
            templates['deal'].format(**troupe_data)

    if show_summary:
        troupe_data['summary_section'] = \
            templates['summary'].format(**troupe_data)

    if 'site' in troupe_data and troupe_data['site']:
        troupe_data['more_info_section'] = \
            templates['more_info'].format(**troupe_data)

    if 'cast' in troupe_data:
        troupe_data['cast_list'] = \
            "{{ Unbulleted list | [[" + \
            "]] | [[".join(sorted(troupe_data['cast'])) + "]] }}"

    troupe_data['is_or_was'] = "was"

    if not 'start_year' in troupe_data:
        troupe_data['start_year'] = "???"
    if not 'end_year' in troupe_data:
        troupe_data['end_year'] = "???"

    if troupe_data['end_year'] == '2014':
        troupe_data['end_year'] = "Present"
        troupe_data['is_or_was'] = "is"

    if 'video' in troupe_data:
        troupe_data['video_list'] = \
            "\n".join({"* [" + url + " Video #" + str(index + 1) + "]"
                       for index, url in enumerate(troupe_data['video'])})
        troupe_data['media_section'] = \
            templates['media'].format(**troupe_data)

    troupe_data['other_categories'] = ""

    if troupe_data['is_or_was'] == 'is':
        troupe_data['other_categories'] += "\n[[Category:Active]]"
    if 'cast' in troupe_data and len(troupe_data['cast']) == 2:
        troupe_data['other_categories'] += "\n[[Category:Duos]]"

    return templates["troupe"].format(**troupe_data)


# direct access to the page generator, for testing
def create_test_page(troupe_name, troupe_data):
    templates = load_template_files()
    # print create_troupe_page(troupe_name, troupe_data, templates)
    return create_troupe_page(troupe_name, troupe_data, templates)


def create_troupe_pages(filename):
    troupe_dict = process_troupe_data(filename)
    templates = load_template_files()
    pages_dict={troupe_name: create_troupe_page(troupe_name, troupe_data, templates)
        for troupe_name, troupe_data in troupe_dict.iteritems()}
    return(pages_dict)


def troupe_name_to_file_name(troupe_name, subdir, extension):
    return ".\\output\\" + subdir + "\\" +\
        "".join(x for x in troupe_name if x.isalnum()) +\
        extension


def download_troupe_pics(filename):
    troupe_dict = process_troupe_data(filename)
    print troupe_dict
    for troupe_name, troupe_data in troupe_dict.iteritems():
        import os
        import urllib
        _, file_extension = os.path.splitext(troupe_data['photo'])
        file_name = troupe_name_to_file_name(troupe_name, "pics",
                                             file_extension)
        urllib.urlretrieve(troupe_data['photo'], file_name)


def output_troupe_pages(filename):
    pages_dict = create_troupe_pages(filename)
    for troupe_name, troupe_page in pages_dict.iteritems():
        file_name = troupe_name_to_file_name(troupe_name, "pages",
                                             ".wiki")
        # save troupe page to file name
        with open(file_name, "w") as text_file:
            text_file.write(troupe_page)

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        print output_troupe_pages(sys.argv[1])
    else:
        print __doc__
