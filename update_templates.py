import os
import re

def update_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern to match the nav_links block and remove it
    pattern = r'{% block nav_links %}.*?{% endblock %}[\r\n]+'
    updated_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    if content != updated_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

def main():
    templates_dir = 'templates'
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(templates_dir, filename)
            update_template(file_path)

if __name__ == "__main__":
    main() 