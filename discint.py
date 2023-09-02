import settings
import cyril

import discord
from discord.ext import commands

def start_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="-", intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} [{bot.user.id}] starting")


    @bot.command(
            aliases=['playlistSearch', 'listSongs']
    )
    async def list_songs(ctx, arg):
        playlist = cyril.search_playlist(arg)
        playlist_name = list(playlist.keys())[0]
        print(playlist)
        embed = discord.Embed(title="Cyril", color=discord.Color.from_rgb(170, 250, 191))
        embed.add_field(name=f"Songs in **{playlist_name}**", value=len(playlist[playlist_name]))
        for song in playlist[playlist_name]:
            embed.add_field(name=f"**{song['song_title']}**", value=f"` Artist ` *{song['main_artist']}* \n` Featuring Artists ` *{', '.join(song['featuring_artists'])}*\n` Length (seconds) ` *{song['length']}*\n` Global Plays ` *{song['global_plays']}*", inline=False)
        embed.set_footer(text="Cyril | Created by ZEYL")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1147515757245235293/8e2002fc3917f5625c074f80e09f561e")
        await ctx.send(embed=embed)


    bot.run(settings.DISCORD_SECRET)

if __name__ == "__main__":
    start_bot()