import os
import requests
from urllib.parse import urljoin

# Function to download a file from a URL
def download_file(url, directory):
    response = requests.get(url)
    filename = os.path.join(directory, os.path.basename(url))
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f'Downloaded: {filename}')

# Main function
def main():
    # Prompt user for installation directory
    install_dir = input('Enter the installation directory: ')
    os.makedirs(install_dir, exist_ok=True)  

    # Repository file URL
    repo_url = 'https://raw.githubusercontent.com/petrospetrosapostolou-bot/PYTHONSCPIRTNEWESTdosbox/main/'

    # List of files in the repository (Add all filenames to download)
    files_to_download = [
        'file1.py',  # Example file names, add real filenames
        'file2.py',  
        'README.md',
        # Add more files as needed
    ]

    # Download each file
    for filename in files_to_download:
        file_url = urljoin(repo_url, filename)
        download_file(file_url, install_dir)

if __name__ == '__main__':
    main()