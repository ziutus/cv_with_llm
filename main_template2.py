import os

import unidecode
import yaml
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
import textwrap

y_offset = 50
y_left_column_text = 60
width, height = A4
column_left_width = 210


def draw_courses_left(c, course, y_position, visual_setup, page_number):
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
    year_text = str(course["year"])
    course_text = f"{year_text} - {course['name']}"

    if "link" in course and course["link"]:
        link_text = " (link)"
        c.drawString(60, y_position, course_text)

        c.setFillColor(HexColor(visual_config['colors']['link']))
        link_start_x = 60 + c.stringWidth(course_text)
        c.drawString(link_start_x, y_position, link_text)
        underline_y = y_position - 1
        link_width = c.stringWidth(link_text)
        c.line(link_start_x, underline_y, link_start_x + link_width, underline_y)
        c.linkURL(course["link"], (link_start_x, y_position - 2, link_start_x + link_width, y_position + 12),
                  relative=1)
        c.setFillColor(HexColor(visual_config['colors']['text']))
        y_position -= 15
    else:
        y_position, page_number = draw_entry_left(c, course_text, visual_setup, y_position, page_number)

    return y_position, page_number

def draw_education_entry_left(c, edu, y_position, visual_setup, page_number):
    y_position, page_number = draw_entry_left(c, edu["school"], visual_setup['school_name'], y_position, page_number)
    y_position, page_number = draw_entry_left(c, edu['years'], visual_setup['years'], y_position, page_number)
    y_position, page_number = draw_entry_left(c, edu["degree"], visual_setup['degree'], y_position, page_number)
    y_position -= 5

    return y_position, page_number

def draw_entry_left(c, text, visual_setup, y_position, page_number):
    y_position, page_number = draw_entry(c, text, visual_setup, 60, y_position, page_number)
    return y_position, page_number

def draw_entry(c, text, visual_setup, x_position, y_position, page_number):
    text_wrapped = textwrap.wrap(text, width=visual_setup['width'])
    for line in text_wrapped:
        c.setFillColor(HexColor(visual_setup['color']))
        c.setFont(visual_setup['font'], visual_setup['font_size'])
        c.drawString(x_position, y_position, line)
        y_position -= visual_setup['Y_delta']

        if y_position < y_offset:
            add_footer(c, page_number, visual_config)
            c.showPage()
            page_number += 1
            draw_left_column_empty(c, height, visual_config)
            y_position = height - y_offset

    return y_position, page_number

def draw_entry_right(c, text, visual_setup, y_position, page_number):
    y_position, page_number = draw_entry(c, text, visual_setup, 270, y_position, page_number)
    return y_position, page_number

def draw_entry_right_with_superscript(c, text, super_text, config, y_position, page_number):
    # Rysowanie głównego tekstu
    c.setFont("Arial", 12)
    c.drawString(270, y_position, text)

    # Szerokość głównego tekstu
    text_width = c.stringWidth(text, "Arial", 12)

    # Rysowanie górnego indeksu
    c.setFont("Arial", 10)
    x_new_position = 595 - 20 - c.stringWidth(super_text, "Arial", 10)
    c.drawString(x_new_position, y_position + 5, super_text)

    y_position -= config['Y_delta']
    return y_position, page_number

def add_footer(c, page_num, visual_config_footer):
    """Adds a footer with the page number."""
    width, height = A4
    c.setFont(visual_config_footer['fonts']['default'], visual_config_footer['sizes']['small'])
    c.setFillColor(HexColor(visual_config_footer['colors']['footer']))
    footer_text = f"Page {page_num}"
    c.drawString((width / 2) - 20, 30, footer_text)

def draw_left_column_empty(c, height, visual_config_left):

    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
    c.rect(50, 50, column_left_width, height - 100, stroke=0, fill=1)


