import json
import logging
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from lib.config.strings import log_messages as msg
from lib.models.page import Page
from lib.tasks.scrape_comments_from_post import ScrapeCommentsFromPost
from lib.tasks.scrape_page_data import ScrapePageData
from lib.tasks.scrape_posts_from_page import ScrapePostsFromPage
from lib.tasks.scrape_dates_from_posts import ScrapeDatesFromPosts
from lib.utils.driver import chromedriver, facebook_login


def pages_from_json(pagepath: str):
    """Makes a list of Page objects from JSON file"""
    pagepath = Path(pagepath)
    with open(pagepath / 'pages.json', 'rb') as jfile:
        page_objects = json.load(jfile)
    return [Page(po['fullname'], po['username']) for po in page_objects]

def parse_threshold_config(thresh_conf: str):
    """Parse threshold configuration by format"""
    if thresh_conf.isnumeric():
        return int(thresh_conf)
    threshold = date.fromisoformat(thresh_conf)
    return (date.today() - threshold).days

def main():
    """Main function, run the crawler's operations"""

    # initialize paths
    crawl_time = time.perf_counter()
    with open('configuration.json', 'rb') as jfile:
        config = json.load(jfile)  # load configurations
    datapath = Path(config['data_path'])
    timestring = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    datapath = datapath / timestring
    os.mkdir(datapath)

    # initialize logger
    logging_fmt = "[%(levelname)s][%(asctime)s] %(message)s"
    logging.basicConfig(
        filename=datapath / 'logfile.log',
        format=logging_fmt,
        level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info('Started Facebook Crawler')

    # loading pages from pages.json
    pages = pages_from_json(config['page_path'])
    logging.info(msg['PAGE_LOAD_JSON'], len(pages))

    try:
        logging.info('initiating login to Facebook...')
        email, password = config["facebook_auth"].values()
        driver = chromedriver()
        facebook_login(driver, email, password)

        for page in pages:
            # scrape content for each page
            pagepath = datapath / page.fullname.lower().replace(' ', '_')
            os.mkdir(pagepath)

            logging.info(msg['PAGE_START'], page.fullname)
            task = ScrapePageData(driver, page.username)
            task.run()  # run page data scraping task
            logging.info(msg['PAGE_END'], page.fullname, timedelta(seconds=task.time))
            page.set_likes_followers(task.likes_followers)
            with open(pagepath / 'page_data.json', 'w', encoding='utf-8') as jfile:
                json.dump(page.__dict__, jfile, ensure_ascii=False, indent=4)
            del task

            driver.quit()  # driver reset
            driver = chromedriver(incognito=True)

            logging.info(msg['POST_START'], page.fullname)
            threshold = parse_threshold_config(config['threshold_date'])
            task = ScrapeDatesFromPosts(driver, page)
            task.run(threshold)
            date_dict = task.date_dict
            task_time = task.time
            del task

            driver.quit()  # driver reset
            driver = chromedriver()

            task = ScrapePostsFromPage(driver, page, date_dict)
            task.run(threshold)  # run post scraping task
            posts = task.scraped_posts
            task_time += task.time
            del task

            # if len(posts) > 0:
            #     for post in posts:
            #         post.datetime = task.date_dict[post.post_id]
            logging.info(msg['POST_END'], len(posts), page.fullname, timedelta(seconds=task_time))

            driver.quit()  # driver reset
            driver = chromedriver()

            if len(posts) == 0:
                logging.info('no available posts for %s', page.fullname)
            else:
                logging.info(msg['TOTAL_POSTS'], len(posts), page.fullname)
                comments = []
                total_time = 0
                for post in posts:
                    logging.info(msg['COMM_START'], post.type, post.post_id)
                    task = ScrapeCommentsFromPost(driver, post)
                    task.run()  # run comment scraping task
                    total_time += task.time
                    logging.info(msg['COMM_END'],
                                len(task.scraped_comments), timedelta(seconds=task.time))
                    comments += task.scraped_comments
                    del task

                    driver.quit()  # driver reset
                    driver = chromedriver()

                logging.info(msg['TOTAL_COMMS'], page.fullname,
                            len(comments), timedelta(seconds=total_time))
                posts = [post.__dict__ for post in posts]
                comments = [comment.__dict__ for comment in comments]
                with open(pagepath / 'posts.json', 'w', encoding='utf-8') as jfile:
                    json.dump(posts, jfile, ensure_ascii=False, indent=4)
                with open(pagepath / 'comments.json', 'w', encoding='utf-8') as jfile:
                    json.dump(comments, jfile, ensure_ascii=False, indent=4)

            logging.info('done scraping %s', page.fullname)

    finally:
        crawl_time = time.perf_counter() - crawl_time
        logging.info(msg['CRAWLER_DONE'], timedelta(seconds=crawl_time))
        driver.quit()


if __name__ == "__main__":
    main()
