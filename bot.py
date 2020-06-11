import discord
import os
import dotenv
import asyncio
import collections
import operator

dotenv.load_dotenv()

class MyClient(discord.Client):

    votes = {}
    already_voted = {}
    vote_store = []

    # Confirm bot has joined the channel and is reading messages.
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    # Asynchronous function for reading messages awaiting the appropriate commands.
    async def on_message(self, message):

        if "!newvote" in message.content:
            await self.new_vote(message)

        elif message.content.startswith("!vote"):
            await self.add_vote(message)

        elif message.content.startswith("!changevote"):
            await self.change_vote(message)

        elif message.content.startswith("!standings"):
            movie_string = ""
            i = 1
            for movie in self.votes.values():

                movie_string += f"{i}: {movie['Movie Name']}. Points: {movie['Vote Count']}\n"
                i += 1
                
            await self.channel_message(movie_string)
            

        elif "!endvote" in message.content:

            if "Admin" in [role.name for role in message.author.roles]:

                # Finds the largest item in the dictionary by sorting based on the vote count value.
                winner_key = max(self.votes, key= (lambda key_val: self.votes[key_val]["Vote Count"]))

                await self.channel_message(f"{self.votes[winner_key]['Movie Name']} wins with {self.votes[winner_key]['Vote Count']} points.")
                self.already_voted.clear()
                self.votes.clear()

    # Split vote choices, removing the command prefix and return resulting list.
    def get_message_content(self, message_string):
        return message_string.content.split(" ")[1:]

    # Allows only 'Admin' roles to start votes, displays all vote possibilities to users in channel.
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
            
            await self.channel_message(f"Use `!vote X Y Z` to place your votes\nChanges to votes are done by using `!changevote X Y Z`\n Movies to vote on: \n {movie_string}")

        else:
            await self.channel_message("Only those with the role of 'Admin' can start votes.")

    # Checks whether there are duplicates within somebodies vote, this is not allowed.
    def check_duplicates(self, choices):
        return len(choices) != len(set(choices))

    # Add a vote to the current movies available.
    async def add_vote(self, options):
        message_author = options.author.name

        try:

            if self.already_voted[message_author]:
                print(message_author + " attempted to vote twice using !vote.")
                await self.channel_message(message_author + " has already voted.")
        
        except:

            choices = self.get_message_content(options)
    
            if len(choices) <= 3:

                if self.check_duplicates(choices):
                    await self.channel_message("There should be no duplicates in your vote.")
                    return

                vote_hold = [val for val in choices]
                i = 3

                for value in choices:
                    self.votes[int(value)]["Vote Count"] += i
                    i -= 1


                self.already_voted[message_author] = vote_hold
                print(self.already_voted)
        
            else:
                await self.channel_message("You cannot vote for more than 3 things at time.")


    # Allow a user to change their vote by reading the stored vote generated previously, removing their old vote and reapplying the new one.
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


        await self.channel_message(message_author + " vote changed.")
        print("Vote changed: ", message_author)

    # Wrapper function for sending a message into the relevant channel, this is always the same designated channel e.g. #bot-spam
    async def channel_message(self, message):
        chan = self.get_channel(int(os.getenv("CHANNEL_ID")))
        await chan.send(message)

client = MyClient()
client.run(os.getenv("API_KEY"))
