# conda activate extras2

import asyncio
import g4f

async def main():
    response = await g4f.ChatCompletion.create_async(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Расскажи анекдот"}]
    )
    print(response)

asyncio.run(main())