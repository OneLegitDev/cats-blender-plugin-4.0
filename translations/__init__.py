# Thanks to https://www.thegrove3d.com/learn/how-to-translate-a-blender-addon/ for the idea

import os
import csv
import pathlib
import importlib
import addon_utils
from bpy.app.translations import locale

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
translations_dir = os.path.join(str(main_dir), "translations")
translations_file = os.path.join(translations_dir, "translations.csv")

# Get package name, important for relative imports
package_name = ''
for mod in addon_utils.modules():
    if mod.bl_info['name'] == 'Cats Blender Plugin':
        package_name = mod.__name__

languages = []
dictionary = {}
dictionary_en = {}
lang_module = None
lang_en_module = None


def load_translations():
    global dictionary
    dictionary = {}

    with open (translations_file, 'r', encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for row in csv_reader:
            text = row.get(locale)
            if not text:
                text = row.get('en_US')
            dictionary[row['name']] = text


def t(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    output = dictionary.get(phrase)
    if output is None:
        print('Warning: Unknown phrase: ' + phrase)
        return phrase

    return output.format(*args, **kwargs)


def load_translations_old():
    global languages, dictionary, dictionary_en, lang_module, lang_en_module
    languages = []
    dictionary = {}
    dictionary_en = {}

    # Get all supported languages in translations folder
    for file in os.listdir(os.path.dirname(__file__)):
        lang_name = os.path.splitext(file)[0]
        if len(lang_name) == 5 and lang_name[2] == '_' and lang_name != 'en_US':
            languages.append(lang_name)

    # Import the correct language dictionary
    if locale in languages:
        if lang_module:
            importlib.reload(lang_module)
        lang_module = importlib.import_module(package_name + '.translations.' + locale)
        dictionary = lang_module.dictionary

    if lang_en_module:
        importlib.reload(lang_en_module)
    lang_en_module = importlib.import_module(package_name + '.translations.en_US')
    dictionary_en = lang_en_module.dictionary
    # print('LOADED TRANSLATIONS')
    # print(dictionary_en.get('CreditsPanel.descContributors2'))


def t_old(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    output = dictionary.get(phrase)
    if output is None:
        output = dictionary_en.get(phrase)
    if output is None:
        print('Warning: Unknown phrase: ' + phrase)
        return phrase

    if isinstance(output, list):
        new_list = []
        for string in output:
            new_list.append(string.format(*args, **kwargs))
        return new_list
    elif not isinstance(output, str):
        return output
    else:
        return output.format(*args, **kwargs)


def check_missing_translations():
    lang_dicts = []
    for language in languages:
        lang = importlib.import_module(package_name + '.translations.' + language)
        lang_dicts.append(lang.dictionary)

    for key, value in dictionary_en.items():
        if value is None:
            print('Translations en_US: Value missing for key: ' + key)

        for lang_dict in lang_dicts:
            if lang_dict.get(key) is None:
                print('Translations ' + lang_dict.get('name') + ': Value missing for key: ' + key)

    del lang_dicts


def output_translations():
    load_translations_old()

    lang_dicts = []
    for language in languages:
        lang = importlib.import_module(package_name + '.translations.' + language)
        lang_dicts.append(lang.dictionary)

    lines = []
    separator = ','

    def encase_str(string):
        return '"' + str(string).replace('"', '""') + '"'

    for key, value in dictionary_en.items():
        if type(value) is list:
            value = '\n'.join(value)

        # print(key, separator, value)
        line = key + separator + encase_str(value)

        for dict_trans in lang_dicts:
            trans = dict_trans.get(key)

            if type(trans) is list:
                trans = '\n'.join(trans)

            if trans == value or None:
                trans = ''

            # print(key, separator, trans)
            line += separator + encase_str(trans)

        lines.append(line + '\n')

    with open(translations_file, 'w', encoding="utf8") as outfile:
        outfile.writelines(lines)


# output_translations()
# load_translations_old()
load_translations()