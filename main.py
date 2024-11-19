import os
import re

import unidecode
import yaml
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor

width, height = A4


def add_footer(c, page_num, visual_config_footer):
    c.setFont(visual_config_footer['fonts']['default'], visual_config_footer['sizes']['small'])
    c.setFillColor(HexColor(visual_config_footer['colors']['footer']))
    footer_text = f"Page {page_num}"
    c.drawString((width / 2) - 20, 30, footer_text)


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
    c.drawString(y_right_column_text_min, y_position, text)

    c.setFont("Arial", 10)
    x_new_position = y_right_column_text_max - c.stringWidth(super_text, "Arial", 10)
    c.drawString(x_new_position, y_position + 5, super_text)

    y_position -= config['Y_delta']
    return y_position, page_number


def draw_entry(c, text, visual_setup, x_position, y_position, page_number, site):
    text = text.replace('\n', '')
    text_words = split_and_keep_delimiters(text)

    if site == "left":
        y_length_min = y_left_column_text_min
        y_length_max = y_left_column_text_max
    else:
        y_length_min = y_right_column_text_min
        y_length_max = y_right_column_text_max
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

        if y_position < y_bottom_margin:
            add_footer(c, page_number, visual_config)
            c.showPage()
            page_number += 1
            draw_left_column_empty(c, height, visual_config)
            y_position = height - y_top_margin

    return y_position, page_number


def draw_entry_left(c, text, visual_setup, y_position, page_number):
    y_position, page_number = draw_entry(c, text, visual_setup, y_left_column_text_min, y_position, page_number, "left")
    return y_position, page_number


def draw_entry_right(c, text, visual_setup, y_position, page_number):
    y_position, page_number = draw_entry(c, text, visual_setup, y_right_column_text_min, y_position, page_number,
                                         "right")
    return y_position, page_number


def create_cv(filename, cv_data_json, visual_config_cv):
    c = canvas.Canvas(filename, pagesize=A4)

    pdfmetrics.registerFont(TTFont(visual_config_cv['fonts']['default'], 'fonts/ARIAL.TTF'))
    pdfmetrics.registerFont(TTFont(visual_config_cv['fonts']['bold'], 'fonts/ARIALBD.TTF'))
    pdfmetrics.registerFont(TTFont(visual_config_cv['fonts']['bold-italic'], 'fonts/ARIALBLACKITALIC.TTF'))
    pdfmetrics.registerFont(TTFont(visual_config_cv['fonts']['italic'], 'fonts/ArialCEItalic.ttf'))
    c.setFont(visual_config_cv['fonts']['default'], visual_config_cv['sizes']['normal'])

    page_number = 1

    c.setFillColor(HexColor(visual_config_cv['colors']['text']))
    draw_left_column(c, cv_data_json, height, page_number, visual_config_cv)
    draw_right_column(c, cv_data_json, height, page_number, visual_config_cv)

    c.save()


def draw_left_column_empty(c, high, visual_config_left):
    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
    c.rect(x_left_column_grey_top, y_left_column_grey_bottom, column_left_width, high - column_left_high_minus,
           stroke=0, fill=1)


