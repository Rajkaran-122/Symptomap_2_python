import urllib.request
import urllib.error

def check_admin():
    url = 'http://localhost:8000/api/v1/admin/pending'
    try:
        response = urllib.request.urlopen(url)
        print(f"Success: {response.getcode()}")
        print(response.read().decode('utf-8')[:100])
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_admin()
