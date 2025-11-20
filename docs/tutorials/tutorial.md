# Getting Started with Lykos - A Simple Tutorial

This tutorial covers the basics of setting up and using Lykos. I wrote this while learning how to use it, so it might help other beginners too.

## What is Lykos?

Lykos is a bot for playing Werewolf (or Mafia) games on IRC. You join a channel, type `!join` and then play a game where some people are wolves and some are villagers.

## First Steps

### Installing the Bot

First you need to get the code. Use git to clone it:

```bash
git clone https://github.com/lykoss/lykos.git
cd lykos
```

The project uses Poetry for dependency management. Install Poetry first if you don't have it, then run:

```bash
poetry install
```

This will install all the required dependencies.

### Setting Up the Config

Copy the `botconfig.example.yml` file and name it `botconfig.yml`:

```bash
cp botconfig.example.yml botconfig.yml
```

Open it in a text editor and update the following:
- The IRC server address (for example, libera.chat)
- Your username so the bot knows you're the admin
- Other settings as needed (the file has comments explaining what each setting does)

### Running the Bot

To start the bot, run:

```bash
poetry run lykos-bot
```

Or you can do:

```bash
poetry run python wolfbot.py
```

Both work the same way. The bot should connect to IRC and join your channel. If something goes wrong check the error messages - they usually tell you what's wrong.

## Playing Your First Game

### Joining a Game

Once the bot is running in your IRC channel, you can join a game by typing:

```
!join
```

You need at least 6 people to start a game. The bot will tell you how many people have joined.

### Starting the Game

When enough people join, someone with permissions (like you if you're the admin) can start the game with:

```
!start
```

The bot will then message you privately with your role. Check your private messages from the bot.

### Understanding Your Role

The bot will tell you:
- What role you are (villager, wolf, seer, etc.)
- What commands you can use
- What your goal is

For example, if you're a wolf, you can talk to other wolves in a private chat. If you're a seer, you can check if someone is a wolf or not.

### Basic Commands

Here are some basic commands:

- `!join` - Join a game
- `!leave` - Leave a game (before it starts)
- `!start` - Start the game (admin only)
- `!players` - See who's in the game
- `!vote <player>` - Vote to eliminate someone during the day phase

Different roles have different commands. The bot will tell you what you can do when the game starts.

## Tips I Learned

1. **Read the private messages from the bot** - The bot tells you everything you need to know about your role and available commands.

2. **Pay attention to the game phases** - There's a day phase (everyone talks) and night phase (wolves and special roles do things). The bot will tell you when it's day or night.

3. **If you're a wolf** - You can talk to other wolves privately. Message the bot and it will relay to other wolves. Don't talk about being a wolf in the main channel.

4. **If you're a special role** - Use your powers. For example, if you're a seer, check people to see if they're wolves. Be careful - if wolves find out what you are, they might kill you at night.

5. **Practice helps** - The first few games can be confusing, but after a few games it starts making sense.

## Common Problems

### The bot won't connect

- Check your `botconfig.yml` file - make sure the server address is right
- Make sure your IRC network allows bots
- Check if you need to register the bot's nickname first

### The bot connects but doesn't respond

- Make sure the bot has permissions in the channel (ops or voice)
- Check that you're using the right commands (they start with `!`)
- Make sure you're in the right channel

### I don't understand what's happening

- Read the bot's messages carefully
- Ask other players for help
- Try playing as a simple villager first to learn the basics

## Adding Custom Roles (Advanced)

To add your own role, there's a file called `src/roles/_skel.py` which is a template. Copy it and modify it to create your own role. This requires understanding Python and how the game works. The file has comments that explain the structure.

## Where to Get Help

If you're stuck, you can:
- Check the README.md file (it has more info)
- Look at the wiki (there's a link in the README)
- Ask in the #lykos channel on Libera IRC
- Read the code comments (they're actually pretty helpful)

## Final Thoughts

Lykos takes some time to understand, but once you get the basics it becomes easier to use. The code is open source, so you can look at it and modify it if needed.

If you find mistakes in this tutorial or want to add something, feel free to update it.

