import asyncio


# async def task(se: asyncio.BoundedSemaphore):
#     await se.acquire()
#     print('task created, sleeping')
#     await asyncio.sleep(5)
#     se.release()
#     print('wake up')
#
#
# async def main():
#     sem = asyncio.BoundedSemaphore(2)
#     tasks = []
#
#     for _ in range(10):
#         # await sem.acquire()
#         print('task added')
#         tasks.append(await task(sem))
#         # sem.release()
#     await asyncio.gather(*tasks)

import asyncio
import time


async def myWorker(semaphore):
    async with semaphore:
        # await semaphore.acquire()
        print("Successfully acquired the semaphore")
        await asyncio.sleep(3)
        print("Releasing Semaphore")
        # semaphore.release()


async def main():
    mySemaphore = asyncio.Semaphore(value=2)
    tasks = []
    for _ in range(3):
        tasks.append(asyncio.create_task(myWorker(mySemaphore)))
    await asyncio.gather(*tasks)
    print("Main Coroutine")

asyncio.run(main())
print("All Workers Completed")

