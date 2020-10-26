import os

import discord
import dotenv
import yaml


def load_config():

    config_map = {
        "testing": "/app/config.yaml",
        "production": "/app/config.yaml",
        "ci-tests": "config.yaml",
        "local": "config.yaml",
    }

    bot_env = os.getenv("bot_environment")

    with open(config_map[bot_env], "r") as conf:

        try:

            info = yaml.safe_load(conf)

            return {"key": info["API_KEY"], "channel": info[bot_env]["CHANNEL_ID"]}

        except yaml.YAMLError as exc:
            print("Error loading YAML:", exc)


class MyClient(discord.Client):

    votes = {}
    already_voted = {}
    vote_store = []

    # Confirm bot has joined the channel and is reading messages.
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    # Asynchronous function for reading messages awaiting the appropriate commands.
    async def on_message(self, message):

        if message.channel.id == config["channel"]:

            if message.content.startswith("!newvote"):
                await self.new_vote(message)

            elif message.content.startswith("!vote"):
                await self.add_vote(message)

            elif message.content.startswith("!changevote"):
                await self.change_vote(message)

            elif message.content == "!endtest":
                await self.__end_test(message)

            elif "!endvote" in message.content:

                if "Admin" in [role.name for role in message.author.roles]:

                    # Finds the largest item in the dictionary by sorting based on the vote count value.
                    winner_key = max(
                        self.votes,
                        key=(lambda key_val: self.votes[key_val]["Vote Count"]),
                    )

                    await self.channel_message(
                        f"{self.votes[winner_key]['Movie Name']} wins with {self.votes[winner_key]['Vote Count']} points."
                    )
                    self.already_voted.clear()
                    self.votes.clear()

    # Split vote choices, removing the command prefix and return resulting list.
    def get_message_content(self, message_string):
        return message_string.content.split(" ")[1:]

    # Allows only 'Admin' roles to start votes, displays all vote possibilities to users in channel.
    async def new_vote(self, message):

        if "Admin" in [role.name for role in message.author.roles]:
            movies = message.content.replace("!newvote ", "").split(",")
            for i, movie in enumerate(movies, start=1):
                self.votes[i] = {"Movie Name": movie, "Vote Count": 0}

            movie_string = ""

            for index, movie in enumerate(self.votes.values(), start=1):
                movie_string += f"{index}: {movie['Movie Name']}\n"

            await self.channel_message(
                f"Use `!vote X Y Z` to place your votes\nChanges to votes are done by using `!changevote X Y Z`\n Movies to vote on: \n {movie_string}"
            )

        else:
            await self.channel_message(
                f"{message.author.mention}, only those with the role of 'Admin' can start votes."
            )

    # Checks whether there are duplicates within somebodies vote, this is not allowed.
    def check_duplicates(self, choices):
        return len(choices) != len(set(choices))

    # Add a vote to the current movies available.
    async def add_vote(self, message):
        message_author = message.author.name

        try:

            if self.already_voted[message_author]:
                print(message_author + " attempted to vote twice using !vote.")
                await self.channel_message(
                    f"{message.author.mention}, you have already voted. Use `!changevote`."
                )

        except:

            choices = self.get_message_content(message)

            if self.zero_or_negative_votes(choices):
                await self.channel_message(
                    f"{message.author.mention}, you cannot vote with a negative number."
                )

            if len(choices) <= 3:

                if self.check_duplicates(choices):
                    await self.channel_message(
                        f"{message.author.mention}, there should be no duplicates in your vote."
                    )
                    return

                elif self.check_key_error(choices):
                    await self.channel_message(
                        f"{message.author.mention}, you cannot vote for something outside of the list."
                    )
                    return

                i = 3

                for value in choices:
                    self.votes[int(value)]["Vote Count"] += i
                    i -= 1

                self.store_choices(choices, message_author)
                print(self.already_voted)
                await self.standings_display()

            else:
                await self.channel_message(
                    f"{message.author.mention}, you cannot vote for more than 3 things at time."
                )

    # Allow a user to change their vote by reading the stored vote generated previously, removing their old vote and reapplying the new one.
    async def change_vote(self, message):
        message_author = message.author.name
        old_choices = None
        new_choices = self.get_message_content(message)

        if self.zero_or_negative_votes(new_choices):
            await self.channel_message(
                f"{message.author.mention}, you cannot vote with a negative number."
            )

        if len(new_choices) > 3:
            await self.channel_message(
                f"{message.author.mention}, you cannot vote for more than 3 movies."
            )
            return

        if self.check_duplicates(new_choices):
            await self.channel_message(
                f"{message.author.mention}, you cannot vote for the same movie multiple times in the same vote."
            )
            return

        for voter in self.already_voted.keys():

            if voter == message_author:
                old_choices = self.already_voted[message_author]

        if old_choices == new_choices:
            print("Same votes to change")
            await self.channel_message(
                f"{message.author.mention}, you cannot change your vote to the same vote."
            )
            return

        elif self.check_key_error(new_choices):
            await self.channel_message(f"{message.author.mention}, you're a cunt :) .")
            return

        i = 3
        for choice in old_choices:
            self.votes[int(choice)]["Vote Count"] -= i
            i -= 1

        j = 3
        for choice in new_choices:
            self.votes[int(choice)]["Vote Count"] += j
            j -= 1

        self.store_choices(new_choices, message_author)

        await self.channel_message(f"{message.author.mention} vote changed.")
        await self.standings_display()
        print("Vote changed: ", message_author)

    async def __end_test(self, message):
        if (
            message.author.id == 763492591303655434
            or message.author.id == 187697230767980545
        ):
            white_check_mark_unicode_character = "✅"
            await message.add_reaction(white_check_mark_unicode_character)
            await self.close()

    # Wrapper function for sending a message into the relevant channel, this is always the same designated channel e.g. #movie-voting
    async def channel_message(self, message):
        chan = self.get_channel(config["channel"])
        await chan.send(message)

    # Displays the standings after each vote or change vote, this shows votes in descending order.
    async def standings_display(self):

        sorted_by_vote_count = {
            k: v
            for k, v in sorted(
                self.votes.items(), key=(lambda x: x[1]["Vote Count"]), reverse=True
            )
        }
        msg = ""
        for key in sorted_by_vote_count:
            msg += f"**{key}**: {sorted_by_vote_count[key]['Movie Name']}. Points: {sorted_by_vote_count[key]['Vote Count']}\n"

        await self.channel_message(msg)

    # Helper function to ensure that there are no negative or 0 votes within the choices.
    def zero_or_negative_votes(self, movie_votes):

        for vote in movie_votes:
            if int(vote) <= 0:
                return True

        return False

    def check_key_error(self, movie_votes):

        try:
            for vote in movie_votes:
                self.votes[int(vote)]
            return False

        except KeyError:
            return True

    def store_choices(self, choices, message_author):

        vote_hold = [val for val in choices]
        self.already_voted[message_author] = vote_hold
        return


config = load_config()
client = MyClient()
client.run(config["key"])
