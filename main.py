import unidecode
import yaml
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import grey, white, black, darkgrey, HexColor
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


def add_footer(c, page_num):
    """Adds a footer with the page number."""
    width, height = A4
    c.setFont('DejaVuSans', 10)
    c.setFillColor(grey)
    footer_text = f"Page {page_num}"
    c.drawString((width / 2) - 20, 30, footer_text)


def draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, y_start, page_number):
    """Draws the left column with personal data, top skills, certificates, languages, and links."""

    # Drawing left column with grey background
    column_width = 200  # Adjusted width of the left column

    c.setFillColor(grey)
    c.rect(50, 50, column_width, height - 100, stroke=0, fill=1)

    if page_number == 1:
        c.setFillColor(white)

        # Path to the round photo
        photo_path = 'photo.jpg'
        round_photo_path = 'round_photo.png'
        create_round_mask(photo_path, round_photo_path, size=(int(column_width) - 20, int(column_width) - 20))
        # Position the photo so that it is entirely within the grey column
        c.drawImage(round_photo_path, 50, height - (int(column_width) + 50), width=column_width, height=column_width,
                    mask='auto')

        # Smaller font for left column
        c.setFont('DejaVuSans', 10)

        y_position = height - (int(column_width) + 70)
        c.drawString(60, y_position, f"Email: {personal_info['email']}")
        y_position -= 20
        c.drawString(60, y_position, f"Phone: {personal_info['phone']}")

        # Adding links section without a heading
        y_position -= 30
        for link in links:
            cleaned_link = link['link'].replace("https://", "").replace("http://", "")
            link_name_text = f" ({link['name']})"

            # Combine link and its description so that they do not exceed the grey background
            full_link_text = cleaned_link + link_name_text
            wrapped_link_lines = textwrap.wrap(full_link_text, width=36)  # Adjust width to fit within the grey box

            for line in wrapped_link_lines:
                # Check if we are dealing with the link text or its description
                if line.endswith(link_name_text):
                    link_part = line[:-len(link_name_text)]
                    c.setFillColor(white)
                    c.drawString(60, y_position, link_part)
                    c.setFillColor(darkgrey)
                    c.drawString(60 + c.stringWidth(link_part), y_position, link_name_text)
                else:
                    c.setFillColor(white)
                    c.drawString(60, y_position, line)
                y_position -= 12  # Decrease vertical spacing between links

        # Setting white color for top skills
        y_position -= 20  # Add some space before the top skills section
        c.setFont('DejaVuSans-Bold', 10)
        c.setFillColor(white)
        c.drawString(60, y_position, "Top Skills")
        c.setFont('DejaVuSans', 10)

        y_position -= 20
        for skill in top_skills:
            c.drawString(60, y_position, u"\u2022 " + skill)
            y_position -= 20

        # Adding Certificates section
        y_position -= 20  # Add some space before the certificates section
        c.setFont('DejaVuSans-Bold', 10)
        c.setFillColor(white)
        c.drawString(60, y_position, "Certificates")
        c.setFont('DejaVuSans', 10)

        y_position -= 20
        for certificate in certificates:
            c.drawString(60, y_position, u"\u2022 " + certificate)
            y_position -= 20

        # Adding Languages section
        y_position -= 20  # Add some space before the languages section
        c.setFont('DejaVuSans-Bold', 10)
        c.setFillColor(white)
        c.drawString(60, y_position, "Languages")
        c.setFont('DejaVuSans', 10)

        y_position -= 20
        for language in languages:
            c.drawString(60, y_position, u"\u2022 " + language)
            y_position -= 20


