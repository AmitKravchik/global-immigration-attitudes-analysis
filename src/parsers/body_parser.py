from bs4 import BeautifulSoup


class BodyParser:
    @staticmethod
    def parse(html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        # Start with common article tags
        for tag in soup.find_all(['article', 'main']):
            if tag.get_text(strip=True):
                return tag.get_text(separator="\n", strip=True)
        
        # If no common article tag, look for div tags with common class names
        common_classes = ['article-body', 'post-content', 'entry-content', 'story-body', 'blog-post']
        for class_name in common_classes:
            content = soup.find('div', class_=class_name)
            if content:
                return content.get_text(separator="\n", strip=True)
        
        # Fallback to finding the largest content block by text length
        largest_block = None
        max_length = 0
        for element in soup.find_all(['p', 'div', 'section']):
            text = element.get_text(separator="\n", strip=True)
            if len(text) > max_length:
                max_length = len(text)
                largest_block = text

        return largest_block

