from bs4 import BeautifulSoup


class TitleParser:
    @staticmethod
    def parse(html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        title = None
        if soup.title:
            title = soup.title.get_text(strip=True)
        # Optionally, look for a primary headline element.
        h1 = soup.find('h1')
        if h1 and (not title or len(h1.get_text(strip=True)) > len(title)):
            title = h1.get_text(strip=True)

        return title
