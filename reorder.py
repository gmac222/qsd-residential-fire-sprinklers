import re

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The sections we care about, in the order they currently appear or loosely.
# But it's better to just extract each section block.
# Assuming each section is an HTML comment followed by <section ...> to </section>

def extract_section(section_id, content):
    # This finds the start of the section
    start_pattern = f'<!-- ═══════════════ [^═]+ ═══════════════ -->\s*<section [^>]*id="{section_id}"'
    match = re.search(start_pattern, content)
    if not match:
        start_pattern = f'<section [^>]*id="{section_id}"'
        match = re.search(start_pattern, content)
        if not match:
            return None, content

    start_idx = match.start()
    
    # We need to find the matching closing tag </section>
    # Since sections don't nest <section> tags in our code, we can just find the next </section>
    end_idx = content.find('</section>', start_idx)
    if end_idx == -1:
        return None, content
        
    end_idx += len('</section>')
    
    # also include the newline after it
    if end_idx < len(content) and content[end_idx] == '\n':
        end_idx += 1
        
    # Check if there is a script or something immediately following that belongs to it? No, usually just section tags.
    section_content = content[start_idx:end_idx]
    
    # Remove from content
    new_content = content[:start_idx] + content[end_idx:]
    
    return section_content, new_content

sections_to_extract = ['hero', 'specs', 'media-accreditations', 'testimonials', 'process', 'features', 'audiences', 'cta']
extracted = {}

for sec in sections_to_extract:
    sec_content, content = extract_section(sec, content)
    if sec_content:
        extracted[sec] = sec_content
    else:
        print(f"Could not find section {sec}")

# Now we need to insert them back in the new order.
new_order = [
    'hero',
    'media-accreditations',
    'features',
    'audiences',
    'specs',
    'process',
    'testimonials',
    'cta'
]

# Find the injection point. Usually after the <nav> element
nav_end = content.find('</nav>')
if nav_end != -1:
    inject_idx = nav_end + len('</nav>\n\n')
else:
    print("Could not find nav element")
    exit(1)

ordered_content = "\n\n".join([extracted[sec] for sec in new_order if sec in extracted])

final_content = content[:inject_idx] + ordered_content + "\n\n" + content[inject_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Successfully reordered index.html")
