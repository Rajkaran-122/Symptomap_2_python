
import os

def fix_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Check for UTF-16 LE BOM
        if content.startswith(b'\xff\xfe'):
            decoded = content.decode('utf-16-le')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(decoded)
            print(f"Fixed UTF-16 LE encoding for {filepath}")
            return

        # Check for null bytes (often result of copy/paste or bad encoding)
        if b'\x00' in content:
            decoded = content.replace(b'\x00', b'')
            # Try to decode as utf-8
            try:
                text = decoded.decode('utf-8')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Removed null bytes from {filepath}")
            except:
                print(f"Could not decode {filepath} as utf-8 after removing nulls")
            return
            
        print(f"No fixes needed for {filepath}")
            
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

if __name__ == "__main__":
    fix_file("app/api/v1/chatbot.py")
