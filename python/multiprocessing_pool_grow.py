#!/usr/bin/env python3

# how to add specific number of additional workers to an exisiting multiprocessing pool?
# https://stackoverflow.com/questions/60149376

# multiprocessing.Pool [1] with dynamic size
# [1] https://github.com/python/cpython/blob/117217245390ed3e6fe166180f052e022d296921/Lib/multiprocessing/pool.py#L173

# full example based on the answer by ZF007

import multiprocessing, time, random

def worker_function(job_id):
    dt = random.randint(1, 10)
    print(f"job {job_id}: sleeping for {dt} seconds")
    time.sleep(dt)
    return job_id * job_id

def get_job_done(job_id):
    return lambda val: print(f"job {job_id}: job done: val={val}")

def grow_pool(pool, new_size, max_size=None):
    new_size = min(new_size, max_size) if max_size else new_size
    if new_size > pool._processes:
        print(f"growing pool from {pool._processes} to {new_size}")
        pool._processes = new_size
        pool._repopulate_pool()

if __name__ == "__main__":

    # start pool
    start_workers = 1 # start N workers before demand
    max_workers = 4 # run N workers on demand
    pool = multiprocessing.Pool(start_workers)

    # add jobs
    num_jobs = 10
    grow_pool(pool, num_jobs, max_workers)
    for job_id in range(0, num_jobs):
        job_done = get_job_done(job_id)
        print(f"job {job_id}: adding job")
        pool.apply_async(worker_function, args=(job_id,), callback=job_done)

    # wait
    pool.close()
    pool.join()
