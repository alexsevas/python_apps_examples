# Пример использования библиотеки aioredis
# В Python aioredis — это асинхронная библиотека для работы с базой данных Redis.
# Она построена на базе asyncio и предоставляет неблокирующий интерфейс для взаимодействия с Redis, что позволяет эффективно
# обрабатывать множество запросов одновременно.
#
# Применение aioredis особенно полезно в асинхронных приложениях, где требуется высокая производительность и  отзывчивость.
# aioredis  позволяет выполнять операции с Redis без блокировки основного потока, что  повышает  эффективность  использования ресурсов.


import asyncio
import aioredis

async def redis_example():
    try:
        # Подключение к Redis
        redis = await aioredis.create_redis_pool(
            'redis://localhost',
            db=0,
            encoding='utf-8',  # Декодирование в UTF-8
            minsize=5,  # Минимальное количество соединений в пуле
            maxsize=10   # Максимальное количество соединений в пуле
        )


        # Работа со строками
        await redis.set('name', 'John Doe')
        name = await redis.get('name')
        print(f"Name: {name}") # Вывод: Name: John Doe



        # Работа со списками
        await redis.rpush('my_list', 'one', 'two', 'three')
        list_length = await redis.llen('my_list')
        list_items = await redis.lrange('my_list', 0, -1)
        print(f"List length: {list_length}") # Вывод: List length: 3
        print(f"List items: {list_items}") # Вывод: List items: ['one', 'two', 'three']


        # Работа с хэшами
        await redis.hset('user:1', 'name', 'Alice')
        await redis.hset('user:1', 'age', 30)
        user_data = await redis.hgetall('user:1')
        print(f"User data: {user_data}") # Вывод: User data: {'name': 'Alice', 'age': '30'}


        # Работа с множествами
        await redis.sadd('my_set', 'apple', 'banana', 'cherry')
        set_members = await redis.smembers('my_set')
        print(f"Set members: {set_members}") # Вывод: Set members: {'apple', 'banana', 'cherry'}



        #  Использование pipeline
        async with redis.pipeline(transaction=True) as pipe:  # transaction=True для атомарности операций
            await pipe.set('key1', 'value1')
            await pipe.get('key1')
            await pipe.hset('user:2', 'name', 'Bob')
            results = await pipe.execute()
        print(f"Pipeline results: {results}")



        redis.close()
        await redis.wait_closed()


    except aioredis.RedisError as e:
        print(f"Ошибка Redis: {e}")


if __name__ == "__main__":
    asyncio.run(redis_example())
