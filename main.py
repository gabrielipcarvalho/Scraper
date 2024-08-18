import requests
from bs4 import BeautifulSoup
import pprint


def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def selector(res):
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select('.titleline a')
    filtered_links = [a for a in links if not a.find('span')]
    subtext = soup.select('.subtext')
    return filtered_links, subtext


def sort_stories_by_votes(dictionary):
    return sorted(dictionary, key=lambda x: x['votes'], reverse=True)


def create_custom_hn(links, subtext, vote_threshold=99):
    hn = []
    for idx, item in enumerate(links):
        title = item.getText()
        href = item.get('href', None)
        vote = subtext[idx].select('.score')
        if vote:
            points = int(vote[0].getText().replace(' points', ''))
            if points > vote_threshold:
                hn.append({'title': title, 'link': href, 'votes': points})
    return sort_stories_by_votes(hn)


def fetch_and_combine_hn_stories(pg1, pg2):
    pg1_links, pg1_subtext = selector(pg1)
    pg2_links, pg2_subtext = selector(pg2)
    links = pg1_links + pg2_links
    subtext = pg1_subtext + pg2_subtext
    return create_custom_hn(links, subtext)


if __name__ == "__main__":
    page1_response = fetch_page("https://news.ycombinator.com/")
    page2_response = fetch_page("https://news.ycombinator.com/news?p=2")

    if page1_response and page2_response:
        hn_two_pages = fetch_and_combine_hn_stories(page1_response, page2_response)
        pprint.pprint(hn_two_pages)
