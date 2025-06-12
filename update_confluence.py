import os
from dotenv import load_dotenv
from atlassian import Confluence
import markdown2
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# These are environment variables related to confluence. Make sure to set them as formatted in .env.sample.
CONFLUENCE_URL = os.environ['CONFLUENCE_URL']
CONFLUENCE_USER = os.environ['CONFLUENCE_USER']
CONFLUENCE_API_TOKEN = os.environ['CONFLUENCE_API_TOKEN']
CONFLUENCE_SPACE = os.environ['CONFLUENCE_SPACE']
CONFLUENCE_PARENT_PAGE = os.environ['CONFLUENCE_PARENT_PAGE']

# Create unique confluence instance
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=CONFLUENCE_USER,
    password=CONFLUENCE_API_TOKEN,
)

# This function finds all markdown files in the root directory and skips any example files or ignored folders.
def find_all_markdown_files(root):
    # Ignored folders/files. Add or subtract extensions as needed.
    skips = {'.git', '.github', 'venv', '.venv', '__pycache__'}
    results = []
    for path in root.rglob('*.md'):
        # This line separates the path into parts and checks if any part contains a string that matches a skips string.
        if any(part in skips for part in path.parts):
            continue
        if path.name.lower().endswith('.example.md'):
            continue
        results.append(path)
    results.sort()
    return results

# Transforms something like docs/README.md into the Confluence title docs/README.
# This can be edited to enforce page title naming conventions if needed.
def path_to_title(root, md_path):
    relative_path = md_path.relative_to(root)
    stem = relative_path.with_suffix('')
    return str(stem).replace(os.sep, '/')


# This function turns markdown text into HTML and wraps the result in a <ac:structured-macro>.
def markdown_to_storage(markdown_text):
    return markdown2.markdown(markdown_text, extras=["fenced-code-blocks"])

# This function publishes a new page or an existing page given the title and markdown text.
def publish_page(title, markdown_body, page_id=None):
    html_code = markdown_to_storage(markdown_body)
    if page_id:
        confluence.update_page(page_id, title, html_code)
        print(f"Updated existing page: {title} ({page_id})")
    else:
        result = confluence.create_page(CONFLUENCE_SPACE, title, html_code, parent_id=CONFLUENCE_PARENT_PAGE)
        print(f"Created page: {title} ({result['id']})")


if __name__ == "__main__":
    repository_root = Path.cwd()
    markdown_files = find_all_markdown_files(repository_root)
    if not markdown_files:
        print("No markdown files found; exiting ...")
        exit(0)

    for markdown_path in markdown_files:
        body = markdown_path.read_text(encoding='utf-8')
        title = path_to_title(repository_root, markdown_path)
        html = markdown_to_storage(body)

        existing = confluence.get_page_by_title(CONFLUENCE_SPACE, title)
        pid = existing['id'] if existing else None

        publish_page(title, html, pid)




