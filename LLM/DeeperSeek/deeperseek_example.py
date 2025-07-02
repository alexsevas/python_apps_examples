# conda activate allpy310

import asyncio
from DeeperSeek import DeepSeek, Theme

async def main():
    # Инициализация через почту и пароль
    api = DeepSeek(
        email = "mail",
        password = "psw",
        verbose = False
    )
    # или через session_token
    '''
    api = DeepSeek(
        token = session_token,
        headless= True
    )
    '''

    await api.initialize() # Важный момент

    # Отправить сообщения DeepSeek'у
    '''
    playwright install chromium
    Downloading Chromium 138.0.7204.23 (playwright build v1179) from https://cdn.playwright.dev/dbazure/download/
    playwright/builds/chromium/1179/chromium-win64.zip
    146 MiB [====================] 100% 0.0s
    Chromium 138.0.7204.23 (playwright build v1179) downloaded to C:\-----\----\AppData\Local\ms-playwright\chromium-1179
    Downloading Chromium Headless Shell 138.0.7204.23 (playwright build v1179) from https://cdn.playwright.dev/dbazure/
    download/playwright/builds/chromium/1179/chromium-headless-shell-win64.zip
    89.8 MiB [====================] 100% 0.0s
    Chromium Headless Shell 138.0.7204.23 (playwright build v1179) downloaded to C:\-----\----\AppData\Local\ms-playwright\chromium_headless_shell-1179
    '''

    '''
    FileNotFoundError: could not find a valid chrome browser binary. please make sure chrome is installed.or use the 
    keyword argument 'browser_executable_path=/path/to/your/browser' 
    '''

    response = await api.send_message(
        "Привет, железяка!",
        slow_mode = True,
        deepthink = False,
        search = False,
        slow_mode_delay= 0.25,
        use_chromium=True
    )

    print(response)

    #print(response.text, response.chat_id) # Return type is a Response object

    # Regenerate the last response
    new_response = await api.regenerate_response() # Return type is a Response object
    print(new_response.text, new_response.chat_id)

    # Reset the chat
    await api.reset_chat()

    # Retrieve the session token (useful for debugging)
    token = await api.retrieve_token()
    print(f"Session Token: {token}")

    #await api.switch_account(token = "new_token")

    #await api.switch_account(email = "new_email", password = "<PASSWORD>")

    await api.logout()
    await api.delete_chats()
    await api.switch_chat(chat_id = new_response.chat_id)
    await api.switch_theme(Theme.DARK)


if __name__ == '__main__':
    asyncio.run(main())

'''
FileNotFoundError: could not find a valid chrome browser binary. please make sure chrome is installed.or use the keyword 
argument 'browser_executable_path=/path/to/your/browser
'''

