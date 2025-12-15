#!/usr/bin/env python3
"""
Analyze system prompt improvements based on real data problems
"""

def analyze_system_prompt_improvements():
    """
    Analyze what can be improved in the system prompt based on real problems found
    """
    print("🔍 ANALYZING SYSTEM PROMPT IMPROVEMENTS")
    print("=" * 60)
    
    # Real problems found in data analysis
    real_problems = {
        'grofvuil_issues': {
            'description': 'Items too heavy/large for normal pickup',
            'examples': ['grofvuil', 'kraanwagen', 'te zwaar', 'te groot'],
            'frequency': '5.1% of all problems'
        },
        'not_found_issues': {
            'description': 'Items not found at location',
            'examples': ['niets aangetroffen', 'niet aangetroffen', 'niet gevonden'],
            'frequency': '9.9% of all problems'
        },
        'wrong_placement_issues': {
            'description': 'Items placed incorrectly',
            'examples': ['niet op de juiste plek', 'verkeerde plek', 'niet bereikbaar'],
            'frequency': '1.3% of all problems'
        },
        'technical_issues': {
            'description': 'Technical/logistical problems',
            'examples': ['einde dienst', 'niet gedaan', 'n.a'],
            'frequency': '0.5% of all problems'
        },
        'electrical_appliance_problems': {
            'description': 'High failure rate for electrical appliances',
            'examples': ['gasfornuis 57.8%', 'wasmachine 52.6%', 'oven 50.4%'],
            'frequency': 'Top problematic items'
        }
    }
    
    print("📊 REAL PROBLEMS FOUND IN DATA:")
    print("-" * 40)
    for problem, details in real_problems.items():
        print(f"• {details['description']}: {details['frequency']}")
        print(f"  Examples: {', '.join(details['examples'])}")
        print()
    
    print("🔍 CURRENT SYSTEM PROMPT ANALYSIS:")
    print("=" * 60)
    
    # Current prompt strengths
    print("✅ CURRENT STRENGTHS:")
    print("-" * 30)
    strengths = [
        "Clear gemeente-specific rules",
        "Good categorization system (Huisraad, IJzer/EA/Matrassen, Snoeiafval)",
        "Proper address validation",
        "Privacy compliance",
        "Clear size/weight limits",
        "Good refusal handling for non-allowed items"
    ]
    
    for strength in strengths:
        print(f"• {strength}")
    
    print("\n❌ MISSING ELEMENTS BASED ON REAL PROBLEMS:")
    print("-" * 50)
    
    # Missing elements based on real problems
    missing_elements = {
        'grofvuil_guidance': {
            'issue': '5.1% of problems are "too heavy/large"',
            'current': 'Basic size limits mentioned (1.80m x 0.90m x 30kg)',
            'missing': 'No guidance on what to do when items exceed limits',
            'improvement': 'Add guidance for oversized items (kraanwagen, grofvuil routes)'
        },
        'placement_guidance': {
            'issue': 'Many items "not found" or "wrong placement"',
            'current': 'Basic placement rules (outside, accessible)',
            'missing': 'Specific guidance on exact placement',
            'improvement': 'Detailed placement instructions with examples'
        },
        'electrical_appliance_guidance': {
            'issue': 'High failure rate for electrical appliances (50%+)',
            'current': 'Basic rules for electrical items',
            'missing': 'Specific guidance for heavy appliances',
            'improvement': 'Special handling instructions for wasmachines, koelkasten, ovens'
        },
        'timing_guidance': {
            'issue': 'Many items not found due to timing',
            'current': 'Basic timing rules (05:00-07:30)',
            'missing': 'Guidance on when items might be taken by others',
            'improvement': 'Warnings about early pickup by others'
        },
        'problem_prevention': {
            'issue': 'No proactive problem prevention',
            'current': 'Reactive rule explanation',
            'missing': 'Proactive guidance to prevent common problems',
            'improvement': 'Add "common mistakes to avoid" section'
        }
    }
    
    for element, details in missing_elements.items():
        print(f"🔍 {element.upper().replace('_', ' ')}:")
        print(f"   Issue: {details['issue']}")
        print(f"   Current: {details['current']}")
        print(f"   Missing: {details['missing']}")
        print(f"   Improvement: {details['improvement']}")
        print()
    
    print("💡 SPECIFIC IMPROVEMENTS NEEDED:")
    print("=" * 50)
    
    improvements = {
        'add_problem_prevention_section': {
            'title': 'Add "Common Problems to Avoid" Section',
            'content': [
                'Items too heavy for normal pickup → use grofvuil route',
                'Items not placed outside → ensure items are outside and visible',
                'Items placed incorrectly → follow exact placement rules',
                'Electrical appliances → special handling required',
                'Timing issues → put items out at correct time'
            ]
        },
        'enhance_electrical_appliance_guidance': {
            'title': 'Enhanced Electrical Appliance Guidance',
            'content': [
                'Wasmachines: Must be outside, visible, not blocked',
                'Koelkasten: Must be empty, outside, accessible',
                'Ovens: Must be outside, visible, not blocked',
                'Heavy appliances: May require special pickup'
            ]
        },
        'add_placement_troubleshooting': {
            'title': 'Add Placement Troubleshooting',
            'content': [
                'If items not found: check exact placement',
                'If items not accessible: ensure clear path',
                'If items too heavy: contact for special pickup',
                'If items stolen: report and reschedule'
            ]
        },
        'add_timing_warnings': {
            'title': 'Add Timing Warnings',
            'content': [
                'Items may be taken by others if put out too early',
                'Items must be outside between 05:00-07:30',
                'If items missing: may have been taken by others',
                'Reschedule if items stolen before pickup'
            ]
        },
        'add_problem_resolution_flow': {
            'title': 'Add Problem Resolution Flow',
            'content': [
                'If pickup failed: identify reason',
                'If items too heavy: schedule special pickup',
                'If items not found: check placement and reschedule',
                'If items stolen: report and reschedule'
            ]
        }
    }
    
    for improvement, details in improvements.items():
        print(f"📝 {details['title']}:")
        for item in details['content']:
            print(f"   • {item}")
        print()
    
    print("🎯 PRIORITY IMPROVEMENTS:")
    print("=" * 30)
    
    priorities = [
        "1. Add 'Common Problems to Avoid' section",
        "2. Enhanced electrical appliance guidance",
        "3. Add placement troubleshooting",
        "4. Add timing warnings",
        "5. Add problem resolution flow"
    ]
    
    for priority in priorities:
        print(f"• {priority}")
    
    print("\n📋 SPECIFIC PROMPT ADDITIONS NEEDED:")
    print("=" * 40)
    
    prompt_additions = {
        'common_problems_section': """
Common Problems to Avoid:
- Items too heavy/large → use grofvuil route or contact for special pickup
- Items not outside → ensure items are outside and visible from street
- Items placed incorrectly → follow exact placement rules (on street, accessible)
- Electrical appliances → special handling required, must be outside and visible
- Timing issues → put items out between 05:00-07:30 on pickup day
- Items stolen → may be taken by others if put out too early
""",
        'electrical_appliance_guidance': """
Special Handling for Electrical Appliances:
- Wasmachines: Must be outside, visible, not blocked, accessible
- Koelkasten: Must be empty, outside, visible, not blocked
- Ovens: Must be outside, visible, not blocked, accessible
- Heavy appliances: May require special pickup (kraanwagen)
- All electrical items: Must be outside and visible from street
""",
        'placement_troubleshooting': """
Placement Troubleshooting:
- If items not found: check exact placement (on street, visible)
- If items not accessible: ensure clear path for pickup vehicle
- If items too heavy: contact for special pickup (kraanwagen)
- If items stolen: report and reschedule pickup
- If items blocked: ensure clear access for pickup vehicle
""",
        'timing_warnings': """
Timing Warnings:
- Items may be taken by others if put out too early
- Items must be outside between 05:00-07:30 on pickup day
- If items missing: may have been taken by others before pickup
- Reschedule if items stolen before pickup time
- Don't put items out too early to prevent theft
"""
    }
    
    for section, content in prompt_additions.items():
        print(f"📝 {section.upper().replace('_', ' ')}:")
        print(content)
        print()

if __name__ == "__main__":
    analyze_system_prompt_improvements()
