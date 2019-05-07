import requests
import re

class ProxyRequests:
    def __init__(self):
        self.sockets = []
        self.request, self.proxy = '', ''
        self.proxy_used, self.raw_content = '', ''
        self.status_code, self.try_count = 0, 15
        self.__acquire_sockets()

    # get a list of sockets from sslproxies.org
    def __acquire_sockets(self):
        r = requests.get("https://www.sslproxies.org/")
        matches = re.findall(r"<td>\d+.\d+.\d+.\d+</td><td>\d+</td>", r.text)
        revised_list = [m1.replace("<td>", "") for m1 in matches]
        for socket_str in revised_list:
            self.sockets.append(socket_str[:-5].replace("</td>", ":"))

    def __try_count_succeeded(self):
        message = "Unable to make proxied request. "
        message += "Please check the validity of your URL."
        print(message)

    def __set_request_data(self, req, socket):
        self.request = req.text
        self.status_code = req.status_code
        self.raw_content = req.content
        self.proxy_used = socket

    # recursively try proxy sockets until successful GET
    def get(self, url):
        if len(self.sockets) > 0 and self.try_count > 0:
            current_socket = self.sockets.pop(0)
            proxies = {
                "http": "http://" + current_socket,
                "https": "https://" + current_socket
            }
            try:
                request = requests.get(
                    url,
                    timeout=3.0,
                    proxies=proxies
                )
                self.__set_request_data(request, current_socket)
            except Exception:
                self.try_count -= 1
                self.get()
        else:
            self.__try_count_succeeded()

    def get_status_code(self):
        return self.status_code

    def get_proxy_used(self):
        return str(self.proxy_used)

    def get_raw(self):
        return self.raw_content

    def __str__(self):
        return str(self.request)