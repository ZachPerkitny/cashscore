from .client import client


CATEGORIES = client.Categories.get()['categories']
CATEGORIES_DICT = {
    category['category_id']: category for category in CATEGORIES
}
