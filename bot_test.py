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

    bot_command = "!newvote test_movie1"

    await interface.assert_reply_contains(bot_command, "1: test_movie1")


@test_collector()
async def test_movie_vote(interface):

    bot_command = "!vote 1"

    await interface.assert_reply_contains(bot_command, "test_movie1. Points: 3")


@test_collector()
async def test_cleanup(interface):
    bot_command = "!endvote"

    await interface.assert_reply_contains(bot_command, "wins with")


if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
