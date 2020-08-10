from bootstrap import load_env
from redis_cluster_client import RedisClusterClient
from faker import Faker
import uuid
import os
import asyncio


# from multiprocessing import Process

# an unique id as the key for redis
def get_random_number():
    return uuid.uuid4().hex[:6].upper()


# the actual worker that is writing to redis
async def worker(redis_cluster_client, faker_client, data, single_worker_limit):
    print("[+]----------./starting worker---------[+]")
    tasks = []
    for x in range(single_worker_limit):
        task = work(x, redis_cluster_client, faker_client, data)
        tasks.append(task)
    await asyncio.wait(tasks)
    print("[+]----------./ending worker---------[+]")


async def work(job_id,redis_cluster_client,faker_client,data):
    unique_id = get_random_number()
    name = faker_client.name()
    redis_cluster_client.instance().set(unique_id, name)
    data.append(unique_id)
    print("{0} \t| {1} \t| {2}".format(job_id, unique_id, name))


# write data to a database (file for this demo)
def save_data(data_source):
    print("Saving data to data.txt")
    with open('data.txt', 'w') as f:
        for item in data_source:
            f.write("%s\n" % item)


# bootstrap app.
# enables support for environment variables via .env file
load_env()

# create new redis cluster client instance
redis_cluster = RedisClusterClient()

db_data = []

faker = Faker()

single_worker_handles = int(os.getenv("SINGLE_WORKER_HANDLES"))

counter = int(os.getenv("COUNTER"))

save_data(data_source=db_data)


async def async_worker():
    event_loop_record = []
    for x in range(counter):
        event = worker(redis_cluster_client=redis_cluster,
                       faker_client=faker,
                       data=db_data,
                       single_worker_limit=single_worker_handles)
        event_loop_record.append(event)

    await asyncio.wait(event_loop_record)


async def main():
    await async_worker()
    save_data(data_source=db_data)


if __name__ == '__main__':
    print("[+]----------./firing redis cluster for writing---------[+]")
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())
    loop.close()
    print("[+]----------End of the line---------[+]")
