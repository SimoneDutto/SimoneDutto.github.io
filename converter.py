import csv
import os

def convert_to_markdown(csv_file, output_folder):
    markdown_template = '''---
layout: book
title: "{title}"
author_first_name: "{author_first_name}"
author_last_name: "{author_last_name}"
cover_url: "/assets/images/book-cover-placeholder.jpg"
year: {year}
---'''

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            date_added = row['Date Added']
            if date_added.startswith('2023'):
                title = row['Title']
                author_first_name = row['Author'].split(',')[0]
                author_last_name = row['Author l-f'].split(',')[0]
                year = row['Date Added'].split("/")[0]
                markdown = markdown_template.format(
                    title=title,
                    author_first_name=author_first_name,
                    author_last_name=author_last_name,
                    year=year
                )
                output_file = os.path.join(output_folder, f"{title.replace(' ', '_')}.md")
                with open(output_file, 'w', encoding='utf-8') as out_file:
                    out_file.write(markdown)

# Example usage:
convert_to_markdown('books.csv', '_books')