def draw_left_column(c, cv_data_json, high, page_number, visual_config_left):
    personal_info = cv_data_json.get("personal_info", {})
    top_skills = cv_data_json.get("top_skills", [])
    tools = cv_data_json.get("tools", [])
    education = cv_data_json.get("education", [])
    certificates = cv_data_json.get("certificates", [])
    own_projects = cv_data_json.get("own_projects", [])
    courses = cv_data_json.get("courses", [])
    languages = cv_data_json.get("languages", [])
    links = cv_data_json.get("links", [])

    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
    c.rect(x_left_column_grey_top, y_left_column_grey_bottom, column_left_width, high - column_left_high_minus,
           stroke=0, fill=1)

    if page_number == 1:
        c.setFillColor(HexColor(visual_config_left['colors']['highlight']))

        y_position = high - y_left_top_text_margin

        y_position, page_number = draw_entry_left(c, f"{personal_info['name']}",
                                                  visual_config_left['left_name_surname'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, f"Email: {personal_info['email']}",
                                                  visual_config_left['left_email_phone'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, f"Phone: {personal_info['phone']}",
                                                  visual_config_left['left_email_phone'], y_position, page_number)

        c.setFont(visual_config_left['fonts']['default'], visual_config_left['sizes']['small'])
        for link in links:
            cleaned_link = link['link_to_show']
            link_name_text = f" ({link['name']})"
            full_link_text = cleaned_link + link_name_text

            y_position, page_number = draw_entry_left(c, full_link_text, visual_config_left['left_default'], y_position,
                                                      page_number)
        y_position -= y_left_column_space_headers
        y_position, page_number = draw_entry_left(c, f"Top Skills", visual_config_left['left_section_name'], y_position,
                                                  page_number)

        for skill in top_skills:
            y_position, page_number = draw_entry_left(c, u"\u2022 " + skill, visual_config_left['left_default'],
                                                      y_position, page_number)

        y_position -= y_left_column_space_headers
        y_position, page_number = draw_entry_left(c, f"Tools", visual_config_left['left_section_name'], y_position,
                                                  page_number)
        y_position, page_number = draw_entry_left(c, ", ".join(tools), visual_config_left['left_default'], y_position,
                                                  page_number)

        y_position -= y_left_column_space_headers
        y_position, page_number = draw_entry_left(c, f"Certificates", visual_config_left['left_section_name'],
                                                  y_position, page_number)
        for certificate in certificates:
            y_position, page_number = draw_entry_left(c, u"\u2022 " + certificate, visual_config_left['left_default'],
                                                      y_position, page_number)

        y_position -= y_left_column_space_headers
        y_position, page_number = draw_entry_left(c, f"Education", visual_config_left['left_section_name'], y_position,
                                                  page_number)
        for edu in education:
            y_position, page_number = draw_education_entry_left(c, edu, y_position, visual_config['education'],
                                                                page_number)

        if own_projects['position'] == "left":
            y_position -= y_left_column_space_headers
            y_position, page_number = draw_entry_left(c, f"Own projects", visual_config_left['left_section_name'],
                                                      y_position, page_number)
            for project in own_projects["projects"]:
                y_position, page_number = draw_entry_left(c, u"\u2022 " + project["time"],
                                                          visual_config_left['left_default'], y_position, page_number)
                if "technologies" in project:
                    technologies = project["name"] + " (" + " ,".join(project["technologies"]) + ")"
                    y_position, page_number = draw_entry_left(c, technologies,
                                                              visual_config_left['left_default'],
                                                              y_position, page_number)

                y_position, page_number = draw_entry_left(c, project["link_to_show"],
                                                          visual_config_left['left_default'], y_position, page_number)

        y_position -= y_left_column_space_headers
        y_position, page_number = draw_entry_left(c, f"Courses", visual_config_left['left_section_name'], y_position,
                                                  page_number)
        for course in courses:
            y_position, page_number = draw_courses_left(c, course, y_position, visual_config['courses'], page_number)

        y_position -= y_left_column_space_headers
        y_position, page_number = draw_entry_left(c, f"Languages", visual_config_left['left_section_name'], y_position,
                                                  page_number)
        for language in languages:
            y_position, page_number = draw_entry_left(c, u"\u2022 " + language, visual_config_left['left_default'],
                                                      y_position, page_number)


def draw_personal_data_info(c, personal_data, visual_config_section, page_number):
    visual_config_personal = visual_config_section['personal_data_info']

    c.setFont(visual_config_personal['font'], visual_config_personal['font_size'])
    c.setFillColor(HexColor(visual_config_personal['color']))

    draw_entry_left(c, personal_data, visual_config_personal, visual_config_personal['y_position'], page_number)


def draw_courses_left(c, course, y_position, visual_setup, page_number):
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
    year_text = str(course["year"])
    course_text = f"{year_text} - {course['name']}"
    y_position, page_number = draw_entry_left(c, course_text, visual_setup, y_position, page_number)

    return y_position, page_number


def draw_education_entry_left(c, edu, y_position, visual_setup, page_number):
    y_position, page_number = draw_entry_left(c, edu["school"], visual_setup['school_name'], y_position, page_number)
    y_position, page_number = draw_entry_left(c, edu['years'], visual_setup['years'], y_position, page_number)
    y_position, page_number = draw_entry_left(c, edu["degree"], visual_setup['degree'], y_position, page_number)
    y_position -= visual_setup['Y_delta_after_education_entry']

    return y_position, page_number


def draw_right_column(c, cv_data_json, high, page_number, visual_config_right):
    experience = cv_data_json.get("experience", [])
    personal_data_info = cv_data_json.get("personal_data_info", "")

    y_position = high - y_right_column_text_top_margin

    y_position, page_number = draw_entry_right(c, "Work Experience", visual_config_right['section_name'],
                                               y_position, page_number)

    #
    y_position -= visual_config_right['right_own_project']['Y_top_margin']
    for job in experience:
        y_position, page_number = draw_experience_entry(c, job, y_position, page_number)
        y_position -= visual_config_right['right_own_project']['Y_margin']

    draw_right_column_projects(c, cv_data_json, y_position, page_number, visual_config_right)

    draw_personal_data_info(c, personal_data_info, visual_config_right, page_number)


def draw_experience_entry(c, job, y_position, page_number):
    y_position, page_number = draw_entry_right_with_superscript(c, job["position"], job["period"],
                                                                visual_config['experience']['period'],
                                                                y_position, page_number)

    y_position, page_number = draw_entry_right(c, job["employer"] + " | " + job["location"],
                                               visual_config['experience']['employer'],
                                               y_position, page_number)

    y_position, page_number = draw_entry_right(c, job["description"], visual_config['experience']['description'],
                                               y_position, page_number)
    y_position -= visual_config['experience']['Y_delta_default']
    if "key_achievements" in job:
        y_position, page_number = draw_entry_right(c, "Key achievements:", visual_config['experience']['description'],
                                                   y_position, page_number)
        for achievement in job["key_achievements"]:
            y_position, page_number = draw_entry_right(c, f"* {achievement}",
                                                       visual_config['experience']['description'],
                                                       y_position, page_number)

    y_position -= visual_config['experience']['Y_delta_default']
    if "technologies" in job:
        technologies = "Technologies: " + ", ".join(job["technologies"])
        y_position, page_number = draw_entry_right(c, technologies, visual_config['experience']['technologies'],
                                                   y_position, page_number)
    y_position -= visual_config['experience']['Y_delta_after_technologies']
    return y_position, page_number


def draw_right_column_projects(c, cv_data_json, y_position, page_number, visual_config_projects):
    own_projects = cv_data_json.get("own_projects", [])

    visual_config_default = visual_config_projects['right_own_project']['default']
    visual_config_link = visual_config_projects['right_own_project']['link']

    if own_projects['position'] == "right":
        y_position -= visual_config_projects['right_own_project']['Y_delta']
        y_position, page_number = draw_entry_right(c, f"Own projects", visual_config_projects['section_name'],
                                                   y_position, page_number)
        for project in own_projects["projects"]:
            y_position, page_number = draw_entry_right_with_superscript(c, project["name"], project["time"],
                                                                        visual_config_default, y_position, page_number)

            y_position, page_number = draw_entry_right(c, project["link_to_show"], visual_config_link, y_position,
                                                       page_number)
            if "technologies" in project:
                technologies = "Technologies: " + ", ".join(project["technologies"])
                y_position, page_number = draw_entry_right(c, technologies,
                                                           visual_config_projects['experience']['technologies'],
                                                           y_position, page_number)
            y_position -= visual_config_projects['right_own_project']['Y_delta']


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate CV PDF from YAML data.')
    parser.add_argument('company', type=str, help='The company identifier for the CV data file.')
    parser.add_argument('--config', type=str, default="data/cv_visual_config.yaml",
                        help='The visual configuration YAML file.')
    args = parser.parse_args()

    company = args.company

    with open(args.config, "r", encoding="utf-8") as v_config_file:
        visual_config = yaml.safe_load(v_config_file)

    with open(f"data/cv_data_{company}.yaml", "r", encoding="utf-8") as file:
        cv_data = yaml.safe_load(file)

    y_top_margin = visual_config['y_top_margin']  # For new page but we have 1 page CV
    y_left_top_text_margin = visual_config['y_left_top_text_margin']
    x_left_column_grey_top = visual_config['x_left_column_grey_top']
    column_left_width = visual_config['column_left_width']
    column_left_high_minus = visual_config['column_left_high_minus']
    y_left_column_text_min = visual_config['y_left_column_text_min']
    y_left_column_text_max = y_left_column_text_min + column_left_width - visual_config['y_left_text_right_margin']
    y_left_column_grey_bottom = visual_config['y_left_column_grey_bottom']

    y_left_column_space_headers = visual_config['y_left_column_space_headers']

    y_right_column_text_top_margin = visual_config['y_right_column_text_top_margin']

    y_right_column_text_min = visual_config['y_right_column_text_min']
    y_right_column_text_max = visual_config['y_right_column_text_max']

    y_bottom_margin = visual_config['y_bottom_margin']

    surname_and_name = cv_data['personal_info']['name']
    pdf_filename = f"output/{unidecode.unidecode(surname_and_name).replace(' ', '_')}_{company}.pdf"

    if os.path.isfile(pdf_filename):
        os.remove(pdf_filename)
        print(f"The Old {pdf_filename} has been removed.")

    create_cv(pdf_filename, cv_data, visual_config)

    if os.path.isfile(pdf_filename):
        print(f"The new {pdf_filename} has been generated.")
