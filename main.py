import os
import csv
import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class BotVerification(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        GUILD_ID = discord.Object(id=1493595559876100166)
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)
        print("Commandes synchronisées instantanément sur le serveur !")

bot = BotVerification()

# ==================== VRAIS IDs DE TON SERVEUR ====================
GUILD_ID_NUM = 1493595559876100166

ROLE_VERIFIED_ID = 1497741720698228778      # Rôle Verified
ROLE_UNVERIFIED_ID = 1541221546167898292    # Rôle Unverified (à retirer)
ROLE_VERIF_TEAM_ID = 1541221619807158304    # Rôle Verif Team (autorisé à utiliser la commande)

ROLE_GENDER_MALE_ID = 1497937296140275846    # Boy
ROLE_GENDER_FEMALE_ID = 1497936770166296747  # Girl

# Grades
ROLE_GRADE_1BAC_PC_ID = 1542096954576736267  
ROLE_GRADE_1BAC_SM_ID = 1542096885316059256  
ROLE_GRADE_2BAC_SM_ID = 1497943305315684384  
ROLE_GRADE_2BAC_PC_ID = 1497943106719318146  
ROLE_GRADE_2BAC_SVT_ID = 1497942806327463957 
ROLE_GRADE_CPGE_MP_ID = 1542175837887926372  
ROLE_GRADE_CPGE_EST_ID = 1542105302177026118 
ROLE_GRADE_CPGE_TSI_ID = 1542105252176724059 
ROLE_GRADE_CPGE_MPSI_ID = 1542104923343429652 
# ==================================================================

def sauvegarder_donnees(user_id, gender, grade):
    fichier = "utilisateurs.csv"
    lignes = []
    trouve = False

    if os.path.exists(fichier):
        with open(fichier, mode="r", encoding="utf-8") as f:
            lecteur = csv.reader(f)
            for ligne in lecteur:
                if ligne and ligne[0] == str(user_id):
                    trouve = True
                    lignes.append([str(user_id), gender, grade])
                else:
                    lignes.append(ligne)

    if not trouve:
        lignes.append([str(user_id), gender, grade])

    with open(fichier, mode="w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["id", "gender", "grade"])
        ecrivain.writerows(lignes)


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")


# COMMANDE SLASH POUR VÉRIFIER UN MEMBRE
@bot.tree.command(name="verifier_membre", description="Vérifie un membre en lui donnant ses rôles (Réservé à la Verif Team)")
@app_commands.describe(
    member_id="Colle l'ID Discord du membre unverified",
    gender="Choisis le genre du membre",
    grade="Choisis le grade du membre"
)
@app_commands.choices(gender=[
    app_commands.Choice(name="Boy", value="Boy"),
    app_commands.Choice(name="Girl", value="Girl")
], grade=[
    app_commands.Choice(name="2 Bac SM", value="2 Bac SM"),
    app_commands.Choice(name="2 Bac PC", value="2 Bac PC"),
    app_commands.Choice(name="2 Bac SVT", value="2 Bac SVT"),
    app_commands.Choice(name="1 Bac SM", value="1 Bac SM"),
    app_commands.Choice(name="1 Bac PC", value="1 Bac PC"),
    app_commands.Choice(name="CPGE MP", value="CPGE MP"),
    app_commands.Choice(name="CPGE MPSI", value="CPGE MPSI"),
    app_commands.Choice(name="CPGE TSI", value="CPGE TSI"),
    app_commands.Choice(name="CPGE EST", value="CPGE EST"),
])
async def verifier_membre(interaction: discord.Interaction, member_id: str, gender: app_commands.Choice[str], grade: app_commands.Choice[str]):
    # Vérifie si l'utilisateur a le rôle Verif Team ou s'il est Administrateur
    has_role = any(role.id == ROLE_VERIF_TEAM_ID for role in interaction.user.roles)
    is_admin = interaction.user.guild_permissions.administrator

    if not has_role and not is_admin:
        await interaction.response.send_message("❌ Tu dois faire partie de la Verif Team pour utiliser cette commande.", ephemeral=True)
        return

    guild = interaction.guild
    
    try:
        member = await guild.fetch_member(int(member_id))
    except Exception:
        await interaction.response.send_message("❌ Erreur : Impossible de trouver un membre avec cet ID sur le serveur.", ephemeral=True)
        return

    r_verified = guild.get_role(ROLE_VERIFIED_ID)
    r_unverified = guild.get_role(ROLE_UNVERIFIED_ID)
    r_gender = guild.get_role(ROLE_GENDER_MALE_ID) if gender.value == "Boy" else guild.get_role(ROLE_GENDER_FEMALE_ID)

    grade_mapping = {
        "2 Bac SM": ROLE_GRADE_2BAC_SM_ID,
        "2 Bac PC": ROLE_GRADE_2BAC_PC_ID,
        "2 Bac SVT": ROLE_GRADE_2BAC_SVT_ID,
        "1 Bac SM": ROLE_GRADE_1BAC_SM_ID,
        "1 Bac PC": ROLE_GRADE_1BAC_PC_ID,
        "CPGE MP": ROLE_GRADE_CPGE_MP_ID,
        "CPGE MPSI": ROLE_GRADE_CPGE_MPSI_ID,
        "CPGE TSI": ROLE_GRADE_CPGE_TSI_ID,
        "CPGE EST": ROLE_GRADE_CPGE_EST_ID,
    }
    r_grade = guild.get_role(grade_mapping.get(grade.value))

    try:
        if r_unverified and r_unverified in member.roles:
            await member.remove_roles(r_unverified)
        
        roles_to_add = [r_verified, r_gender, r_grade]
        await member.add_roles(*[r for r in roles_to_add if r])

        sauvegarder_donnees(member.id, gender.value, grade.value)

        await interaction.response.send_message(f"✅ Succès ! Le membre <@{member.id}> a été vérifié avec le genre **{gender.value}** et le grade **{grade.value}**.", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue lors de l'attribution des rôles : {e}", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("Erreur : Le token DISCORD_TOKEN n'a pas été trouvé !")
else:
    bot.run(TOKEN)
