---
path: fr/Translation
---

# Traduire le logiciel
Il existe plusieurs fichiers de traduction, qui s’ouvrent avec [Poedit](https://poedit.net/). Les fichiers .qm se trouvent dans src/qualcoder/GUI. Les fichiers .po se trouvent dans src/qualcoder. Il est possible de mettre à jour le fichier langue en faisant ```python rebuild_lang.py --update``` et de compiler en faisant ```python rebuild_lang.py --compile```.

Glossaire concernant la traduction, afin d’avoir une cohérence dans la traduction :

- Speakers : Intervenant⋅es
- Coder : Codeur·euse
- Case : cas
- Transcript : Retranscription
- Counts : occurrences
- Automatic coding : autocodage
- Mark : Surligner
- Prompt AI : [Instruction](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000050185686)
- Stop words: mots vides
- Codebook : Grille de codage
- Red weak : Protanomalie
- Red blind : Protanopie
- Green weak : Deutéranomalie
- Green blind : Deutéranopie
- Pie charts : Diagrammes circulaires
- Bar charts :  Graphique à barres







---------------

Notes for creating language files



=================================


List_of_ISO_639-1_codes


2 letter codes for different languages





For Qt translations files: .ts to .qm


=====================================


Installs:


sudo apt install python-setuptools


sudo apt install qttools5-dev-tools  # for project.pro to convert multiple files at once


sudo apt install qtcreator


sudo apt -y install linguist-qt6


sudo apt install pyqt6-dev-tools





In directory qualcoder/GUI 


Need a .pro file  in the qualcoder/GUI directory


run:


pylupdate5 project.pro -noobsolete





Note pylupdate6 does not work well, it replaces with blank entries, instead of drawing from existing ts files.





This helper file for this: rebuild_lang.py will updat all the placeholders fo rthe languages in both po and ts files. Run from the Qualcder-master efolder.





ts files are released as app_name.qm 


Release is placed in qualcoder/locale/name/name.qm





#####################################





Strings in python code need to be translated.


https://docs.python.org/3/library/gettext.html#internationalizing-your-programs-and-modules





Code in the main module:


install gettext


At the start:


lang = gettext.translation('qualcoder', localedir='/GUI/', languages=['fr'])


lang.install()








# Install poedit


sudo apt install poedit





In terminal, run these scripts from the qualcoder folder to prepare the po files:


Note this is replaced with the above helper file.





-d is default output name    e.g. fr


-j option to join existing file


# note dont use -j lang.po on first creating a po file





For individual update to po files see below example for Deutsch:





xgettext -d de -j de.po __main__.py add_attribute.py add_item_name.py ai_chat.py ai_llm.py ai_prompts.py ai_search_dialog.py ai_vectorstore.py attributes.py case_file_manager.py cases.py code_color_scheme.py code_text.py code_in_all_files.py code_organiser.py code_pdf.py codebook.py color_selector.py confirm_delete.py edit_textfile.py helpers.py import_survey.py import_twitter_data.py information.py journals.py manage_files.py manage_links.py manage_references.py memo.py merge_projects.py move_resize_rectangle.py pseudonyms.py refi.py report_attributes.py report_codes.py report_code_summary.py report_codes_by_segments.py report_compare_coder_file.py report_cooccurrence.py report_exact_matches.py report_file_summary.py report_relations.py reports.py report_sql.py rqda.py save_sql_query.py select_items.py settings.py special_functions.py text_mining.py view_av.py view_charts.py view_graph.py view_image.py 





After translating, save will produce a name.po and a name.mo file





The .mo file is placed in qualcoder/locale/name/LC_MESSAGES/name.mo
