import discord
from discord import ui, app_commands
from discord.ext import commands
import asyncio

from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

from pymongo import MongoClient

import gspread

gc = gspread.service_account(filename="envs/credentials.json")
wks = gc.open("Ticket Process Transcripts").sheet1

env_path = Path(__file__).parent.parent.parent / 'envs' / 'handybot.env'
load_dotenv(dotenv_path=env_path)

token = os.getenv('JAKEY_DC')
mongopw = os.getenv('MONGO_PW')

connection_string = f"mongodb+srv://jctacogue:{mongopw}@cluster1.plrv4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/',intents=intents)

mongoclient = MongoClient(connection_string)
dbs = mongoclient.Handybot
coll = dbs.ModalForm

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'We have logged in as {bot.user}')

class FeedbackModal(ui.Modal, title="Feedback Form"):
    wallet = ui.Label(text="Wallet Address", component=ui.TextInput())
    email = ui.Label(text="Email Address", component=ui.TextInput())

    async def on_submit(self, interaction: discord.Interaction): # MUST BE CHANGED
        combined = (
            f"{self.wallet.component.value}\n"
            f"{self.email.component.value}\n"
            f"{interaction.user}\n"
            f"{interaction.channel.name}"
        )
        await interaction.response.send_message(f"Here is the following information you have shared, {interaction.user.display_name}. Our moderator will be with you shortly!")
        await interaction.followup.send(combined)

class FeedbackView(ui.View):
    def __init__(self):
        super().__init__()

    @ui.button(label="Feedback Modal", style=discord.ButtonStyle.success)
    async def feedback_button(self, interaction: discord.Interaction, button:ui.Button):
        await interaction.response.send_modal(FeedbackModal())

@bot.event
async def on_guild_channel_create(channel):
    view = FeedbackView()
    await channel.send(content=f"Channel created {channel.name}",view=view)

@bot.command(name="log")
async def log(ctx: commands.Context):
    if ctx.message.reference is None:
        await ctx.reply("Please reply to a feedback message!", ephemeral=True)
        return
    message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    created_time = ctx.channel.created_at
    date_time = created_time.strftime("%m/%d/%Y")
    parts = message.content.split("\n")
    info_document = {
        "wallet_address": parts[0],
        "email_address": parts[1],
        "discord_handle": parts[2],
        "ticket": parts[3],
        "ticket_open_date": date_time,
        "status": "Pending",
        "synced_to_sheets": False
    }
    coll.insert_one(info_document)
    await ctx.reply("Recorded to database", ephemeral=True)

@bot.tree.command(name="transcribe", description="Transcribe a user's record to the sheet.")
@app_commands.describe(
    status="Set the status of the ticket."
)
@app_commands.choices(status=[
    app_commands.Choice(name="Resolved", value="Resolved"),
    app_commands.Choice(name="Unresolved", value="Unresolved"),
    app_commands.Choice(name="Unresponsive", value="Unresponsive"),
])
async def transcribe(ctx: discord.Interaction, status:app_commands.Choice[str]):
    await ctx.response.defer()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: coll.find_one({"ticket": ctx.channel.name}))
    if not result:
        await ctx.followup.send("Failed.")
        return
    
    next_row = await loop.run_in_executor(None, lambda: len(wks.col_values(1)) + 1)
    target_row = f"A{next_row}:G{next_row}"
    today = datetime.now().strftime("%m/%d/%Y")
    await loop.run_in_executor(None, lambda: wks.update([[
        result["ticket_open_date"],
        result["discord_handle"],
        result["ticket"],
        status.value,
        f"Wallet: {result['wallet_address']}\nEmail: {result['email_address']}",
        today,
        ctx.user.name]],
        target_row
    ))
    
    await loop.run_in_executor(None, lambda: coll.update_one({"ticket": ctx.channel.name}, {"$set": {"synced_to_sheets": True,"ticket_close_date": today,"status": status.value}}))

    await ctx.followup.send(f"Transcribed {ctx.user.display_name}'s record successfully.", ephemeral=True)

bot.run(token)