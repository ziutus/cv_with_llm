
Skrypt służy do generowania CV z wykorzystaniem danych z pliku YAML.


## CV PDF Generator

This project allows you to generate a professional CV in PDF format using data stored in a YAML file and customizable visual configurations. The script leverages the `reportlab` library for PDF generation and supports various configurations for styling and formatting.

## Key Features

- **YAML-Based Content**: Easily update the CV content by editing a human-readable YAML file.
- **Customizable Visuals**: Use a YAML configuration file to define fonts, colors, margins, and other visual aspects.
- **Automatic Layout**: Dynamically adjusts layout elements to fit in the PDF pages, handling page breaks and column alignments.

## Installation

Before generating your CV, ensure you have Python installed. The script requires the following Python packages:

- `PyYAML`
- `Pillow`
- `reportlab`

Install them using pip:

```bash
pip install PyYAML pillow reportlab
```

## Usage

1. **Prepare CV Data**: Create a YAML file with your CV details. Follow the provided structure to include sections like personal information, skills, experience, education, etc.
2. **Visual Configuration**: Create or modify a YAML file to define the visual layout and styling of your CV. Customize fonts, colors, margins, and sizes as needed.
3. **Generate PDF**: Run the script to generate the CV in PDF format.

### Command Line Interface

To generate the CV, use the command line as follows:

```bash
python main.py <company_identifier> --config <path_to_visual_config>
```

- `<company_identifier>`: Identifier used to locate your specific CV data file.
- `--config <path_to_visual_config>`: Path to the YAML file containing visual configuration. The default is `data/cv_visual_config.yaml`.

### Example

If your CV data file is named `data/cv_data_google.yaml` and you are using the default visual configuration:

```bash
python main.py google
```

### Visual Configuration

Here's an example of what a visual configuration YAML file may look like:

```yaml
fonts:
  default: ARIAL.TTF
  bold: ARIALBD.TTF
colors:
  text: "#000000"
  highlight: "#ff0000"
  footer: "#888888"
sizes:
  normal: 12
  small: 10
  large: 14
margins:
  top: 50
  bottom: 30
  left: 40
  right: 40
```

### CV Data

Here’s a snippet of how your CV data YAML file might look:

```yaml
personal_info:
  name: "John Doe"
  email: "john.doe@example.com"
  phone: "+123456789"
top_skills:
  - Python
  - Machine Learning
experience:
  - position: "Software Engineer"
    employer: "Google"
    period: "2018-2022"
    location: "Mountain View, CA"
    description: "Worked on developing scalable web applications..."

```

## Page Sizes

The standard size for a PDF page in A4 format is 210 × 297 mm. When using the ReportLab library,
this size is converted to points, with one inch equaling 72 points.

Thus, the dimensions of a PDF page in A4 format are:
* Width: 595 points (8.27 inches * 72 points per inch)
* Height: 842 points (11.69 inches * 72 points per inch)

If you use other page sizes, here are some standard dimensions in points (width x height):
* Letter: 612 × 792 points
* A4: 595 × 842 points
* Legal: 612 × 1008 points
* Tabloid: 792 × 1224 points

In the code, we use the `A4` variable from the ReportLab library, which defines the dimensions for the A4 format.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the script or add new features.

