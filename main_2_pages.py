import os
import re

import unidecode
import yaml
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor

from types import MappingProxyType
import shutil

WIDTH, HEIGHT = A4


def page_add(c, page_number):
    add_footer(c, page_number)
    c.showPage()
    page_number += 1
    draw_left_column(c, page_number)
    y_position = HEIGHT - VISUAL_CONFIG['y_top_margin']

    return y_position, page_number

def add_footer(c, page_num):
    c.setFont(VISUAL_CONFIG['fonts']['default'], VISUAL_CONFIG['sizes']['small'])
    c.setFillColor(HexColor(VISUAL_CONFIG['colors']['footer']))
    footer_text = f"Page {page_num}"
    c.drawString((WIDTH / 2) - 20, 10, footer_text)


def split_and_keep_delimiters(s):
    pattern = r'([\s\-_])'
    parts = re.split(pattern, s)
    result = []

    for i in range(0, len(parts) - 1, 2):
        result.append((parts[i], parts[i + 1]))

    if len(parts) % 2 == 1:
        result.append((parts[-1], ''))

    return result


def draw_entry_right_with_superscript(c, text, super_text, config, y_position, page_number):
    c.setFont("Arial", 12)
    c.drawString(VISUAL_CONFIG['y_right_column_text_min'], y_position, text)

    c.setFont("Arial", 10)
    x_new_position = VISUAL_CONFIG['y_right_column_text_max'] - c.stringWidth(super_text, "Arial", 10)
    c.drawString(x_new_position, y_position + 5, super_text)

    y_position -= config['Y_delta']
    return y_position, page_number


def draw_entry(c, text, visual_setup, x_position, y_position, page_number, site, ignore_new_site = False):
    text = text.replace('\n', '')
    text_words = split_and_keep_delimiters(text)

    if site == "left":
        y_length_min = VISUAL_CONFIG['y_left_column_text_min']
        y_length_max = VISUAL_CONFIG['y_left_column_text_min'] + VISUAL_CONFIG['column_left_width'] - VISUAL_CONFIG['y_left_text_right_margin']
    else:
        y_length_min = VISUAL_CONFIG['y_right_column_text_min']
        y_length_max = VISUAL_CONFIG['y_right_column_text_max']
    y_length_allowed = y_length_max - y_length_min

    text_lines = []
    line = ""
    for word in text_words:
        line_length = c.stringWidth(line, visual_setup['font'], visual_setup['font_size']) + c.stringWidth(word[0],
                                     visual_setup['font'], visual_setup['font_size'])
        if line_length <= y_length_allowed:
            line += word[0] + word[1]
        else:
            text_lines.append(line)
            line = word[0] + word[1]

    text_lines.append(line)

    for line in text_lines:
        c.setFillColor(HexColor(visual_setup['color']))
        c.setFont(visual_setup['font'], visual_setup['font_size'])
        c.drawString(x_position, y_position, line)
        y_position -= visual_setup['Y_delta']

        if not ignore_new_site and y_position < VISUAL_CONFIG['y_bottom_margin']:
            y_position, page_number = page_add(c, page_number)

    return y_position, page_number


def draw_entry_left(c, text, visual_setup, y_position, page_number, ignore_new_site = False):
    y_position, page_number = draw_entry(c, text, visual_setup, VISUAL_CONFIG['y_left_column_text_min'], y_position, page_number,
                                         "left", ignore_new_site)
    return y_position, page_number


def draw_entry_right(c, text, visual_setup, y_position, page_number, ignore_new_site = False):
    y_position, page_number = draw_entry(c, text, visual_setup, VISUAL_CONFIG['y_right_column_text_min'], y_position, page_number,
                                         "right", ignore_new_site)
    return y_position, page_number


def create_cv(filename):
    author_name = CV_DATA.get("personal_info", {}).get("name", "")

    c = canvas.Canvas(filename, pagesize=A4)
    c.setAuthor(author_name)
    c.setCreator("Generator CV: https://github.com/ziutus/cv_with_llm")

    pdfmetrics.registerFont(TTFont(VISUAL_CONFIG['fonts']['default'], 'fonts/ARIAL.TTF'))
    pdfmetrics.registerFont(TTFont(VISUAL_CONFIG['fonts']['bold'], 'fonts/ARIALBD.TTF'))
    pdfmetrics.registerFont(TTFont(VISUAL_CONFIG['fonts']['bold-italic'], 'fonts/ARIALBLACKITALIC.TTF'))
    pdfmetrics.registerFont(TTFont(VISUAL_CONFIG['fonts']['italic'], 'fonts/ArialCEItalic.ttf'))
    c.setFont(VISUAL_CONFIG['fonts']['default'], VISUAL_CONFIG['sizes']['normal'])

    c.setFillColor(HexColor(VISUAL_CONFIG['colors']['text']))
    draw_left_column(c, 1)
    draw_right_column(c, 1)

    c.save()

