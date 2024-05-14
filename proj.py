import random
import time
import requests
from PIL import Image

class Trenstagram: # creds to https://github.com/Trenblack/Trenstagram for the simple and easy-to-use template for insta's API.
    def __init__(self):
        self.BASE_URL = 'https://www.instagram.com/'
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0"
        self.session = requests.Session()
        self.session.headers = {'user-agent': self.USER_AGENT}
        self.session.headers.update({'Referer': self.BASE_URL})
        self.logged_in = False

    def login(self, USERNAME, PASSWD, EMAIL):
        self.email = EMAIL
        self.username = USERNAME
        try:
            req = self.session.get(self.BASE_URL)
            self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
            str_time = str(int(time.time()))
            PASSWORD = '#PWD_INSTAGRAM_BROWSER:0:' + str_time + ':' + PASSWD
            login_data = {'username': USERNAME, 'enc_password': PASSWORD}
            LOGIN_URL = self.BASE_URL + 'accounts/login/ajax/'
            login = self.session.post(LOGIN_URL , data=login_data, allow_redirects=True)
            self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
            if(login.json()['authenticated']):
                self.logged_in = True
                print("Logged in")
                return True
            else:
                raise Exception()
        except:
            print("Error Logging in.")
        return False


    def verify(self):
        if self.logged_in:
            return True
        print("Log in first.")
        return False

    def change_profile_image_from_file(self, file_path):
        if self.verify():
            try:
                with open(file_path, 'rb') as file:
                    image_data = file.read()
                self.session.headers.update({'Content-Length': str(len(image_data))})
                r = self.session.post(self.BASE_URL + "accounts/web_change_profile_picture/", files={'profile_pic': image_data})
                response_json = r.json()
                print("Response Content:", response_json)
                if 'changed_profile' in response_json:
                    if response_json['changed_profile']:
                        print("Profile picture changed!")
                        return True
                raise Exception("Profile picture not changed")
            except Exception as e:
                print('Error Changing Profile Image:', e)
        return False

    def resize_image(self, image_path, max_size=(500, 500)):
        try:
            # Open the image
            image = Image.open(image_path)

            # Resize the image to fit within the maximum size
            image.thumbnail(max_size, Image.LANCZOS)
            return image
        except Exception as e:
            print('Error resizing image:', e)
            return None

    def rotate_and_change_profile_image(self, degrees, image_path):
        if self.verify():
            try:
                # Resize the image to prevent exceeding the size limit
                resized_image = self.resize_image(image_path)
                if resized_image:
                    # Rotate the resized image
                    rotated_image = resized_image.rotate(degrees, expand=True)

                    # Save the rotated image to a temporary file
                    rotated_image_path = 'rotated_profile_image.jpg'
                    rotated_image.save(rotated_image_path)

                    # Upload the rotated image as the new profile picture
                    if self.change_profile_image_from_file(rotated_image_path):
                        print("Profile image rotated and changed successfully!")
                        return True
                    else:
                        print("Failed to rotate and change profile image.")
                else:
                    print("Failed to resize image.")
            except Exception as e:
                print('Error rotating and changing profile image:', e)
        return False

    def refresh_session(self):
        try:
            req = self.session.get(self.BASE_URL)
            req.raise_for_status()  # Raise an exception for HTTP errors
            csrftoken = req.cookies.get('csrftoken')
            if csrftoken:
                self.session.headers.update({'X-CSRFToken': csrftoken})
                print("Session refreshed")
                return True
            else:
                print("Error: CSRF token not found in response headers")
                return False
        except requests.RequestException as e:
            print("Error refreshing session:", e)
            print("Attempting to log in again...")
            return self.login(self.username, self.password, self.email)

trenstagram = Trenstagram()

max_rotations_per_hour = 60
delay_between_rotations = 3600 / max_rotations_per_hour  # 3600 seconds in an hour

def get_random_delay():
    jitter = random.uniform(0.5, 1.5)  # Add random jitter between 0.5 and 1.5 times the delay
    return delay_between_rotations * jitter

current_degrees = 0

if trenstagram.login('username', 'password', 'email'):
    max_rotations = 150  # Example: Limiting to 10 rotations
    rotations = 0
    while rotations < max_rotations:
        print(rotations)
        try:
            # Rotate the profile image by 25 degrees
            current_degrees += 100
            if current_degrees >= 360:
                current_degrees -= 360

            random_delay = get_random_delay()

            if trenstagram.rotate_and_change_profile_image(current_degrees, 'path :)'):
                print('Rotation successful woooo')
            else:
                print('Rotation failed :( ')
            rotations += 1
            print("waiting for", random_delay, "seconds before next rotation")

            time.sleep(random_delay)  # Wait for [random] seconds before next rotation
        except Exception as e:
            print("An error occurred:", e)
            break  # Exit the loop on error
else:
    print("Login failed")
