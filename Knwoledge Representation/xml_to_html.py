from lxml import etree

def tei_to_html(xml_file, output_file):
    """
    Convert TEI XML document to HTML format
    
    Args:
        xml_file (str): Path to the input TEI XML file
        output_file (str): Path to the output HTML file
    """
    # Define TEI namespace
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Parse XML file
    tree = etree.parse(xml_file)
    root = tree.getroot()
    
    # Extract metadata from TEI header
    title = root.xpath('//tei:titleStmt/tei:title/text()', namespaces=ns)[0]
    author = root.xpath('//tei:titleStmt/tei:author/text()', namespaces=ns)[0]
    date = root.xpath('//tei:publicationStmt/tei:date/@when', namespaces=ns)[0]
    pub_place = root.xpath('//tei:publicationStmt/tei:pubPlace/text()', namespaces=ns)[0]
    
    # Start building HTML document
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.8;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.2rem;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .metadata {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        
        .metadata p {{
            margin: 8px 0;
            font-size: 1rem;
        }}
        
        .content {{
            padding: 50px 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            color: #667eea;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            font-weight: 600;
        }}
        
        .paragraph {{
            margin-bottom: 20px;
            text-align: justify;
            font-size: 1.05rem;
            color: #333;
        }}
        
        .person {{
            color: #e74c3c;
            font-weight: 600;
            cursor: help;
            border-bottom: 1px dotted #e74c3c;
        }}
        
        .person:hover {{
            background-color: #ffe6e6;
        }}
        
        .place {{
            color: #27ae60;
            font-weight: 600;
            cursor: help;
            border-bottom: 1px dotted #27ae60;
        }}
        
        .place:hover {{
            background-color: #e6ffe6;
        }}
        
        .org {{
            color: #2980b9;
            font-weight: 600;
            cursor: help;
            border-bottom: 1px dotted #2980b9;
        }}
        
        .org:hover {{
            background-color: #e6f2ff;
        }}
        
        .date {{
            color: #f39c12;
            font-weight: 600;
            font-style: italic;
        }}
        
        .punishment-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .punishment-number {{
            color: #667eea;
            font-weight: bold;
            font-size: 0.9rem;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .conclusion {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 30px;
            border-radius: 5px;
            margin-top: 40px;
        }}
        
        .index {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }}
        
        .index h3 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }}
        
        .index-list {{
            list-style: none;
            padding: 0;
        }}
        
        .index-list li {{
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 3px;
            font-size: 0.95rem;
        }}
        
        .index-list .name {{
            font-weight: 600;
            color: #333;
        }}
        
        .index-list .note {{
            color: #666;
            font-style: italic;
            margin-left: 10px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 0;
                border-radius: 0;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 1.5rem;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="metadata">
                <p><strong>Author:</strong> {author}</p>
                <p><strong>Date:</strong> {date}</p>
                <p><strong>Place:</strong> {pub_place}</p>
            </div>
        </div>
        
        <div class="content">
"""
    
    # Process body content
    body = root.xpath('//tei:text/tei:body', namespaces=ns)[0]
    
    # Process each section div
    for div in body.xpath('.//tei:div[@type="section"]', namespaces=ns):
        section_num = div.get('n', '')
        
        # Check if section has a heading
        head = div.xpath('./tei:head', namespaces=ns)
        if head:
            section_title = process_element_text(head[0], ns)
            html_content += f'<div class="section">\n'
            html_content += f'<h2 class="section-title">{section_title}</h2>\n'
        else:
            html_content += f'<div class="section">\n'
            if section_num:
                html_content += f'<h2 class="section-title">Section {section_num}</h2>\n'
        
        # Process paragraphs
        for para in div.xpath('./tei:p', namespaces=ns):
            para_text = process_element_text(para, ns)
            html_content += f'<p class="paragraph">{para_text}</p>\n'
        
        # Process punishment entries
        for punishment in div.xpath('./tei:div[@type="punishment"]', namespaces=ns):
            pun_num = punishment.get('n', '')
            html_content += f'<div class="punishment-box">\n'
            html_content += f'<div class="punishment-number">Punishment {pun_num}</div>\n'
            for para in punishment.xpath('./tei:p', namespaces=ns):
                para_text = process_element_text(para, ns)
                html_content += f'<p class="paragraph">{para_text}</p>\n'
            html_content += '</div>\n'
        
        html_content += '</div>\n'
    
    # Process conclusion section
    conclusion_div = body.xpath('.//tei:div[@type="conclusion"]', namespaces=ns)
    if conclusion_div:
        html_content += '<div class="conclusion">\n'
        for para in conclusion_div[0].xpath('./tei:p', namespaces=ns):
            para_text = process_element_text(para, ns)
            html_content += f'<p class="paragraph">{para_text}</p>\n'
        html_content += '</div>\n'
    
    # Add index sections
    html_content += '<div class="index">\n'
    
    # Index of Persons
    persons = root.xpath('//tei:listPerson/tei:person', namespaces=ns)
    if persons:
        html_content += '<h3>Index of Persons</h3>\n'
        html_content += '<ul class="index-list">\n'
        for person in persons:
            person_id = person.get('{http://www.w3.org/XML/1998/namespace}id')
            person_name = person.xpath('./tei:persName/text()', namespaces=ns)[0]
            note = person.xpath('./tei:note/text()', namespaces=ns)
            note_text = note[0] if note else ''
            html_content += f'<li><span class="name">{person_name}</span>'
            if note_text:
                html_content += f'<span class="note">- {note_text}</span>'
            html_content += '</li>\n'
        html_content += '</ul>\n'
    
    # Index of Places
    places = root.xpath('//tei:listPlace/tei:place', namespaces=ns)
    if places:
        html_content += '<h3>Index of Places</h3>\n'
        html_content += '<ul class="index-list">\n'
        for place in places:
            place_name = place.xpath('./tei:placeName/text()', namespaces=ns)[0]
            note = place.xpath('./tei:note/text()', namespaces=ns)
            note_text = note[0] if note else ''
            html_content += f'<li><span class="name">{place_name}</span>'
            if note_text:
                html_content += f'<span class="note">- {note_text}</span>'
            html_content += '</li>\n'
        html_content += '</ul>\n'
    
    # Index of Organizations
    orgs = root.xpath('//tei:listOrg/tei:org', namespaces=ns)
    if orgs:
        html_content += '<h3>Index of Organizations</h3>\n'
        html_content += '<ul class="index-list">\n'
        for org in orgs:
            org_name = org.xpath('./tei:orgName/text()', namespaces=ns)[0]
            note = org.xpath('./tei:note/text()', namespaces=ns)
            note_text = note[0] if note else ''
            html_content += f'<li><span class="name">{org_name}</span>'
            if note_text:
                html_content += f'<span class="note">- {note_text}</span>'
            html_content += '</li>\n'
        html_content += '</ul>\n'
    
    html_content += '</div>\n'
    
    # Close HTML tags
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML file successfully generated: {output_file}")


def process_element_text(element, ns):
    """
    Process element text content, including converting internal tags
    
    Args:
        element: XML element to process
        ns: Namespace dictionary
    
    Returns:
        str: Processed HTML text with semantic markup
    """
    result = element.text or ''
    
    for child in element:
        if child.tag == '{http://www.tei-c.org/ns/1.0}persName':
            person_ref = child.get('ref', '').replace('#', '')
            person_text = child.text or ''
            result += f'<span class="person" title="Person ID: {person_ref}">{person_text}</span>'
        elif child.tag == '{http://www.tei-c.org/ns/1.0}placeName':
            place_ref = child.get('ref', '').replace('#', '')
            place_text = child.text or ''
            result += f'<span class="place" title="Place ID: {place_ref}">{place_text}</span>'
        elif child.tag == '{http://www.tei-c.org/ns/1.0}orgName':
            org_ref = child.get('ref', '').replace('#', '')
            org_text = child.text or ''
            result += f'<span class="org" title="Organization ID: {org_ref}">{org_text}</span>'
        elif child.tag == '{http://www.tei-c.org/ns/1.0}date':
            date_when = child.get('when', '')
            date_text = child.text or ''
            result += f'<span class="date" title="{date_when}">{date_text}</span>'
        else:
            result += child.text or ''
        
        result += child.tail or ''
    
    return result


if __name__ == "__main__":
    tei_to_html(
        r'C:\Users\linzi\Desktop\Tomasi project\Knwoledge Representation\boxer_protocol.xml',
        r'C:\Users\linzi\Desktop\Tomasi project\Knwoledge Representation\boxer_protocol.html'
    )