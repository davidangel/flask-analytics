from .csv_loader import load_dataset
from ..helpers.dataset_helper import merge_datasets_vertically, get_entries_after
from ..helpers.datetime_helper import subtract_from_today_days
from ..config import Config


def get_summary(site_name):
    summary = {
        'week': {
            'reviews': 99,
            'promoters': 99,
            'passives': 99,
            'detractors': 99
        },
        'month': {
            'reviews': 99,
            'promoters': 99,
            'passives': 99,
            'detractors': 99
        },
    }
    columns = ['EndDate', 'WebsiteRating', 'ProductRating']
    voc_dataset = load_dataset(site_name, Config.VOC_SURVEY, columns)
    cc_dataset = load_dataset(site_name, Config.COMMENT_CARD_SURVEY, columns)
    merged_dataset = merge_datasets_vertically(voc_dataset, cc_dataset)

    merged_dataset = get_entries_after(merged_dataset, subtract_from_today_days(30), 'EndDate')
    summary['month']['reviews'] = len(merged_dataset)

    merged_dataset = get_entries_after(merged_dataset, subtract_from_today_days(7), 'EndDate')
    summary['week']['reviews'] = len(merged_dataset)

    # merged_dataset.to_csv('data/'+site_name+'out.csv')
    return summary


def addition(a, b):
    return a + b