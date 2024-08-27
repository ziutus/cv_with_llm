import os

import unidecode
import yaml
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from PIL import Image, ImageDraw
import textwrap

def draw_entry_left(c, text, visual_setup, y_position, page_number):
    y_position, page_number = draw_entry(c, text, visual_setup, 60, y_position, page_number)
    return y_position, page_number

def draw_entry(c, text, visual_setup, x_position, y_position, page_number):
    c.setFillColor(HexColor(visual_setup['color']))
    c.setFont(visual_setup['font'], visual_setup['font_size'])
    text_wrapped = textwrap.wrap(text, width=visual_setup['width'])
    for line in text_wrapped:
        c.drawString(x_position, y_position, line)
        y_position -= visual_setup['Y_delta']

    return y_position, page_number

def draw_entry_right(c, text, visual_setup, y_position, page_number):
    y_position, page_number = draw_entry(c, text, visual_setup, 270, y_position, page_number)
    return y_position, page_number

def create_round_mask(image_path, output_path, size):
    """Creates a round mask for the image."""
    with Image.open(image_path) as im:
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, *size), fill=255)
        im = im.resize(size, Image.Resampling.LANCZOS)
        im.putalpha(mask)
        im.save(output_path, format="PNG")


def add_footer(c, page_num, visual_config_footer):
    """Adds a footer with the page number."""
    width, height = A4
    c.setFont(visual_config_footer['fonts']['default'], visual_config_footer['sizes']['small'])
    c.setFillColor(HexColor(visual_config_footer['colors']['footer']))
    footer_text = f"Page {page_num}"
    c.drawString((width / 2) - 20, 30, footer_text)

def draw_left_column_empty(c, height, visual_config_left):
    column_width = 200  # Adjusted width of the left column

    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
    c.rect(50, 50, column_width, height - 100, stroke=0, fill=1)


def draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, y_start, page_number,
                     visual_config_left):
    """Draws the left column with personal data, top skills, certificates, languages, and links."""

    column_width = 200  # Adjusted width of the left column

    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
    c.rect(50, 50, column_width, height - 100, stroke=0, fill=1)

    if page_number == 1:
        c.setFillColor(HexColor(visual_config_left['colors']['highlight']))

        photo_path = 'photo.jpg'
        round_photo_path = 'round_photo.png'
        create_round_mask(photo_path, round_photo_path, size=(int(column_width) - 20, int(column_width) - 20))
        c.drawImage(round_photo_path, 50, height - (int(column_width) + 50), width=column_width, height=column_width,
                    mask='auto')

        c.setFont(visual_config_left['fonts']['default'], visual_config_left['sizes']['small'])

        y_position = height - (int(column_width) + 70)
        c.drawString(60, y_position, f"Email: {personal_info['email']}")
        y_position -= 20

        # y_position, page_number = draw_entry_right(c, f"Email: {personal_info['email']}", visual_setup['degree'], y_position, page_number)

        c.drawString(60, y_position, f"Phone: {personal_info['phone']}")

        y_position -= 30
        for link in links:
            cleaned_link = link['link'].replace("https://", "").replace("http://", "")
            link_name_text = f" ({link['name']})"
            full_link_text = cleaned_link + link_name_text
            wrapped_link_lines = textwrap.wrap(full_link_text, width=36)

            for line in wrapped_link_lines:
                if line.endswith(link_name_text):
                    link_part = line[:-len(link_name_text)]
                    c.setFillColor(HexColor(visual_config_left['colors']['highlight']))
                    c.drawString(60, y_position, link_part)
                    c.setFillColor(HexColor(visual_config_left['colors']['grey_background']))
                    c.drawString(60 + c.stringWidth(link_part), y_position, link_name_text)
                else:
                    c.setFillColor(HexColor(visual_config_left['colors']['highlight']))
                    c.drawString(60, y_position, line)
                y_position -= 12

        y_position -= 20
        c.setFont(visual_config_left['fonts']['bold'], visual_config_left['sizes']['small'])
        c.setFillColor(HexColor(visual_config_left['colors']['highlight']))
        c.drawString(60, y_position, "Top Skills")
        c.setFont(visual_config_left['fonts']['default'], visual_config_left['sizes']['small'])

        y_position -= 20
        for skill in top_skills:
            c.drawString(60, y_position, u"\u2022 " + skill)
            y_position -= 20

        y_position -= 20
        c.setFont(visual_config_left['fonts']['bold'], visual_config_left['sizes']['small'])
        c.setFillColor(HexColor(visual_config_left['colors']['highlight']))
        c.drawString(60, y_position, "Certificates")
        c.setFont(visual_config_left['fonts']['default'], visual_config_left['sizes']['small'])

        y_position -= 20
        for certificate in certificates:
            c.drawString(60, y_position, u"\u2022 " + certificate)
            y_position -= 20

        y_position -= 20
        c.setFont(visual_config_left['fonts']['bold'], visual_config_left['sizes']['small'])
        c.setFillColor(HexColor(visual_config_left['colors']['highlight']))
        c.drawString(60, y_position, "Languages")
        c.setFont(visual_config_left['fonts']['default'], visual_config_left['sizes']['small'])

        y_position -= 20
        for language in languages:
            c.drawString(60, y_position, u"\u2022 " + language)
            y_position -= 20