def draw_left_column(c, page_number):

    c.setFillColor(HexColor(VISUAL_CONFIG['colors']['grey_background']))
    c.rect(VISUAL_CONFIG['x_left_column_grey_top'], VISUAL_CONFIG['y_left_column_grey_bottom'], VISUAL_CONFIG['column_left_width'], HEIGHT - VISUAL_CONFIG['column_left_high_minus'],
           stroke=0, fill=1)

    if page_number == 1:
        c.setFillColor(HexColor(VISUAL_CONFIG['colors']['highlight']))
        y_position = HEIGHT - VISUAL_CONFIG['y_left_top_text_margin']

        personal_info = CV_DATA.get("personal_info", {})
        y_position, page_number = draw_entry_left(c, f"{personal_info['name']}",
                                                  VISUAL_CONFIG['left_name_surname'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, f"Email: {personal_info['email']}",
                                                  VISUAL_CONFIG['left_email_phone'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, f"Phone: {personal_info['phone']}",
                                                  VISUAL_CONFIG['left_email_phone'], y_position, page_number)

        c.setFont(VISUAL_CONFIG['fonts']['default'], VISUAL_CONFIG['sizes']['small'])

        y_position, page_number = draw_left_column_links(c, y_position, page_number)
        y_position, page_number = draw_left_column_top_skills(c, y_position, page_number)
        y_position, page_number = draw_left_column_tools(c, y_position, page_number)
        y_position, page_number = draw_left_column_certificates(c, y_position, page_number)
        y_position, page_number = draw_left_column_education(c, y_position, page_number)

        own_projects = CV_DATA.get("own_projects", [])

        if own_projects['position'] == "left":
            y_position, page_number = draw_left_column_own_projects(c, y_position, page_number, own_projects)

        y_position, page_number = draw_left_column_languages(c, y_position, page_number)

    if page_number == 2:
        y_position = HEIGHT - VISUAL_CONFIG['y_left_top_text_margin']
        y_position, page_number = draw_left_column_courses(c, y_position, page_number)

def draw_left_column_links(c, y_position, page_number):
    links = CV_DATA.get("links", [])
    for link in links:
        cleaned_link = link['link_to_show']
        link_name_text = f" ({link['name']})"
        full_link_text = cleaned_link + link_name_text

        y_position, page_number = draw_entry_left(c, full_link_text, VISUAL_CONFIG['left_default'], y_position,
                                                  page_number)

    return y_position, page_number


def draw_left_column_top_skills(c, y_position, page_number):
    y_position -= VISUAL_CONFIG['y_left_column_space_headers']

    y_position, page_number = draw_entry_left(c, f"Top Skills", VISUAL_CONFIG['left_section_name'], y_position,
                                              page_number)

    top_skills = CV_DATA.get("top_skills", [])
    for skill in top_skills:
        y_position, page_number = draw_entry_left(c, u"\u2022 " + skill, VISUAL_CONFIG['left_default'],
                                                  y_position, page_number)

    return y_position, page_number

def draw_left_column_tools(c, y_position, page_number):
    tools = CV_DATA.get("tools", [])
    y_position -= VISUAL_CONFIG['y_left_column_space_headers']
    y_position, page_number = draw_entry_left(c, f"Tools", VISUAL_CONFIG['left_section_name'], y_position,
                                              page_number)
    y_position, page_number = draw_entry_left(c, ", ".join(tools), VISUAL_CONFIG['left_default'], y_position,
                                              page_number)

    return y_position, page_number

def draw_left_column_certificates(c, y_position, page_number):
    y_position -= VISUAL_CONFIG['y_left_column_space_headers']
    y_position, page_number = draw_entry_left(c, f"Certificates", VISUAL_CONFIG['left_section_name'],
                                              y_position, page_number)

    certificates = CV_DATA.get("certificates", [])
    for certificate in certificates:
        y_position, page_number = draw_entry_left(c, u"\u2022 " + certificate, VISUAL_CONFIG['left_default'],
                                                  y_position, page_number)
    return y_position, page_number

def draw_left_column_education(c, y_position, page_number):
    y_position -= VISUAL_CONFIG['y_left_column_space_headers']
    y_position, page_number = draw_entry_left(c, f"Education", VISUAL_CONFIG['left_section_name'], y_position,
                                              page_number)

    education = CV_DATA.get("education", [])
    for edu in education:
        y_position, page_number = draw_education_entry_left(c, edu, y_position, page_number)

    return y_position, page_number

def draw_left_column_own_projects(c, y_position, page_number, own_projects):
    y_position -= VISUAL_CONFIG['y_left_column_space_headers']
    y_position, page_number = draw_entry_left(c, f"Own projects", VISUAL_CONFIG['left_section_name'],
                                              y_position, page_number)
    for project in own_projects["projects"]:
        y_position, page_number = draw_entry_left(c, u"\u2022 " + project["time"],
                                                  VISUAL_CONFIG['left_default'], y_position, page_number)
        if "technologies" in project:
            technologies = project["name"] + " (" + " ,".join(project["technologies"]) + ")"
            y_position, page_number = draw_entry_left(c, technologies,
                                                      VISUAL_CONFIG['left_default'],
                                                      y_position, page_number)

        y_position, page_number = draw_entry_left(c, project["link_to_show"],
                                                  VISUAL_CONFIG['left_default'], y_position, page_number)

    return y_position, page_number

def draw_left_column_languages(c, y_position, page_number):
    y_position -= VISUAL_CONFIG['y_left_column_space_headers']
    y_position, page_number = draw_entry_left(c, f"Languages", VISUAL_CONFIG['left_section_name'], y_position,
                                              page_number)

    languages = CV_DATA.get("languages", [])
    for language in languages:
        y_position, page_number = draw_entry_left(c, u"\u2022 " + language, VISUAL_CONFIG['left_default'],
                                                  y_position, page_number)
    return y_position, page_number

def draw_left_column_courses(c, y_position, page_number):
    courses = CV_DATA.get("courses", [])

    y_position -= VISUAL_CONFIG['y_left_column_space_headers']
    y_position, page_number = draw_entry_left(c, f"Courses", VISUAL_CONFIG['left_section_name'], y_position,
                                              page_number)
    for course in courses:
        y_position, page_number = draw_courses_left(c, course, y_position, page_number)

    return y_position, page_number

def draw_right_column_courses(c, y_position, page_number):
    experience = CV_DATA.get("experience", [])

    y_position, page_number = draw_entry_right(c, "Work Experience", VISUAL_CONFIG['section_name'],
                                               y_position, page_number)

    y_position -= VISUAL_CONFIG['right_own_project']['Y_top_margin']
    for job in experience:
        if y_position < 100 and page_number == 1:
            y_position, page_number = page_add(c, page_number)
            c.setFillColor(HexColor('#000000'))

        y_position, page_number = draw_experience_entry(c, job, y_position, page_number)
        y_position -= VISUAL_CONFIG['right_own_project']['Y_margin']

    return y_position, page_number

def draw_personal_data_info(c, page_number):
    personal_data_info = CV_DATA.get("personal_data_info", "")
    c.setFont(VISUAL_CONFIG['personal_data_info']['font'], VISUAL_CONFIG['personal_data_info']['font_size'])
    c.setFillColor(HexColor(VISUAL_CONFIG['personal_data_info']['color']))

    draw_entry_left(c, personal_data_info, VISUAL_CONFIG['personal_data_info'], VISUAL_CONFIG['personal_data_info']['y_position'], page_number)

def draw_own_generate_info(c, page_number):
    own_generate_info = CV_DATA.get("own_generate_info", "")
    c.setFont(VISUAL_CONFIG['own_generate_info']['font'], VISUAL_CONFIG['own_generate_info']['font_size'])
    c.setFillColor(HexColor(VISUAL_CONFIG['own_generate_info']['color']))

    draw_entry_right(c, own_generate_info, VISUAL_CONFIG['own_generate_info'], VISUAL_CONFIG['own_generate_info']['y_position'], page_number, True)

def draw_courses_left(c, course, y_position, page_number):
    c.setFont(VISUAL_CONFIG['fonts']['default'], VISUAL_CONFIG['sizes']['normal'])
    year_text = str(course["year"])
    course_text = f"{year_text} - {course['name']}"
    y_position, page_number = draw_entry_left(c, course_text, VISUAL_CONFIG['courses'], y_position, page_number)

    return y_position, page_number


def draw_education_entry_left(c, edu, y_position, page_number):
    y_position, page_number = draw_entry_left(c, edu["school"], VISUAL_CONFIG['education']['school_name'], y_position, page_number)
    y_position, page_number = draw_entry_left(c, edu['years'], VISUAL_CONFIG['education']['years'], y_position, page_number)
    y_position, page_number = draw_entry_left(c, edu["degree"] + ': ' + edu["field_of_study"], VISUAL_CONFIG['education']['degree'], y_position, page_number)
    y_position -= VISUAL_CONFIG['education']['Y_delta_after_education_entry']

    return y_position, page_number


def draw_right_column(c, page_number):
    y_position = HEIGHT - VISUAL_CONFIG['y_right_column_text_top_margin']
    y_position, page_number = draw_right_column_courses(c, y_position, page_number)
    draw_right_column_projects(c, y_position, page_number)

    draw_personal_data_info(c, page_number)
    draw_own_generate_info(c, page_number)


def draw_experience_entry(c, job, y_position, page_number):
    y_position, page_number = draw_entry_right_with_superscript(c, job["position"], job["period"],
                                                                VISUAL_CONFIG['experience']['period'],
                                                                y_position, page_number)

    y_position, page_number = draw_entry_right(c, job["employer"] + " | " + job["location"],
                                               VISUAL_CONFIG['experience']['employer'],
                                               y_position, page_number)

    y_position, page_number = draw_entry_right(c, job["description"], VISUAL_CONFIG['experience']['description'],
                                               y_position, page_number)
    y_position -= VISUAL_CONFIG['experience']['Y_delta_default']
    if "key_achievements" in job:
        y_position, page_number = draw_entry_right(c, "Key achievements:", VISUAL_CONFIG['experience']['description'],
                                                   y_position, page_number)
        for achievement in job["key_achievements"]:
            y_position, page_number = draw_entry_right(c, f"* {achievement}",
                                                       VISUAL_CONFIG['experience']['description'],
                                                       y_position, page_number)

    y_position -= VISUAL_CONFIG['experience']['Y_delta_default']
    if "technologies" in job:
        technologies = "Technologies: " + ", ".join(job["technologies"])
        y_position, page_number = draw_entry_right(c, technologies, VISUAL_CONFIG['experience']['technologies'],
                                                   y_position, page_number)
    y_position -= VISUAL_CONFIG['experience']['Y_delta_after_technologies']
    return y_position, page_number


def draw_right_column_projects(c, y_position, page_number):
    own_projects = CV_DATA.get("own_projects", [])

    visual_config_default = VISUAL_CONFIG['right_own_project']['default']
    visual_config_link = VISUAL_CONFIG['right_own_project']['link']

    if own_projects['position'] == "right":
        y_position -= VISUAL_CONFIG['right_own_project']['Y_delta']
        y_position, page_number = draw_entry_right(c, f"Own projects", VISUAL_CONFIG['section_name'],
                                                   y_position, page_number)
        for project in own_projects["projects"]:
            y_position, page_number = draw_entry_right_with_superscript(c, project["name"], project["time"],
                                                                        visual_config_default, y_position, page_number)

            y_position, page_number = draw_entry_right(c, project["link_to_show"], visual_config_link, y_position,
                                                       page_number)
            if "technologies" in project:
                technologies = "Technologies: " + ", ".join(project["technologies"])
                y_position, page_number = draw_entry_right(c, technologies,
                                                           VISUAL_CONFIG['experience']['technologies'],
                                                           y_position, page_number)
            y_position -= VISUAL_CONFIG['right_own_project']['Y_delta']


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate CV PDF from YAML data.')
    parser.add_argument('company', type=str, help='The company identifier for the CV data file.')
    parser.add_argument('--config', type=str, default="data/cv_visual_config.yaml",
                        help='The visual configuration YAML file.')
    args = parser.parse_args()

    company = args.company

    with open(args.config, "r", encoding="utf-8") as v_config_file:
        _visual_config = yaml.safe_load(v_config_file)
        VISUAL_CONFIG = MappingProxyType(_visual_config)

    with open(f"data/cv_data_{company}.yaml", "r", encoding="utf-8") as file:
        _cv_data = yaml.safe_load(file)
        CV_DATA = MappingProxyType(_cv_data)

    pdf_filename = f"output/{unidecode.unidecode(CV_DATA['personal_info']['name']).replace(' ', '_')}_{company}.pdf"
    pdf_filename_base = f"output/{unidecode.unidecode(CV_DATA['personal_info']['name']).replace(' ', '_')}.pdf"


    if os.path.isfile(pdf_filename):
        os.remove(pdf_filename)
        print(f"The Old {pdf_filename} has been removed.")
    if os.path.isfile(pdf_filename_base):
        os.remove(pdf_filename_base)
        print(f"The Old {pdf_filename_base} has been removed.")

    create_cv(pdf_filename)
    shutil.copy2(pdf_filename, pdf_filename_base)

    if os.path.isfile(pdf_filename):
        print(f"The new {pdf_filename} has been generated.")
    if os.path.isfile(pdf_filename_base):
        print(f"The new {pdf_filename_base} has been generated.")
