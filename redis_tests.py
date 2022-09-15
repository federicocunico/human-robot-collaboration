from threading import Thread
import time
import redis


class RedisPublisher(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.redis = redis.Redis("127.0.0.1", 6379, 0)

    def run(self) -> None:
        i = 0
        while True:
            print(f"Publishing: {i}")
            # self.redis.set("__test__", i)
            self.redis.publish("__test__", i)
            i += 1
            time.sleep(3)


class RedisSubscriber(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.redis = redis.Redis(
            "127.0.0.1", 6379, 0, decode_responses=True, charset="utf-8"
        )

    def get_message(self, timeout):
        val = None
        msg = self.sub.get_message(timeout=timeout)
        while msg is not None:
            val = msg
            msg = self.sub.get_message(timeout=timeout)
        return val

    def run(self) -> None:

        print("Creating subscribing")
        self.sub = self.redis.pubsub()

        self.sub.subscribe("__test__")

        while True:

            val = self.get_message(timeout=0.1)
            if val is not None:
                print("Got", val["data"])
            else:
                print("Got None")
            time.sleep(0.1)


def main():
    RedisPublisher().start()
    RedisSubscriber().start()

    while True:
        pass


if __name__ == "__main__":
    main()