def create_cv(filename, personal_info, top_skills, certificates, languages, summary, summary_short, experience,
              education, links, courses, personal_data_info):
    c = canvas.Canvas(filename, pagesize=A4)

    # Registering TrueType font
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'DejaVuSans-Oblique.ttf'))  # Registering Italic font
    c.setFont('DejaVuSans', 12)

    width, height = A4
    page_number = 1
    y_offset = 50  # Bottom margin

    # Function to draw the name in the top left corner of the right column
    def draw_name_left(c, personal_info, summary_short):
        c.setFillColor(black)  # Change font color to black
        c.setFont('DejaVuSans-Bold', 24)
        c.drawString(270, height - 100, personal_info["name"])
        c.setFont('DejaVuSans', 12)

        # Drawing the summary_short
        c.setFillColor(grey)
        y_position = height - 130
        summary_lines = textwrap.wrap(summary_short, width=55)  # Adjust the width to fit within the right column
        for line in summary_lines:
            c.drawString(270, y_position, line)
            y_position -= 15

    def draw_experience(job, y_position, page_number, added_work_experience):
        """Draws a single entry in the work experience section."""

        if not added_work_experience:
            if y_position != height - 200:
                c.setFont('DejaVuSans-Bold', 16)
                c.drawString(270, y_position, "Work Experience")
                y_position -= 20
                added_work_experience = True

        c.setFont('DejaVuSans-Bold', 12)
        c.drawString(270, y_position, job["employer"])
        y_position -= 20
        c.setFont('DejaVuSans-Oblique', 12)  # Italic font for position
        c.drawString(270, y_position, job["position"])
        y_position -= 20
        c.setFont('DejaVuSans', 12)  # Return to regular font
        c.drawString(270, y_position, job["period"])
        y_position -= 20
        c.drawString(270, y_position, job["location"])
        y_position -= 20

        description_lines = textwrap.wrap(job["description"], width=60)
        for line in description_lines:
            c.drawString(270, y_position, line)
            y_position -= 15

            if y_position < y_offset:  # Adding a new page if there's no space
                add_footer(c, page_number)
                c.showPage()
                page_number += 1
                draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, height - 160,
                                 page_number)
                c.setFont('DejaVuSans', 12)
                c.setFillColor(black)  # Returning font color to black
                y_position = height - 160  # Reset y_position for new page

        return y_position, page_number, added_work_experience

    def draw_education(edu, y_position, page_number, first_page=False):
        """Draws a single entry in the education section."""

        if not first_page or (first_page and y_position != height - 200):
            c.setFont('DejaVuSans-Bold', 12)
            c.drawString(270, y_position, edu["school"])
            y_position -= 20
            c.setFont('DejaVuSans', 12)
            c.drawString(270, y_position, f'{edu["degree"]}, {edu["field_of_study"]}')
            y_position -= 20
            c.drawString(270, y_position, edu["years"])
            y_position -= 30  # To add some space after each education entry

            if y_position < y_offset:  # Adding a new page if there's no space
                add_footer(c, page_number)
                c.showPage()
                page_number += 1
                draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, height - 160,
                                 page_number)
                c.setFont('DejaVuSans', 12)
                c.setFillColor(black)  # Returning font color to black
                y_position = height - 160  # Reset y_position for new page

        return y_position, page_number

    def draw_courses(course, y_position, page_number, first_page=False):
        """Draws a single entry in the courses section."""

        if not first_page or (first_page and y_position != height - 200):
            c.setFont('DejaVuSans', 12)  # Normal font for course name and year
            year_text = str(course["year"])
            course_text = f"{year_text} - {course['name']}"

            # Check if there is a link in the course entry
            if "link" in course and course["link"]:
                # Set font color to blue for link and underline it
                link_text = " (link)"
                course_text_with_link = course_text + link_text

                # Draw course text in black
                c.drawString(270, y_position, course_text)

                # Draw link text in blue with underline
                c.setFillColorRGB(0, 0, 1)  # Set font color to blue
                link_start_x = 270 + c.stringWidth(course_text)
                c.drawString(link_start_x, y_position, link_text)
                underline_y = y_position - 1  # Position for underline
                link_width = c.stringWidth(link_text)
                c.line(link_start_x, underline_y, link_start_x + link_width, underline_y)  # Underline the text
                c.linkURL(course["link"], (link_start_x, y_position - 2, link_start_x + link_width, y_position + 12),
                          relative=1)
                c.setFillColor(black)  # Return font color to black after drawing the link
            else:
                c.drawString(270, y_position, course_text)

            y_position -= 15  # Add some space after each course entry

            if y_position < y_offset:  # Adding a new page if there's no space
                add_footer(c, page_number)
                c.showPage()
                page_number += 1
                draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, height - 160,
                                 page_number)
                c.setFont('DejaVuSans', 12)
                c.setFillColor(black)  # Returning font color to black
                y_position = height - 160  # Reset y_position for new page

        return y_position, page_number

    def draw_personal_data_info(c, y_position, personal_data_info):
        """Draws the personal data information text at the bottom of the last page."""
        c.setFont('DejaVuSans', 8)
        c.setFillColor(HexColor('#0000FF'))  # Blue color

        y_position = 90  # Position near the bottom of the page
        footer_margin = 50
        wrapped_info_lines = textwrap.wrap(personal_data_info, width=80)  # Adjust the width to fit within the column

        for line in wrapped_info_lines:
            c.drawString(270, y_position, line)
            y_position -= 10

        return y_position

    def add_linkedin_info(c, y_position, linkedin_link):
        """Adds LinkedIn information at the end of the second page."""
        info_text = "You can find more information about my experience on my LinkedIn profile:"
        c.setFont('DejaVuSans', 10)
        c.setFillColor(HexColor('#0000FF'))  # Blue color
        c.drawString(270, y_position, info_text)
        y_position -= 15
        c.setFillColorRGB(0, 0, 1)  # Set font color to blue
        link_text = linkedin_link
        c.drawString(270, y_position, link_text)
        underline_y = y_position - 1  # Position for underline
        link_width = c.stringWidth(link_text)
        c.line(270, underline_y, 270 + link_width, underline_y)  # Underline the text
        c.linkURL(link_text, (270, y_position - 2, 270 + link_width, y_position + 12), relative=1)
        c.setFillColor(black)  # Return font color to black after drawing the link

    # First page
    c.setFillColor(black)
    y_position = height - 160
    draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, y_position, page_number)
    draw_name_left(c, personal_info, summary_short)

    # Draw the summary
    y_position = height - 200
    c.setFillColor(black)
    c.setFont('DejaVuSans-Bold', 16)
    c.drawString(270, y_position, "Summary")
    y_position -= 20
    c.setFont('DejaVuSans', 12)
    summary_lines = textwrap.wrap(summary, width=53)  # Adjust the width to fit within the right column
    for line in summary_lines:
        c.drawString(270, y_position, line)
        y_position -= 15

    # Work Experience title below the summary (only on first page)
    y_position -= 20
    added_work_experience = False

    y_position, page_number, added_work_experience = draw_experience(experience[0], y_position - 20, page_number,
                                                                     added_work_experience)

    for job in experience[1:]:
        y_position, page_number, added_work_experience = draw_experience(job, y_position - 50, page_number,
                                                                         added_work_experience)

    # Ensure LinkedIn info is added immediately after the experience ends on the second page
    linkedin_link = next((link['link'] for link in links if link['name'].lower() == 'linkedin'), None)
    if linkedin_link:
        y_position -= 30  # Adjust the vertical spacing before the LinkedIn section
        add_linkedin_info(c, y_position, linkedin_link)
        y_position -= 30  # Adjust the vertical spacing after the LinkedIn section

    # Ensure Education starts at the top of a new page
    add_footer(c, page_number)
    c.showPage()
    page_number += 1
    draw_left_column(c, personal_info, top_skills, certificates, languages, links, height, y_position, page_number)
    c.setFont('DejaVuSans', 12)
    y_position = height - 50
    c.setFillColor(black)

    # Education title at the beginning of the new page
    c.setFont('DejaVuSans-Bold', 16)
    c.drawString(270, y_position, "Education")
    y_position -= 30

    for edu in education:
        y_position, page_number = draw_education(edu, y_position, page_number, first_page=True)

    # Courses title
    y_position -= 30
    c.setFont('DejaVuSans-Bold', 16)
    c.drawString(270, y_position, "Courses")
    y_position -= 20

    for course in courses:
        y_position, page_number = draw_courses(course, y_position, page_number, first_page=True)

    # Draw personal data info at the bottom of the last page
    y_position = draw_personal_data_info(c, y_position, personal_data_info)

    # Adding footer with page number on each page
    add_footer(c, page_number)

    c.save()


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
          education, links, courses, personal_data_info)
