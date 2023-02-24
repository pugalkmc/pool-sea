import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Step 1: Authenticate and access the spreadsheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('omega-cosmos-290504-9567ce79765b.json', scope)
client = gspread.authorize(creds)

sheet_url = 'https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0'
sheet_name = 'Sheet1'
sheet = client.open_by_url(sheet_url).worksheet(sheet_name)

# Step 2: Get user input and convert usernames to Twitter profile links
username = input('Enter your username: ')
account_count = int(input('Enter the number of accounts: '))
twitter_username_list = []
for i in range(account_count):
    twitter_username = input(f'Enter Twitter username {i+1}: ')
    twitter_username_list.append(f'https://twitter.com/{twitter_username}')

# Step 3: Write the content to the spreadsheet
content_list = []
for i in range(account_count * 10):
    content = f'{username} content {i+1}'
    content_list.append(content)

for i, twitter_username in enumerate(twitter_username_list):
    start_index = i * 10
    end_index = (i + 1) * 10
    content_chunk = content_list[start_index:end_index]
    sheet.update_cell(start_index+1, 1, twitter_username)
    for j, content in enumerate(content_chunk):
        sheet.update_cell(start_index+j+1, 2, content)

# Step 4: Share the spreadsheet with view-only access
sheet.share('', perm_type='anyone', role='reader', notify=True)
print(f'View-only link: {sheet.url}')
