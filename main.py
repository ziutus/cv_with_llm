import unidecode
import yaml
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from PIL import Image, ImageDraw
import textwrap


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


def create_cv(filename, personal_info, top_skills, certificates, languages, summary, summary_short, experience,
              education, links, courses, personal_data_info, visual_config):
    c = canvas.Canvas(filename, pagesize=A4)

    pdfmetrics.registerFont(TTFont(visual_config['fonts']['default'], 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont(visual_config['fonts']['bold'], 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont(visual_config['fonts']['italic'], 'DejaVuSans-Oblique.ttf'))
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])

    width, height = A4
    page_number = 1
    y_offset = 50

    def draw_name_left(c, personal_info_left, summary_short_left):
        c.setFillColor(HexColor(visual_config['colors']['text']))
        c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['title'])
        c.drawString(270, height - 100, personal_info_left["name"])
        c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])

        c.setFillColor(HexColor(visual_config['colors']['grey_background']))
        y_position = height - 130
        summary_lines_left = textwrap.wrap(summary_short_left, width=55)
        for line in summary_lines_left:
            c.drawString(270, y_position, line)
            y_position -= 15

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
                draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, height - 160,
                                 page_number, visual_config)
                c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
                c.setFillColor(HexColor(visual_config['colors']['text']))
                y_position = height - 160

        return y_position, page_number, added_work_experience

    def draw_education(edu, y_position, page_number, first_page=False):
        if not first_page or (first_page and y_position != height - 200):
            c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['normal'])
            c.drawString(270, y_position, edu["school"])
            y_position -= 20
            c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
            c.drawString(270, y_position, f'{edu["degree"]}, {edu["field_of_study"]}')
            y_position -= 20
            c.drawString(270, y_position, edu["years"])
            y_position -= 30

            if y_position < y_offset:
                add_footer(c, page_number, visual_config)
                c.showPage()
                page_number += 1
                draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, height - 160,
                                 page_number, visual_config)
                c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
                c.setFillColor(HexColor(visual_config['colors']['text']))
                y_position = height - 160

        return y_position, page_number

    def draw_courses(course, y_position, page_number, first_page=False):
        if not first_page or (first_page and y_position != height - 200):
            c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
            year_text = str(course["year"])
            course_text = f"{year_text} - {course['name']}"

            if "link" in course and course["link"]:
                link_text = " (link)"
                course_text_with_link = course_text + link_text
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
                draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, height - 160,
                                 page_number, visual_config)
                c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
                c.setFillColor(HexColor(visual_config['colors']['text']))
                y_position = height - 160

        return y_position, page_number

    def draw_personal_data_info(c, y_position, personal_data, visual_config_section):
        pd_config = visual_config_section['personal_data_info']
        width = pd_config['width']  # Pobranie szerokości tekstu
        font = pd_config['font']  # Pobranie czcionki
        font_size = pd_config['font_size']  # Pobranie rozmiaru czcionki
        color = pd_config['color']  # Pobranie koloru tekstu

        c.setFont(font, font_size)
        c.setFillColor(HexColor(color))

        y_position = 90
        footer_margin = 50
        wrapped_info_lines = textwrap.wrap(personal_data, width=width)  # Użyj szerokości z pliku konfiguracyjnego

        for personal_line in wrapped_info_lines:
            c.drawString(270, y_position, personal_line)
            y_position -= 10

        return y_position

    def add_linkedin_info(c, y_position, my_linkedin_link):
        info_text = "You can find more information about my experience on my LinkedIn profile:"
        c.setFont(visual_config['fonts']['default'], visual_config['sizes']['small'])
        c.setFillColor(HexColor(visual_config['colors']['link']))
        c.drawString(270, y_position, info_text)
        y_position -= 15
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
    draw_name_left(c, personal_info, summary_short)

    y_position = height - 200
    c.setFillColor(HexColor(visual_config['colors']['text']))
    c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['subtitle'])
    c.drawString(270, y_position, "Summary")
    y_position -= 20
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
    summary_lines = textwrap.wrap(summary, width=53)
    for line in summary_lines:
        c.drawString(270, y_position, line)
        y_position -= 15

    y_position -= 20
    added_work_experience = False

    y_position, page_number, added_work_experience = draw_experience(experience[0], y_position - 20, page_number,
                                                                     added_work_experience)

    for job in experience[1:]:
        y_position, page_number, added_work_experience = draw_experience(job, y_position - 50, page_number,
                                                                         added_work_experience)

    linkedin_link = next((link['link'] for link in links if link['name'].lower() == 'linkedin'), None)
    if linkedin_link:
        y_position -= 30
        add_linkedin_info(c, y_position, linkedin_link)
        y_position -= 30

    add_footer(c, page_number, visual_config)
    c.showPage()
    page_number += 1
    draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, y_position, page_number,
                     visual_config)
    c.setFont(visual_config['fonts']['default'], visual_config['sizes']['normal'])
    y_position = height - 50
    c.setFillColor(HexColor(visual_config['colors']['text']))

    c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['subtitle'])
    c.drawString(270, y_position, "Education")
    y_position -= 30

    for edu in education:
        y_position, page_number = draw_education(edu, y_position, page_number, first_page=True)

    y_position -= 30
    c.setFont(visual_config['fonts']['bold'], visual_config['sizes']['subtitle'])
    c.drawString(270, y_position, "Courses")
    y_position -= 20

    for course in courses:
        y_position, page_number = draw_courses(course, y_position, page_number, first_page=True)

    y_position = draw_personal_data_info(c, y_position, personal_data_info, visual_config)

    add_footer(c, page_number, visual_config)

    c.save()


# Reading visual configuration from YAML file
with open("cv_visual_config.yaml", "r", encoding="utf-8") as v_config_file:
    visual_config = yaml.safe_load(v_config_file)

# Reading data from YAML file
with open("cv_data.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)
    personal_info = data.get("personal_info", {})
    top_skills = data.get("top_skills", [])
    certificates = data.get("certificates", [])
    languages = data.get("languages", [])
    summary = data.get("summary", "")
    summary_short = data.get("summary_short", "")
    experience = data.get("experience", [])
    education = data.get("education", [])
    links = data.get("links", [])
    courses = data.get("courses", [])
    personal_data_info = data.get("personal_data_info", "")

# Removing Polish characters from the name
name = unidecode.unidecode(personal_info["name"])

# Creating a PDF file with personal information, top skills, certificates, summary, languages, work experience, education, links, courses, and personal data info
pdf_filename = f"{name.replace(' ', '_')}.pdf"
create_cv(pdf_filename, personal_info, top_skills, certificates, languages, summary, summary_short, experience,
          education, links, courses, personal_data_info, visual_config)
