import os
import streamlit as st

def load_css(css_files):
    """Load CSS file(s) and inject them into Streamlit.
    
    Args:
        css_files: A string or list of strings with CSS file paths
    """
    if isinstance(css_files, str):
        css_files = [css_files]
        
    for css_file in css_files:
        with open(css_file, 'r') as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def load_html_template(template_path):
    """Load an HTML template file.
    
    Args:
        template_path: Path to the HTML template file
        
    Returns:
        The HTML template as a string
    """
    with open(template_path, 'r') as f:
        return f.read()

def render_template(template, **kwargs):
    """Render an HTML template with the provided values.
    
    Args:
        template: The HTML template string
        **kwargs: The values to replace in the template
        
    Returns:
        The rendered HTML string
    """
    return template.format(**kwargs)

def get_base_path():
    """Get the base path to the frontend directory.
    
    Returns:
        The absolute path to the frontend directory
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_css_path(filename):
    """Get the full path to a CSS file.
    
    Args:
        filename: The CSS filename
        
    Returns:
        The full path to the CSS file
    """
    return os.path.join(get_base_path(), 'static', 'css', filename)

def get_html_path(filename):
    """Get the full path to an HTML template file.
    
    Args:
        filename: The HTML filename
        
    Returns:
        The full path to the HTML file
    """
    return os.path.join(get_base_path(), 'static', 'html', filename)