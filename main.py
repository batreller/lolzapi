import __init__

client = __init__.Client(
    "_ga=GA1.1.327237918.1666707226; _ym_uid=1666707227246044402; _ym_d=1666707227; G_ENABLED_IDPS=google; xf_tfa_trust=9V79E6WTxVrffe-K6hHbi0831lTW4EA8; xf_user=157562%2C3076d96bc3df65607f2be685e0e9a698d0c5a15c; xf_logged_in=1; xf_market_search_bar=%7B%2210%22%3A1659454784%7D; xf_language_id=2; xf_last_read_article_date=1668097500; xf_is_not_mobile=1; xf_feed_custom_order=post_date; xf_session=b471c14debfaf99e65f9ddeccd8026db; _ym_isad=1; xf_viewedContestsHidden=1; _ga_J7RS527GFK=GS1.1.1671037156.73.1.1671040014.0.0.0; ")
# client = lolzapi.Client()

data = {
    "message_html": "[visitor]asd[/visitor]",
    "_xfRelativeResolver": "https://zelenka.guru/threads/5062288/",
    "last_date": "1678371119",
    "last_known_date": "1678370916",
    "_xfToken": client.xf_token,
    "_xfRequestUri": "/threads/5062288/",
    "_xfNoRedirect": "1",
    "_xfToken": client.xf_token,
    "_xfResponseType": "json",
}
response = client.send_request("POST", "https://zelenka.guru/posts/37465621/comment", data=data)
print(response.text)

# while True:
#     threads = client.get_threads("contests")
#
#     for thread in threads["threads"]:
#         result = client.participate(thread["thread_id"])
#         print(result.text)
#
#     time.sleep(5)

# thread = client.get_thread(5058039)
# print(thread.text)