def create_cv(filename, cv_data_json, visual_config):
    c = canvas.Canvas(filename, pagesize=A4)

    personal_info = cv_data_json.get("personal_info", {})
    top_skills = cv_data_json.get("top_skills", [])
    certificates = cv_data_json.get("certificates", [])
    languages = cv_data_json.get("languages", [])
    summary = cv_data_json.get("summary", "")
    summary_short = cv_data_json.get("summary_short", "")
    experience = cv_data_json.get("experience", [])
    education = cv_data_json.get("education", [])
    links = cv_data_json.get("links", [])
    courses = cv_data_json.get("courses", [])
    personal_data_info = cv_data_json.get("personal_data_info", "")

    pdfmetrics.registerFont(TTFont(visual_config['fonts']['default'], 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont(visual_config['fonts']['bold'], 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont(visual_config['fonts']['italic'], 'DejaVuSans-Oblique.ttf'))
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])

    width, height = A4
    page_number = 1
    y_offset = 50

    def draw_experience(job, y_position, page_number, added_work_experience):
        if not added_work_experience:
            if y_position != height - 200:
                c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['subtitle'])
                c.drawString(270, y_position, "Work Experience")
                y_position -= 20
                added_work_experience = True

        c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['normal'])
        c.drawString(270, y_position, job["employer"])
        y_position -= 20
        c.setFont(visual_config['fonts']['italic'], visual_config['sizes']['normal'])
        c.drawString(270, y_position, job["position"])
        y_position -= 20
        c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
        c.drawString(270, y_position, job["period"])
        y_position -= 20
        c.drawString(270, y_position, job["location"])
        y_position -= 20

        description_lines = textwrap.wrap(job["description"], width=60)
        for line in description_lines:
            c.drawString(270, y_position, line)
            y_position -= 15

            if y_position < y_offset:
                add_footer(c, page_number, visual_config)
                c.showPage()
                page_number += 1
                draw_left_column_empty(c, height, visual_config)
                c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
                c.setFillColor(HexColor(visual_config['colors']['text']))
                y_position = height - 160

        return y_position, page_number, added_work_experience

    def draw_education(edu, y_position, visual_setup, page_number):
        y_position, page_number = draw_entry_right(c, edu["school"], visual_setup['school_name'], y_position - 10, page_number)
        text = f'{edu["degree"]}, {edu["field_of_study"]}'
        y_position, page_number = draw_entry_right(c, text, visual_setup['degree'], y_position, page_number)
        y_position, page_number = draw_entry_right(c, edu['years'], visual_setup['years'], y_position, page_number)

        return y_position, page_number

    def draw_courses(course, y_position, page_number, first_page=False):
        if not first_page or (first_page and y_position != height - 200):
            c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
            year_text = str(course["year"])
            course_text = f"{year_text} - {course['name']}"

            if "link" in course and course["link"]:
                link_text = " (link)"
                c.drawString(270, y_position, course_text)

                c.setFillColor(HexColor(visual_config['colors']['link']))
                link_start_x = 270 + c.stringWidth(course_text)
                c.drawString(link_start_x, y_position, link_text)
                underline_y = y_position - 1
                link_width = c.stringWidth(link_text)
                c.line(link_start_x, underline_y, link_start_x + link_width, underline_y)
                c.linkURL(course["link"], (link_start_x, y_position - 2, link_start_x + link_width, y_position + 12),
                          relative=1)
                c.setFillColor(HexColor(visual_config['colors']['text']))
            else:
                c.drawString(270, y_position, course_text)

            y_position -= 15

            if y_position < y_offset:
                add_footer(c, page_number, visual_config)
                c.showPage()
                page_number += 1
                draw_left_column_empty(c, height, visual_config)
                c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
                c.setFillColor(HexColor(visual_config['colors']['text']))
                y_position = height - 160

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

    def add_linkedin_info(c, my_linkedin_link, visual_config_section):
        page_number = 2
        y_position, page_number = draw_entry_right(c, visual_config_section['text'], visual_config_section, visual_config_section['y_position'], page_number)

        c.setFillColor(HexColor(visual_config['colors']['link']))
        link_text = my_linkedin_link
        c.drawString(270, y_position, link_text)
        underline_y = y_position - 1
        link_width = c.stringWidth(link_text)
        c.line(270, underline_y, 270 + link_width, underline_y)
        c.linkURL(link_text, (270, y_position - 2, 270 + link_width, y_position + 12), relative=1)
        c.setFillColor(HexColor(visual_config['colors']['text']))

    c.setFillColor(HexColor(visual_config['colors']['text']))
    y_position = height - 160
    draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, y_position, page_number,
                     visual_config)

    y_position, page_number = draw_entry_right(c, personal_info["name"], visual_config['name_and_surname'], height - visual_config['name_and_surname']['y_top_minus'], page_number)
    y_position, page_number = draw_entry_right(c, summary_short, visual_config['summary_short'], height - visual_config['summary_short']['y_top_minus'], page_number)
    y_position, page_number = draw_entry_right(c, "Summary", visual_config['section_name'], height - visual_config['summary']['y_top_minus'], page_number)
    y_position, page_number = draw_entry_right(c, summary, visual_config['summary'], y_position - 10, page_number)

    #
    # y_position -= 210
    added_work_experience = False

    y_position, page_number, added_work_experience = draw_experience(experience[0], y_position - 20, page_number,
                                                                     added_work_experience)

    for job in experience[1:]:
        y_position, page_number, added_work_experience = draw_experience(job, y_position - 50, page_number,
                                                                         added_work_experience)

    linkedin_link = next((link['link'] for link in links if link['name'].lower() == 'linkedin'), None)
    if linkedin_link:
        add_linkedin_info(c, linkedin_link, visual_config['linkedin_more_info'])

    add_footer(c, page_number, visual_config)

    #
    # education and courses are always on separate page
    #
    c.showPage()
    page_number += 1
    draw_left_column_empty(c, height, visual_config)

    y_position, page_number = draw_entry_right(c, "Education", visual_config['section_name'], height - visual_config['education']['y_top_minus'], page_number)

    for edu in education:
        y_position, page_number = draw_education(edu, y_position, visual_config['education'], page_number)

    y_position, page_number = draw_entry_right(c, "Courses", visual_config['section_name'], y_position, page_number)


    for course in courses:
        y_position, page_number = draw_courses(course, y_position, page_number, first_page=True)

    draw_personal_data_info(c, personal_data_info, visual_config)

    add_footer(c, page_number, visual_config)

    c.save()


# Reading visual configuration from YAML file
with open("cv_visual_config.yaml", "r", encoding="utf-8") as v_config_file:
    visual_config = yaml.safe_load(v_config_file)

# Reading data from YAML file
with open("cv_data.yaml", "r", encoding="utf-8") as file:
    cv_data = yaml.safe_load(file)


# Removing Polish characters from the name
surname_and_name = cv_data['personal_info']['name']
pdf_filename = f"{unidecode.unidecode(surname_and_name).replace(' ', '_')}.pdf"

if os.path.isfile(pdf_filename):
    os.remove(pdf_filename)
    print(f"The Old {pdf_filename} has been removed.")

# Creating a PDF file with personal information, top skills, certificates, summary, languages, work experience, education, links, courses, and personal data info
create_cv(pdf_filename, cv_data, visual_config)

if os.path.isfile(pdf_filename):
    print(f"The new {pdf_filename} has been generated.")
