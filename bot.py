import discord
import os
import dotenv
import asyncio
import collections
import operator

dotenv.load_dotenv()


class MyClient(discord.Client):

    votes = {}
    voted_list = []

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print(message)
        print(message.channel.id)
        if "!newvote" in message.content:
            # print(type(message.content))
            self.new_vote(message)

        elif "!vote" in message.content:
            self.add_vote(message)

        elif "!changevote" in message.content:
            self.change_vote(message)

        elif "!endvote" in message.content:
            # Finds the largest item in the dictionary by sorting based on the vote count value.
            winner_key = max(self.votes, key= (lambda key_val: self.votes[key_val]["Vote Count"]) )
            print(self.votes[winner_key]["Movie Name"])

    def get_message_content(self, message_string):
        return message_string.content.split(" ")[1:]

    def new_vote(self, message):
        movies = message.content.replace("!newvote ", "").split(", ")

        for i, movie in enumerate(movies, start=1):
            self.votes[i] = {"Movie Name" : movie, "Vote Count" : 0}

        print(self.votes)

    async def add_vote(self, options):
        message_author = options.author.name

        for voter in self.voted_list:
            if voter[message_author]:
                print(message_author + " has already voted.")
                await options.author.send("voted")

                # CHANGED VOTED LIST TO DICT FOR FAST ACCESS.
        
        else:
            choices = self.get_message_content(options)
            vote_store = {message_author : [val for val in choices]}
            for value in choices:
                self.votes[int(value)]["Vote Count"] += 1

            # print(message_author + " vote added")
            print(vote_store)
            self.voted_list.append(vote_store)
        
        

    def change_vote(self, new_options):
        message_author = new_options.author.name
        old_choices = None
        new_choices = self.get_message_content(new_options)

        for voter in self.voted_list:
            if voter[message_author]:
                old_choices = voter[message_author]

        for choice in old_choices:
            self.votes[int(choice)]["Vote Count"] -= 1

        for choice in new_choices:
            self.votes[int(choice)]["Vote Count"] += 1

        print("Vote changed: ", message_author)
        print(self.votes)
        

client = MyClient()
client.run(os.getenv("API_KEY"))
