from lxml import etree
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, XSD
from rdflib.namespace import DC, DCTERMS, FOAF, SKOS
from datetime import datetime

def tei_to_rdf(xml_file, output_file, base_uri="http://example.org/boxer_protocol/"):
    """
    Convert TEI XML document to RDF format
    
    Args:
        xml_file (str): Path to the input TEI XML file
        output_file (str): Path to the output RDF file (turtle format)
        base_uri (str): Base URI for RDF resources
    """
    
    # Initialize RDF graph
    g = Graph()
    
    # Define namespaces
    EX = Namespace(base_uri)
    SCHEMA = Namespace("http://schema.org/")
    CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    EDM = Namespace("http://www.europeana.eu/schemas/edm/")
    
    # Bind prefixes for readable output
    g.bind("ex", EX)
    g.bind("dc", DC)
    g.bind("dcterms", DCTERMS)
    g.bind("foaf", FOAF)
    g.bind("schema", SCHEMA)
    g.bind("skos", SKOS)
    g.bind("crm", CRM)
    g.bind("edm", EDM)
    
    # Define TEI namespace
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Parse XML file
    tree = etree.parse(xml_file)
    root = tree.getroot()
    
    # Create main document resource
    doc_uri = EX.ImperialEdict_1901_02_13
    
    # Add document type
    g.add((doc_uri, RDF.type, SCHEMA.HistoricalDocument))
    g.add((doc_uri, RDF.type, FOAF.Document))
    g.add((doc_uri, RDF.type, CRM.E31_Document))
    
    # Extract and add metadata
    try:
        title = root.xpath('//tei:titleStmt/tei:title/text()', namespaces=ns)[0]
        g.add((doc_uri, DC.title, Literal(title, lang="en")))
        g.add((doc_uri, DCTERMS.title, Literal(title, lang="en")))
    except:
        pass
    
    try:
        author = root.xpath('//tei:titleStmt/tei:author/text()', namespaces=ns)[0]
        author_uri = EX.QingImperialCourt
        g.add((author_uri, RDF.type, FOAF.Organization))
        g.add((author_uri, FOAF.name, Literal(author, lang="en")))
        g.add((doc_uri, DC.creator, author_uri))
        g.add((doc_uri, DCTERMS.creator, author_uri))
    except:
        pass
    
    try:
        date_str = root.xpath('//tei:publicationStmt/tei:date/@when', namespaces=ns)[0]
        g.add((doc_uri, DC.date, Literal(date_str, datatype=XSD.date)))
        g.add((doc_uri, DCTERMS.created, Literal(date_str, datatype=XSD.date)))
        g.add((doc_uri, SCHEMA.dateCreated, Literal(date_str, datatype=XSD.date)))
    except:
        pass
    
    try:
        pub_place = root.xpath('//tei:publicationStmt/tei:pubPlace/text()', namespaces=ns)[0]
        place_uri = EX.Beijing
        g.add((place_uri, RDF.type, SCHEMA.Place))
        g.add((place_uri, FOAF.name, Literal(pub_place, lang="en")))
        g.add((doc_uri, SCHEMA.locationCreated, place_uri))
    except:
        pass
    
    try:
        source_desc = root.xpath('//tei:sourceDesc/tei:p/text()', namespaces=ns)[0]
        g.add((doc_uri, DC.description, Literal(source_desc, lang="en")))
        g.add((doc_uri, DCTERMS.description, Literal(source_desc, lang="en")))
    except:
        pass
    
    # Add language
    g.add((doc_uri, DC.language, Literal("en")))
    g.add((doc_uri, DCTERMS.language, Literal("eng")))
    
    # Add subject/keywords
    keywords = root.xpath('//tei:keywords[@scheme="LCSH"]/tei:term/text()', namespaces=ns)
    for keyword in keywords:
        g.add((doc_uri, DC.subject, Literal(keyword, lang="en")))
        g.add((doc_uri, DCTERMS.subject, Literal(keyword, lang="en")))
    
    # Process persons from the back matter
    persons = root.xpath('//tei:listPerson/tei:person', namespaces=ns)
    for person in persons:
        person_id = person.get('{http://www.w3.org/XML/1998/namespace}id')
        person_uri = EX[person_id]
        
        # Add person type
        g.add((person_uri, RDF.type, FOAF.Person))
        g.add((person_uri, RDF.type, SCHEMA.Person))
        g.add((person_uri, RDF.type, CRM.E21_Person))
        
        # Add person name
        try:
            person_name = person.xpath('./tei:persName/text()', namespaces=ns)[0]
            g.add((person_uri, FOAF.name, Literal(person_name, lang="en")))
            g.add((person_uri, RDFS.label, Literal(person_name, lang="en")))
            g.add((person_uri, SCHEMA.name, Literal(person_name, lang="en")))
        except:
            pass
        
        # Add person description/note
        try:
            person_note = person.xpath('./tei:note/text()', namespaces=ns)[0]
            g.add((person_uri, RDFS.comment, Literal(person_note, lang="en")))
            g.add((person_uri, SCHEMA.description, Literal(person_note, lang="en")))
        except:
            pass
        
        # Link person to document
        g.add((doc_uri, SCHEMA.mentions, person_uri))
        g.add((doc_uri, CRM.P67_refers_to, person_uri))
    
    # Process places from the back matter
    places = root.xpath('//tei:listPlace/tei:place', namespaces=ns)
    for place in places:
        place_id = place.get('{http://www.w3.org/XML/1998/namespace}id')
        place_uri = EX[place_id]
        
        # Add place type
        g.add((place_uri, RDF.type, SCHEMA.Place))
        g.add((place_uri, RDF.type, CRM.E53_Place))
        
        # Add place name
        try:
            place_name = place.xpath('./tei:placeName/text()', namespaces=ns)[0]
            g.add((place_uri, FOAF.name, Literal(place_name, lang="en")))
            g.add((place_uri, RDFS.label, Literal(place_name, lang="en")))
            g.add((place_uri, SCHEMA.name, Literal(place_name, lang="en")))
        except:
            pass
        
        # Add coordinates if available
        try:
            coords = place.xpath('./tei:location/tei:geo/text()', namespaces=ns)[0]
            lat, lon = coords.split()
            g.add((place_uri, SCHEMA.latitude, Literal(float(lat), datatype=XSD.float)))
            g.add((place_uri, SCHEMA.longitude, Literal(float(lon), datatype=XSD.float)))
        except:
            pass
        
        # Add place description/note
        try:
            place_note = place.xpath('./tei:note/text()', namespaces=ns)[0]
            g.add((place_uri, RDFS.comment, Literal(place_note, lang="en")))
            g.add((place_uri, SCHEMA.description, Literal(place_note, lang="en")))
        except:
            pass
        
        # Link place to document
        g.add((doc_uri, SCHEMA.mentions, place_uri))
        g.add((doc_uri, CRM.P67_refers_to, place_uri))
    
    # Process organizations from the back matter
    orgs = root.xpath('//tei:listOrg/tei:org', namespaces=ns)
    for org in orgs:
        org_id = org.get('{http://www.w3.org/XML/1998/namespace}id')
        org_uri = EX[org_id]
        
        # Add organization type
        g.add((org_uri, RDF.type, FOAF.Organization))
        g.add((org_uri, RDF.type, SCHEMA.Organization))
        g.add((org_uri, RDF.type, CRM.E74_Group))
        
        # Add organization name
        try:
            org_name = org.xpath('./tei:orgName/text()', namespaces=ns)[0]
            g.add((org_uri, FOAF.name, Literal(org_name, lang="en")))
            g.add((org_uri, RDFS.label, Literal(org_name, lang="en")))
            g.add((org_uri, SCHEMA.name, Literal(org_name, lang="en")))
        except:
            pass
        
        # Add organization description/note
        try:
            org_note = org.xpath('./tei:note/text()', namespaces=ns)[0]
            g.add((org_uri, RDFS.comment, Literal(org_note, lang="en")))
            g.add((org_uri, SCHEMA.description, Literal(org_note, lang="en")))
        except:
            pass
        
        # Link organization to document
        g.add((doc_uri, SCHEMA.mentions, org_uri))
        g.add((doc_uri, CRM.P67_refers_to, org_uri))
    
    # Process punishments and create events
    punishments = root.xpath('//tei:div[@type="punishment"]', namespaces=ns)
    for idx, punishment in enumerate(punishments, 1):
        pun_num = punishment.get('n', str(idx))
        event_uri = EX[f"Punishment_{pun_num}"]
        
        # Add event type
        g.add((event_uri, RDF.type, SCHEMA.Event))
        g.add((event_uri, RDF.type, CRM.E5_Event))
        g.add((event_uri, RDFS.label, Literal(f"Punishment {pun_num}", lang="en")))
        
        # Extract text content for description
        text_parts = []
        for para in punishment.xpath('./tei:p', namespaces=ns):
            text_parts.append(''.join(para.itertext()))
        full_text = ' '.join(text_parts)
        
        g.add((event_uri, SCHEMA.description, Literal(full_text[:500], lang="en")))  # Truncate if too long
        
        # Link event to document
        g.add((doc_uri, SCHEMA.about, event_uri))
        g.add((event_uri, SCHEMA.isPartOf, doc_uri))
        
        # Extract and link persons mentioned in this punishment
        person_refs = punishment.xpath('.//tei:persName/@ref', namespaces=ns)
        for ref in person_refs:
            person_id = ref.replace('#', '')
            person_uri = EX[person_id]
            g.add((event_uri, SCHEMA.actor, person_uri))
            g.add((event_uri, CRM.P11_had_participant, person_uri))
    
    # Create relationships between entities based on document structure
    # Link historical event (Boxer Rebellion) to document
    boxer_event_uri = EX.BoxerRebellion
    g.add((boxer_event_uri, RDF.type, SCHEMA.Event))
    g.add((boxer_event_uri, RDF.type, CRM.E5_Event))
    g.add((boxer_event_uri, RDFS.label, Literal("Boxer Rebellion", lang="en")))
    g.add((boxer_event_uri, SCHEMA.startDate, Literal("1899", datatype=XSD.gYear)))
    g.add((boxer_event_uri, SCHEMA.endDate, Literal("1901", datatype=XSD.gYear)))
    g.add((doc_uri, SCHEMA.about, boxer_event_uri))
    
    # Link Boxers organization to the event
    boxers_uri = EX.boxers
    if (boxers_uri, None, None) in g:
        g.add((boxer_event_uri, SCHEMA.organizer, boxers_uri))
    
    # Add relation to Boxer Protocol
    protocol_uri = EX.BoxerProtocol
    g.add((protocol_uri, RDF.type, SCHEMA.HistoricalDocument))
    g.add((protocol_uri, RDFS.label, Literal("Boxer Protocol", lang="en")))
    g.add((protocol_uri, SCHEMA.dateCreated, Literal("1901-09-07", datatype=XSD.date)))
    g.add((doc_uri, DCTERMS.relation, protocol_uri))
    g.add((doc_uri, SCHEMA.relatedLink, protocol_uri))
    
    # Serialize to file
    g.serialize(destination=output_file, format='turtle')
    print(f"✓ RDF file successfully generated: {output_file}")
    print(f"✓ Total triples created: {len(g)}")
    
    # Also create RDF/XML version
    xml_output = output_file.replace('.ttl', '.rdf')
    g.serialize(destination=xml_output, format='xml')
    print(f"✓ RDF/XML file successfully generated: {xml_output}")
    
    return g


def print_rdf_statistics(graph):
    """
    Print statistics about the generated RDF graph
    
    Args:
        graph: RDFLib graph object
    """
    print("\n=== RDF Graph Statistics ===")
    print(f"Total triples: {len(graph)}")
    
    # Count by type
    persons = list(graph.subjects(RDF.type, FOAF.Person))
    places = list(graph.subjects(RDF.type, SCHEMA.Place))
    orgs = list(graph.subjects(RDF.type, FOAF.Organization))
    events = list(graph.subjects(RDF.type, SCHEMA.Event))
    
    print(f"Persons: {len(persons)}")
    print(f"Places: {len(places)}")
    print(f"Organizations: {len(orgs)}")
    print(f"Events: {len(events)}")
    print("============================\n")


# Usage example
if __name__ == "__main__":
    import os
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define file paths relative to script location
    xml_file = os.path.join(script_dir, 'boxer_protocol.xml')
    output_file = os.path.join(script_dir, 'boxer_protocol.ttl')
    
    # Convert TEI XML to RDF
    graph = tei_to_rdf(xml_file, output_file)
    
    # Print statistics
    print_rdf_statistics(graph)