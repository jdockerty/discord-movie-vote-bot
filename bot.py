import discord
import os
import dotenv
import asyncio
import collections
import operator
import json

dotenv.load_dotenv()

class MyClient(discord.Client):

    votes = {}
    already_voted = {}
    vote_store = []

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if "!newvote" in message.content:
            await self.new_vote(message)

        elif message.content.startswith("!vote"):
            await self.add_vote(message)

        elif message.content.startswith("!changevote"):
            await self.change_vote(message)

        elif "!endvote" in message.content:

            # Finds the largest item in the dictionary by sorting based on the vote count value.
            winner_key = max(self.votes, key= (lambda key_val: self.votes[key_val]["Vote Count"]))
            print(self.votes[winner_key]["Movie Name"])
            chan = self.get_channel(int(os.getenv("CHANNEL_ID")))
            await chan.send(f"{self.votes[winner_key]['Movie Name']} wins with {self.votes[winner_key]['Vote Count']} votes.")
            self.already_voted.clear()
            self.votes.clear()

    def get_message_content(self, message_string):
        return message_string.content.split(" ")[1:]

    async def new_vote(self, message):

        if "Admin" in [role.name for role in message.author.roles]:
            movies = message.content.replace("!newvote ", "").split(", ")
            for i, movie in enumerate(movies, start=1):
                self.votes[i] = {"Movie Name" : movie, "Vote Count" : 0}

            movie_string = ""
            i = 1
            for movie in self.votes.values():
                movie_string += f"{i}: {movie['Movie Name']}\n"
                i += 1
            chan = self.get_channel(int(os.getenv("CHANNEL_ID")))
            await chan.send(f"Use `!vote X Y Z` to place your votes\nChanges to votes are done by using `!changevote X Y Z`\n Movies to vote on: \n {movie_string}")

        else:
            chan = self.get_channel(int(os.getenv("CHANNEL_ID")))
            await chan.send("Only those with the role of 'Admin' can start votes.")

    async def add_vote(self, options):
        message_author = options.author.name

        try:

            if self.already_voted[message_author]:
                chan = self.get_channel(int(os.getenv("CHANNEL_ID")))
                await chan.send(message_author + " has already voted.")
        
        except:

            choices = self.get_message_content(options)
            vote_hold = [val for val in choices]
            
            i = 3
            for value in choices:
                self.votes[int(value)]["Vote Count"] += i
                i -= 1


            self.already_voted[message_author] = vote_hold
            print(self.already_voted)
        
        

    async def change_vote(self, new_options):
        message_author = new_options.author.name
        old_choices = None
        new_choices = self.get_message_content(new_options)
        for voter in self.already_voted.keys():
   
            if voter == message_author:
                print(voter, message_author)
                old_choices = self.already_voted[message_author]
        
        i = 3
        for choice in old_choices:
            self.votes[int(choice)]["Vote Count"] -= i
            i -= 1

        j = 3
        for choice in new_choices:
            self.votes[int(choice)]["Vote Count"] += j
            j -= 1

        chan = self.get_channel(int(os.getenv("CHANNEL_ID")))
        await chan.send(message_author + " vote changed.")
        print("Vote changed: ", message_author)
        

client = MyClient()
client.run(os.getenv("API_KEY"))
