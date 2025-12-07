#!/usr/bin/env python3
"""
LODLAM Project - CSV to RDF Converter
Converts multiple CSV files containing triples to RDF format
"""

import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, DCTERMS, FOAF, XSD, OWL
import re
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define namespaces
EX = Namespace("http://example.org/lodlam/")
SCHEMA = Namespace("http://schema.org/")
EDM = Namespace("http://www.europeana.eu/schemas/edm/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

# List of CSV files to process
CSV_FILES = [
    "1__Admonitions_of_the_Instructress_to_Court_Ladies.csv",
    "2__Brush_Holder.csv",
    "3__Boxer_Protocol.csv",
    "4__Summer_Palace_Grounds_Photograph.csv",
    "5__Throne.csv",
    "6__Grand_Porcelain_Tower_Stereograph.csv",
    "7__Jewelry.csv",
    "8__Longevity_Mountain_Carving.csv",
    "9__Longevity_Mountain_Stereograph.csv",
    "10__Beautiful_Winding_Corridor.csv"
]

def clean_uri_string(text):
    """
    Clean text to create valid URI components
    Replace spaces with underscores, remove special characters
    """
    # Remove parentheses and replace spaces
    text = re.sub(r'[(),]', '', str(text))
    text = text.replace(' ', '_')
    # Remove any other problematic characters
    text = re.sub(r'[^\w\-_.]', '', text)
    return text

def create_uri(text):
    """
    Convert text to a valid URI
    If text is already a URL, return as URIRef
    Otherwise, create a URI in the example namespace
    """
    text_str = str(text).strip()
    
    # Check if it's already a URL
    if text_str.startswith("http://") or text_str.startswith("https://"):
        return URIRef(text_str)
    
    # Create URI from text
    clean_text = clean_uri_string(text_str)
    return EX[clean_text]

def parse_property(property_string):
    """
    Parse property string and return appropriate namespace term
    Handles prefixed properties like 'dcterms:creator' or 'rdf:type'
    """
    # Mapping of common prefixes to their namespaces
    namespace_map = {
        'rdf': RDF,
        'rdfs': RDFS,
        'dcterms': DCTERMS,
        'dc': DC,
        'foaf': FOAF,
        'schema': SCHEMA,
        'edm': EDM,
        'crm': CRM,
        'owl': OWL,
        'ex': EX
    }
    
    property_str = str(property_string).strip()
    
    # Check if property has a prefix
    if ':' in property_str:
        prefix, local_name = property_str.split(':', 1)
        prefix_lower = prefix.lower()
        
        # Get the appropriate namespace
        if prefix_lower in namespace_map:
            ns = namespace_map[prefix_lower]
            return ns[local_name]
        else:
            # Unknown prefix, use example namespace
            return EX[property_str.replace(':', '_')]
    else:
        # No prefix, use example namespace
        return EX[property_str]

def is_literal_value(value):
    """
    Determine if a value should be treated as a literal
    Returns True if value appears to be descriptive text, dates, or measurements
    """
    value_str = str(value).lower()
    
    # Check for date/time indicators
    if any(indicator in value_str for indicator in 
           ['century', 'dynasty', 'period', 'year', 'ad', 'bc', '-']):
        return True
    
    # Check for measurements
    if any(unit in value_str for unit in 
           ['cm', 'mm', 'inch', 'meter', 'kg', '×']):
        return True
    
    # Check if it's a number
    try:
        float(value)
        return True
    except:
        pass
    
    # Check for descriptive phrases
    if any(word in value_str for word in 
           ['made of', 'consists of', 'located at', 'depicts', 'shows', 
            'approximately', 'height', 'width', 'print', 'photograph']):
        return True
    
    return False

def should_be_uri(value):
    """
    Determine if a value should be a URI (entity) rather than a literal
    Entities are proper nouns, names, locations, etc.
    """
    value_str = str(value).strip()
    
    # Already a URL
    if value_str.startswith('http'):
        return True
    
    # Check if it looks like a proper noun (starts with capital)
    # and doesn't contain literal indicators
    if value_str and value_str[0].isupper() and not is_literal_value(value):
        return True
    
    return False

def csv_to_rdf(csv_files, output_file="lodlam_dataset.ttl"):
    """
    Main function to convert CSV files to RDF
    
    Args:
        csv_files: List of CSV file paths
        output_file: Output file name for RDF data
    
    Returns:
        rdflib.Graph object containing all triples
    """
    # Initialize RDF graph
    g = Graph()
    
    # Bind namespaces for cleaner output
    g.bind("ex", EX)
    g.bind("dcterms", DCTERMS)
    g.bind("dc", DC)
    g.bind("foaf", FOAF)
    g.bind("schema", SCHEMA)
    g.bind("edm", EDM)
    g.bind("crm", CRM)
    g.bind("owl", OWL)
    
    print("=" * 60)
    print("LODLAM Project - CSV to RDF Conversion")
    print("=" * 60)
    
    total_triples = 0
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"\nProcessing: {csv_file}")
        
        # Create full path to the file
        file_path = os.path.join(SCRIPT_DIR, csv_file)
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Verify required columns exist
            if not all(col in df.columns for col in ['Subject', 'Property', 'Object']):
                print(f"  ERROR: Missing required columns in {csv_file}")
                continue
            
            file_triples = 0
            
            # Process each row (each triple)
            for idx, row in df.iterrows():
                try:
                    # Get subject (always a URI)
                    subject = create_uri(row['Subject'])
                    
                    # Get predicate (property)
                    predicate = parse_property(row['Property'])
                    
                    # Get object (could be URI or Literal)
                    obj_value = row['Object']
                    
                    # Determine if object should be URI or Literal
                    if should_be_uri(obj_value):
                        obj = create_uri(obj_value)
                    else:
                        # Create literal with appropriate datatype
                        if isinstance(obj_value, (int, float)):
                            obj = Literal(obj_value, datatype=XSD.integer if isinstance(obj_value, int) else XSD.float)
                        else:
                            obj = Literal(str(obj_value))
                    
                    # Add triple to graph
                    g.add((subject, predicate, obj))
                    file_triples += 1
                    
                except Exception as e:
                    print(f"  WARNING: Error processing row {idx}: {e}")
                    continue
            
            print(f"  Successfully added {file_triples} triples")
            total_triples += file_triples
            
        except Exception as e:
            print(f"  ERROR: Could not read file {csv_file}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"Conversion complete!")
    print(f"Total triples added: {total_triples}")
    print("=" * 60)
    
    # Create full path for output file
    output_path = os.path.join(SCRIPT_DIR, output_file)
    
    # Serialize to Turtle format (primary format)
    print(f"\nSaving RDF data to Turtle format...")
    g.serialize(destination=output_path, format='turtle', encoding='utf-8')
    print(f"  ✓ Turtle format saved: {output_file}")
    
    return g

def export_rdf_xml(graph):
    """
    Export RDF graph to RDF/XML format
    """
    print("\nExporting to RDF/XML format...")
    
    try:
        # Create full path for output file
        output_path = os.path.join(SCRIPT_DIR, 'lodlam_dataset.rdf')
        graph.serialize(destination=output_path, format='xml', encoding='utf-8')
        print(f"  ✓ RDF/XML format saved: lodlam_dataset.rdf")
    except Exception as e:
        print(f"  ✗ RDF/XML export failed: {e}")

def print_sample_triples(graph, num_triples=10):
    """
    Print sample triples from the graph
    """
    print(f"\n--- Sample Triples (first {num_triples}) ---")
    for i, (s, p, o) in enumerate(graph):
        if i >= num_triples:
            break
        print(f"{i+1}. <{s}> <{p}> <{o}>")

def generate_statistics(graph):
    """
    Generate and print statistics about the RDF graph
    """
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    
    # Count unique subjects, predicates, objects
    subjects = set(s for s, _, _ in graph)
    predicates = set(p for _, p, _ in graph)
    objects = set(o for _, _, o in graph)
    
    print(f"Total triples: {len(graph)}")
    print(f"Unique subjects: {len(subjects)}")
    print(f"Unique predicates: {len(predicates)}")
    print(f"Unique objects: {len(objects)}")
    
    print("\nPredicates used:")
    predicate_counts = {}
    for _, p, _ in graph:
        p_str = str(p)
        predicate_counts[p_str] = predicate_counts.get(p_str, 0) + 1
    
    for pred, count in sorted(predicate_counts.items(), key=lambda x: x[1], reverse=True):
        # Show just the local name for readability
        local_name = pred.split('/')[-1].split('#')[-1]
        print(f"  {local_name}: {count}")

if __name__ == "__main__":
    # Print working directory for debugging
    print(f"Script location: {SCRIPT_DIR}")
    print(f"Looking for CSV files in: {SCRIPT_DIR}\n")
    
    # Convert CSV files to RDF
    rdf_graph = csv_to_rdf(CSV_FILES)
    
    # Export to RDF/XML format
    export_rdf_xml(rdf_graph)
    
    # Print sample triples
    print_sample_triples(rdf_graph)
    
    # Generate statistics
    generate_statistics(rdf_graph)
    
    print("\n" + "=" * 60)
    print("All files generated successfully!")
    print("=" * 60)
    print("\nOutput files:")
    print("  • lodlam_dataset.ttl (Turtle format - primary)")
    print("  • lodlam_dataset.rdf (RDF/XML format - standard)")
