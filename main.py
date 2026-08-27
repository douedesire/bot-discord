import os
import discord
from discord.ext import commands

# Configuration des intents du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Nécessaire pour gérer les membres et les rôles

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CONFIGURATION DES IDs ====================
# Remplace les zéros par les vrais ID de ton serveur Discord (clic droit -> Copier l'ID)
ROLE_VERIFIED_ID = 000000000000000000  # ID du rôle Verified / Vérifié
ROLE_GENDER_MALE_ID = 000000000000000000  # ID du rôle Genre (ex: Homme)
ROLE_GENDER_FEMALE_ID = 000000000000000000  # ID du rôle Genre (ex: Femme)
ROLE_GRADE_ID = 000000000000000000  # ID du rôle Grade / Membre
# ===============================================================

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    print("Le bot est prêt et en ligne !")

# Exemple de commande de vérification qui attribue le rôle verified
@bot.command(name="verifier")
async def verifier(ctx):
    role = ctx.guild.get_role(ROLE_VERIFIED_ID)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"✅ {ctx.author.mention}, tu as bien été vérifié !")
    else:
        await ctx.send("❌ Erreur : Le rôle Verified est introuvable (vérifie l'ID).")

# Récupération sécurisée du token depuis Railway
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("Erreur : Le token DISCORD_TOKEN n'a pas été trouvé dans les variables d'environnement !")
else:
    bot.run(TOKEN)
