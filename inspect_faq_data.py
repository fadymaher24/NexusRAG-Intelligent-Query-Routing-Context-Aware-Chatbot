#!/usr/bin/env python3
"""
Inspect FAQ data from faq.joblib file.
Shows all FAQs, search by keyword, filter by type, etc.
"""

import joblib
from pathlib import Path
import json
import sys


def load_faq_data():
    """Load FAQ data from joblib file."""
    data_path = Path(__file__).parent / "dataset" / "faq.joblib"
    
    if not data_path.exists():
        print(f"❌ Error: FAQ file not found at {data_path}")
        return None
    
    print(f"📂 Loading FAQs from: {data_path}")
    faqs = joblib.load(data_path)
    print(f"✅ Loaded {len(faqs)} FAQs\n")
    return faqs


def show_all_faqs(faqs):
    """Display all FAQs."""
    print("="*70)
    print("ALL FAQs")
    print("="*70)
    
    for i, faq in enumerate(faqs, 1):
        print(f"\n{i}. Q: {faq.get('question', 'N/A')}")
        print(f"   A: {faq.get('answer', 'N/A')}")
        print(f"   Type: {faq.get('type', 'N/A')}")
        print("-" * 70)


def show_summary(faqs):
    """Show summary statistics."""
    print("="*70)
    print("FAQ SUMMARY")
    print("="*70)
    
    # Total count
    print(f"\n📊 Total FAQs: {len(faqs)}")
    
    # Group by type
    by_type = {}
    for faq in faqs:
        faq_type = faq.get('type', 'Unknown')
        if faq_type not in by_type:
            by_type[faq_type] = []
        by_type[faq_type].append(faq)
    
    print(f"\n📁 Categories ({len(by_type)}):")
    for faq_type, items in sorted(by_type.items()):
        print(f"   • {faq_type}: {len(items)} questions")
    
    # Check for vectors
    has_vectors = any('vector' in faq for faq in faqs)
    print(f"\n🔢 Has vector embeddings: {'Yes' if has_vectors else 'No'}")
    
    # Data structure
    if faqs:
        print(f"\n🔑 Available fields: {list(faqs[0].keys())}")


def show_by_category(faqs, category=None):
    """Show FAQs filtered by category."""
    # Get all categories
    categories = set(faq.get('type', 'Unknown') for faq in faqs)
    
    if category is None:
        print("\n📁 Available Categories:")
        for i, cat in enumerate(sorted(categories), 1):
            count = sum(1 for faq in faqs if faq.get('type') == cat)
            print(f"   {i}. {cat} ({count} FAQs)")
        return
    
    # Filter by category
    filtered = [faq for faq in faqs if faq.get('type', '').lower() == category.lower()]
    
    if not filtered:
        print(f"\n❌ No FAQs found in category: {category}")
        print(f"   Available: {', '.join(sorted(categories))}")
        return
    
    print(f"\n{'='*70}")
    print(f"FAQs in category: {category}")
    print(f"{'='*70}")
    
    for i, faq in enumerate(filtered, 1):
        print(f"\n{i}. Q: {faq.get('question', 'N/A')}")
        print(f"   A: {faq.get('answer', 'N/A')}")


def search_faqs(faqs, keyword):
    """Search FAQs by keyword."""
    keyword_lower = keyword.lower()
    
    # Search in questions and answers
    results = []
    for faq in faqs:
        question = faq.get('question', '').lower()
        answer = faq.get('answer', '').lower()
        
        if keyword_lower in question or keyword_lower in answer:
            results.append(faq)
    
    print(f"\n{'='*70}")
    print(f"Search results for: '{keyword}'")
    print(f"{'='*70}")
    print(f"Found {len(results)} matching FAQ(s)\n")
    
    if not results:
        print("❌ No FAQs found matching your search.")
        return
    
    for i, faq in enumerate(results, 1):
        print(f"{i}. Q: {faq.get('question', 'N/A')}")
        print(f"   A: {faq.get('answer', 'N/A')}")
        print(f"   Type: {faq.get('type', 'N/A')}")
        print()


def export_to_json(faqs, output_file="faqs_export.json"):
    """Export FAQs to JSON format."""
    # Remove vectors if present (they're binary and not JSON serializable)
    faqs_clean = []
    for faq in faqs:
        faq_dict = {k: v for k, v in faq.items() if k != 'vector'}
        faqs_clean.append(faq_dict)
    
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(faqs_clean, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(faqs_clean)} FAQs to: {output_path}")
    print(f"   File size: {output_path.stat().st_size / 1024:.2f} KB")


def show_specific_faq(faqs, index):
    """Show a specific FAQ by index."""
    if index < 1 or index > len(faqs):
        print(f"❌ Invalid index. Please choose between 1 and {len(faqs)}")
        return
    
    faq = faqs[index - 1]
    
    print(f"\n{'='*70}")
    print(f"FAQ #{index}")
    print(f"{'='*70}")
    print(f"\nQuestion: {faq.get('question', 'N/A')}")
    print(f"\nAnswer: {faq.get('answer', 'N/A')}")
    print(f"\nType/Category: {faq.get('type', 'N/A')}")
    
    # Show all fields
    print(f"\nAll fields:")
    for key, value in faq.items():
        if key != 'vector':  # Don't print binary vector data
            print(f"   • {key}: {value}")
        else:
            print(f"   • {key}: <vector data, {len(value) if hasattr(value, '__len__') else 'N/A'} dimensions>")


def main():
    """Main function with interactive menu."""
    print("\n" + "="*70)
    print("FAQ DATA INSPECTOR")
    print("="*70)
    
    faqs = load_faq_data()
    if not faqs:
        return
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            show_all_faqs(faqs)
        elif command == "summary":
            show_summary(faqs)
        elif command == "categories":
            show_by_category(faqs)
        elif command == "category" and len(sys.argv) > 2:
            show_by_category(faqs, sys.argv[2])
        elif command == "search" and len(sys.argv) > 2:
            search_faqs(faqs, sys.argv[2])
        elif command == "export":
            output = sys.argv[2] if len(sys.argv) > 2 else "faqs_export.json"
            export_to_json(faqs, output)
        elif command == "show" and len(sys.argv) > 2:
            try:
                index = int(sys.argv[2])
                show_specific_faq(faqs, index)
            except ValueError:
                print("❌ Error: Please provide a valid number for FAQ index")
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    else:
        # Interactive mode
        show_summary(faqs)
        print_usage()


def print_usage():
    """Print usage instructions."""
    print("\n" + "="*70)
    print("USAGE")
    print("="*70)
    print("""
Interactive Commands:
  python inspect_faq_data.py all              - Show all FAQs
  python inspect_faq_data.py summary          - Show summary statistics
  python inspect_faq_data.py categories       - List all categories
  python inspect_faq_data.py category <name>  - Show FAQs by category
  python inspect_faq_data.py search <keyword> - Search FAQs by keyword
  python inspect_faq_data.py show <number>    - Show specific FAQ by index
  python inspect_faq_data.py export [file]    - Export to JSON

Examples:
  python inspect_faq_data.py all
  python inspect_faq_data.py category "returns and exchanges"
  python inspect_faq_data.py search return
  python inspect_faq_data.py show 5
  python inspect_faq_data.py export faqs.json
""")


if __name__ == "__main__":
    main()