def draw_left_column(c, personal_info, top_skills, tools, education, certificates, courses, languages, links, height, y_start, page_number,
                     visual_config_left):


    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
    c.rect(50, 50, column_left_width, height - 100, stroke=0, fill=1)

    if page_number == 1:
        c.setFillColor(HexColor(visual_config_left['colors']['highlight']))

        y_position = height - 70

        y_position, page_number = draw_entry_left(c, f"{personal_info['name']}", visual_config_left['left_name_surname'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, f"Email: {personal_info['email']}", visual_config_left['left_email_phone'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, f"Phone: {personal_info['phone']}", visual_config_left['left_email_phone'], y_position, page_number)
        y_position -= 10

        c.setFont(visual_config_left['fonts']['default'], visual_config_left['sizes']['small'])
        for link in links:
            cleaned_link = link['link_to_show']
            link_name_text = f" ({link['name']})"
            full_link_text = cleaned_link + link_name_text

            y_position, page_number = draw_entry_left(c, full_link_text, visual_config_left['left_default'], y_position,
                                                      page_number)


        y_position -= 10
        y_position, page_number = draw_entry_left(c, f"Top Skills", visual_config_left['left_section_name'], y_position, page_number)

        for skill in top_skills:
            y_position, page_number = draw_entry_left(c,  u"\u2022 " + skill, visual_config_left['left_default'],
                                                      y_position, page_number)

        y_position -= 10
        y_position, page_number = draw_entry_left(c, f"Tools", visual_config_left['left_section_name'], y_position, page_number)
        y_position, page_number = draw_entry_left(c, ", ".join(tools), visual_config_left['left_default'], y_position, page_number)


        y_position -= 10
        y_position, page_number = draw_entry_left(c, f"Certificates", visual_config_left['left_section_name'], y_position, page_number)
        for certificate in certificates:
            y_position, page_number = draw_entry_left(c, u"\u2022 " + certificate, visual_config_left['left_default'], y_position, page_number)


        y_position -= 10
        y_position, page_number = draw_entry_left(c, f"Education", visual_config_left['left_section_name'], y_position, page_number)
        for edu in education:
            y_position, page_number = draw_education_entry_left(c, edu, y_position, visual_config['education'], page_number)

        y_position -= 10
        y_position, page_number = draw_entry_left(c, f"Courses", visual_config_left['left_section_name'], y_position, page_number)
        for course in courses:
            y_position, page_number = draw_courses_left(c, course, y_position, visual_config['courses'], page_number)

        y_position -= 10
        y_position, page_number = draw_entry_left(c, f"Languages", visual_config_left['left_section_name'], y_position, page_number)
        for language in languages:
            y_position, page_number = draw_entry_left(c, u"\u2022 " + language, visual_config_left['left_default'], y_position, page_number)


def create_cv(filename, cv_data_json, visual_config):
    c = canvas.Canvas(filename, pagesize=A4)

    personal_info = cv_data_json.get("personal_info", {})
    top_skills = cv_data_json.get("top_skills", [])
    certificates = cv_data_json.get("certificates", [])
    languages = cv_data_json.get("languages", [])
    summary = cv_data_json.get("summary", "")
    experience = cv_data_json.get("experience", [])
    education = cv_data_json.get("education", [])
    links = cv_data_json.get("links", [])
    tools = cv_data_json.get("tools", [])
    courses = cv_data_json.get("courses", [])
    personal_data_info = cv_data_json.get("personal_data_info", "")

    pdfmetrics.registerFont(TTFont(visual_config['fonts']['default'], 'ARIAL.TTF'))
    pdfmetrics.registerFont(TTFont(visual_config['fonts']['bold'], 'ARIALBD.TTF'))
    pdfmetrics.registerFont(TTFont(visual_config['fonts']['italic'], 'ARIALBLACKITALIC.TTF'))
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])

    page_number = 1

    def draw_experience_entry(job, y_position, page_number):

        y_position, page_number = draw_entry_right_with_superscript(c, job["position"], job["period"],
                                                                    visual_config['experience']['period'],
                                                                    y_position, page_number)

        y_position, page_number = draw_entry_right(c, job["employer"] + " | " + job["location"], visual_config['experience']['employer'],
                                                   y_position, page_number)

        y_position, page_number = draw_entry_right(c, job["description"], visual_config['experience']['description'],
                                                   y_position, page_number)
        y_position -= 4
        if "key_achievements" in job:
            y_position, page_number = draw_entry_right(c, "Key achievements:", visual_config['experience']['description'],
                                                       y_position, page_number)
            for achievement in job["key_achievements"]:
                y_position, page_number = draw_entry_right(c, f"* {achievement}", visual_config['experience']['description'],
                                                   y_position, page_number)

        y_position -= 4
        if "technologies" in job:
            technologies = "Technologies: " + ", ".join(job["technologies"])
            y_position, page_number = draw_entry_right(c, technologies, visual_config['experience']['technologies'],
                                                   y_position, page_number)
        y_position -= 6
        return y_position, page_number

    def draw_personal_data_info(c, personal_data, visual_config_section):
        visual_config = visual_config_section['personal_data_info']
        width = visual_config['width']  # Pobranie szerokości tekstu
        font = visual_config['font']  # Pobranie czcionki
        font_size = visual_config['font_size']  # Pobranie rozmiaru czcionki
        color = visual_config['color']  # Pobranie koloru tekstu
        y_position = visual_config['y_position']

        c.setFont(font, font_size)
        c.setFillColor(HexColor(color))

        wrapped_info_lines = textwrap.wrap(personal_data, width=width)  # Użyj szerokości z pliku konfiguracyjnego

        for personal_line in wrapped_info_lines:
            c.drawString(270, y_position, personal_line)
            y_position -= 10

    c.setFillColor(HexColor(visual_config['colors']['text']))
    y_position = height - 160
    draw_left_column(c, personal_info, top_skills, tools, education, certificates, courses, languages, links, height, y_position, page_number,
                     visual_config)

    y_position = height -55

    y_position, page_number = draw_entry_right(c, "Work Experience", visual_config['section_name'],
                                               y_position -10, page_number)

    y_position -= 4
    for job in experience:
        y_position, page_number = draw_experience_entry(job, y_position, page_number)
        y_position -= 3

    draw_personal_data_info(c, personal_data_info, visual_config)

    # add_footer(c, page_number, visual_config)

    c.save()


with open("cv_visual_config_template2.yaml", "r", encoding="utf-8") as v_config_file:
    visual_config = yaml.safe_load(v_config_file)

with open("cv_data_20241105.yaml", "r", encoding="utf-8") as file:
    cv_data = yaml.safe_load(file)


surname_and_name = cv_data['personal_info']['name']
pdf_filename = f"{unidecode.unidecode(surname_and_name).replace(' ', '_')}_20241105.pdf"

if os.path.isfile(pdf_filename):
    os.remove(pdf_filename)
    print(f"The Old {pdf_filename} has been removed.")

create_cv(pdf_filename, cv_data, visual_config)

if os.path.isfile(pdf_filename):
    print(f"The new {pdf_filename} has been generated.")