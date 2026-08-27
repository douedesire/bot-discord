import os
import discord
from discord.ext import commands
from discord import app_commands

# Configuration des intents du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Indispensable pour gérer les rôles

class BotVérification(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronise les commandes slash avec ton serveur
        await self.tree.sync()
        print("Commandes slash synchronisées avec succès !")

bot = BotVérification()

# ==================== CONFIGURATION DES IDs ====================
# Remplace par les vrais ID de ton serveur Discord (clic droit -> Copier l'ID)
ROLE_VERIFIED_ID = 000000000000000000  
ROLE_GENDER_MALE_ID = 000000000000000000  
ROLE_GENDER_FEMALE_ID = 000000000000000000  
ROLE_GRADE_ID = 000000000000000000  
# ===============================================================

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    print("Le bot est prêt et en ligne !")

# Commande slash /setup_verif
@bot.tree.command(name="setup_verif", description="Envoie le message de vérification du serveur")
@app_commands.default_permissions(administrator=True) # Réservé aux admins
async def setup_verif(interaction: discord.Interaction):
    # Répond à l'interaction pour éviter l'erreur "The application did not respond"
    await interaction.response.send_message("✅ Le système de vérification a bien été initialisé ici !", ephemeral=True)
    
    # Ici tu pourras ajouter un bouton de validation si tu le souhaites par la suite

# Récupération sécurisée du token depuis Railway
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("Erreur : Le token DISCORD_TOKEN n'a pas été trouvé dans les variables d'environnement !")
else:
    bot.run(TOKEN)
