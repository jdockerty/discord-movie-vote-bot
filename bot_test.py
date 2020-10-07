import asyncio
import sys
from distest import TestCollector
from distest import run_interactive_bot, run_dtest_bot
import os
import yaml

test_collector = TestCollector()

@test_collector()
async def test_movie_list_reply(interface):
    """

    Test case returns a number formatted list by the vote bot.
    This should contain the string "1: <movie_name>".

    """

    message = "!newvote test_movie1"

    await interface.assert_reply_contains(message, "1: test_movie1")

if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)