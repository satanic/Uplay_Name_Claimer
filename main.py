import requests, queue, base64, random, string, threading, ctypes
from colorama import Fore, Style, init; init(convert=True)

class Claimer():
    usernames = queue.Queue()
    headers = {'Ubi-AppId': "2c2d31af-4ee4-4049-85dc-00dc74aef88f","Ubi-RequestedPlatformType": "uplay","user-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}
    checked_count = 0; error_count = 0
    session=requests.Session()

    def create_account(self, user):
        email = f"{user}-" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        password = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_letters) for _ in range(15))
        proxies = {"https":f'http://{random.choice(open("proxies.txt", "r").readlines())}',"http":f'http://{random.choice(open("proxies.txt", "r").readlines())}'}
        body = {
            'age': None,
            "dateOfBirth": "1989-01-18T00:00:00.00000Z",
            'confirmedEmail': email,
            'email': email,
            'country': 'GB',
            'firstName': None,
            'lastName': None,
            'nameOnPlatform': user,
            'password': password,
            'preferredLanguage': 'en',
            'legalOptinsKey': 'eyJ2dG91IjoiNC4wIiwidnBwIjoiNC4wIiwidnRvcyI6IjIuMSIsImx0b3UiOiJlbi1HQiIsImxwcCI6ImVuLUdCIiwibHRvcyI6ImVuLUdCIn0'
        }
        r = self.session.post("https://public-ubiservices.ubi.com/v3/users", proxies=proxies, headers=self.headers, json=body)
        if r.status_code == 200:
            with open('data/claimed.txt', "a") as f:
                f.write(f'{user} | {email}:{password}\n')


    def login(self):
        self.headers["Authorization"] = "Basic " + base64.b64encode(bytes(open("data/login.txt", "r").readline(), "utf-8")).decode("utf-8")
        r = self.session.post("https://public-ubiservices.ubi.com/v3/profiles/sessions", json={"Content-Type":"application/json"}, headers=self.headers)
        if r.status_code == 200:
            if r.json()["ticket"]:
                token = "Ubi_v1 t=" + r.json()["ticket"]
                self.headers['Authorization'] = token
                return True
            return False
        return False


    def main(self):
        while not self.usernames.empty():
            name = self.usernames.get(); self.usernames.put(name)
            ctypes.windll.kernel32.SetConsoleTitleW(f"Checked: {self.checked_count+1} | Errors: {self.error_count}")
            proxies = {"https":f'http://{random.choice(open("proxies.txt", "r").readlines())}',"http":f'http://{random.choice(open("proxies.txt", "r").readlines())}'}
            
            r = self.session.get(f'https://public-ubiservices.ubi.com/v2/profiles?nameOnPlatform={name}&platformType=uplay',headers=self.headers, proxies=proxies)
            if r.status_code == 200:
                if len(r.json()['profiles']) == 0:
                    print(Fore.GREEN + Style.BRIGHT + f'[+] {name}\n')
                    self.create_account(name)
                else:
                    print(Fore.RED + Style.BRIGHT + f'[-] {name}\n')
            else:
                self.error_count+=1
                print(Fore.BLACK + Style.BRIGHT + f'[!] {name}\n')
                

    def threads(self):
        if self.login():
            [self.usernames.put(line.strip()) for line in open('data/names.txt')]
            for _ in range(250):
                threading.Thread(target=self.main, args=()).start()



if __name__ == "__main__":
    Claimer().threads()
