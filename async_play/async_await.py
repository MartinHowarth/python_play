import asyncio


async def countdown(length, name=""):
    local_var = 0
    while local_var < length:
        print(f"{name}: T-minus {length - local_var}")
        await asyncio.sleep(1)
        local_var += 1


loop = asyncio.get_event_loop()
tasks = [
    loop.create_task(countdown(5, "Five")),
    loop.create_task(countdown(3, "Three")),
]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

