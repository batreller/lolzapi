import re

import bs4
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Response:
    @staticmethod
    def get_threads_response(data: requests.models.Response) -> dict:
        data = data.json()
        res = {
            "title": data["title"],
            "canPostThread": data["canPostThread"],
            "createThreadLink": data["createThreadLink"],
            "nextPageHref": data.get("nextPageHref"),
            "node_id": data["node_id"],
            "threads": [],
            "full_info": data,
            "fill_threads_info": []
        }
        soup = BeautifulSoup(data["templateHtml"], "html.parser")
        all_threads = soup.find("div", {"class": "latestThreads _insertLoadedContent"})
        if not all_threads:
            return res
        all_threads = all_threads.contents

        for thread in all_threads:
            # thread_text = str(thread)
            if len(str(thread)) < 100 or "thread-" not in str(thread):
                continue
            a = thread.find('div', class_=re.compile('discussionListItem'))
            print(str(thread))
            thread_data = {
                # "thread_id": thread.split("thread-")[1].split("\"")[0],
                "thread_id": thread.get("id").split("-")[-1],
                "thread_name": thread.find("span", class_=re.compile('spanTitle')).text,
                "creator_name": thread.get("data-author"),
                "creator_id": re.findall(r'members/(.*?)/', str(thread), re.DOTALL)[0]
            }
            res["threads"].append(thread_data)
            res["fill_threads_info"].append(thread)

        return res

    @staticmethod
    def get_user_response(response: requests.models.Response) -> dict:
        # todo finish here
        res = {
            "user_exists": True,
            "user": {
                "name": None,
                "id": None,
                "url": response.url,
                "info": {
                    "registration_date": None,
                    "discord": None,
                    "jabber": None,
                    "qiwi": None,
                    "steam": None,
                    "telegram": None,
                    "vk": None
                },
                "blocked": False,
            },
            "stats": {
                "messages": None,
                "sympathies": None,
                "trophies": None,
                "contests": None,
                "subscribe": None,
                "subscribers": None
            },
            "profile_posts": [],
            "full_response": response
        }
        if response.status_code == 404:
            res["user_exists"] = False
            return res

        elif response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            a = soup.find("div", class_="userContentLinks")

            res["user"]["name"] = soup.find("meta", property="profile:username").get("content")
            res["user"]["id"] = re.findall(r'user/(.*?)/',
                                           soup.find("div", class_="userContentLinks").find_all("a", class_="button")[
                                               -1].get("href"), re.DOTALL)[0]
            return res

        else:
            raise SystemError(f"zelenka.guru returned unknown response, status code {response.status_code}")

    @staticmethod
    def get_thread_response(response: requests.models.Response) -> dict:
        print(response.text)
        res = {
            "title": None,
            "thread_id": None,
            "views": None,
            "creation_date": None,
            "posts": [],
            "thread_creator": {
                "id": None,
                "name": None,
                "likes": None,
                "avatar": None
            },
            "categories": []
        }

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # name, id, views, creation date
        title = soup.find("div", class_="titleBar")
        res["title"] = title.find("h1")["title"]
        res["views"] = title.find("span", class_="info-separator")

        string_time = title.find(class_="DateTime")  # 1 окт 2016 в 12:46
        print(string_time)
        unix_creation_time = datetime.strptime(string_time, "%d %b %Y в %H:%M")
        res["creation_date"] = unix_creation_time

        # categories
        categories = soup.find("span", "crumbs").find_all("a", class_="crumb")
        for category in categories:
            res["categories"].append({
                "name": category.text.strip(),
                "url": category["href"]
            })

        return res

    @staticmethod
    def get_shared_ips(response: requests.models.Response) -> requests.models.Response:
        return response

    @staticmethod
    def likes_inline(response: requests.models.Response) -> requests.models.Response:
        return response

    @staticmethod
    def like(response: requests.models.Response) -> requests.models.Response:
        return response

    @staticmethod
    def participate(response: requests.models.Response) -> requests.models.Response:
        return response

    @staticmethod
    def follow(response: requests.models.Response) -> requests.models.Response:
        return response

    @staticmethod
    def unfollow(response: requests.models.Response) -> requests.models.Response:
        return response

    @staticmethod
    def participate(response: requests.models.Response) -> requests.models.Response:
        return response
