import sched, time
s = sched.scheduler(time.time, time.sleep)


def test_fn():
    print time.time()


s.enter(5, 1, test_fn, ())
s.run()