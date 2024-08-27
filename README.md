Skrypt służy do generowania CV z wykorzystaniem danych z pliku YAML.

## Rozmiary stron

Standardowy rozmiar strony PDF w formacie A4 wynosi 210 × 297 mm. W przypadku korzystania z biblioteki ReportLab,
rozmiar ten jest przeliczany na punkty, przy czym jeden cal odpowiada 72 punktom.

Tak więc wymiary strony PDF w formacie A4 wynoszą:
* Szerokość: 595 punktów (8.27 cala * 72 punkty na cal)
* Wysokość: 842 punkty (11.69 cala * 72 punkty na cal)

Jeżeli używasz innych rozmiarów stron, oto kilka standardowych wymiarów w punktach (width x height):
* Letter: 612 × 792 punktów
* A4: 595 × 842 punktów
* Legal: 612 × 1008 punktów
* Tabloid: 792 × 1224 punktów

W kodzie używamy zmiennej `A4` z biblioteki ReportLab, która definiuje wymiary dla formatu A4.

