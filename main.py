import os
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
        await self.tree.sync()
        print("Commandes slash synchronisées avec succès !")

bot = BotVerification()

# ==================== VRAIS IDs DE TON SERVEUR ====================
ROLE_VERIFIED_ID = 1497741720698228778      # Rôle Verified
ROLE_GENDER_MALE_ID = 1497937296140275846    # Boy
ROLE_GENDER_FEMALE_ID = 1497936770166296747  # Girl

# Grades (1 Bac / 2 Bac / CPGE)
ROLE_GRADE_1BAC_PC_ID = 1542096954576736267  # 1 bac pc
ROLE_GRADE_1BAC_SM_ID = 1542096885316059256  # 1 bac sm
ROLE_GRADE_2BAC_SM_ID = 1497943305315684384  # 2 bac sm
ROLE_GRADE_2BAC_PC_ID = 1497943106719318146  # 2 bac pc
ROLE_GRADE_2BAC_SVT_ID = 1497942806327463957 # 2 bac svt
ROLE_GRADE_CPGE_MP_ID = 1542175837887926372  # CPGE MP
ROLE_GRADE_CPGE_EST_ID = 1542105302177026118 # CPGE EST
ROLE_GRADE_CPGE_TSI_ID = 1542105252176724059 # CPGE TSI
ROLE_GRADE_CPGE_MPSI_ID = 1542104923343429652 # CPGE MPSI
# ==================================================================

# 1. MENU DÉROULANT POUR LES GRADES
class GradeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="2 Bac SM", description="2ème Bac Sciences Mathématiques", emoji="🎓"),
            discord.SelectOption(label="2 Bac PC", description="2ème Bac Physique-Chimie", emoji="🧪"),
            discord.SelectOption(label="2 Bac SVT", description="2ème Bac Sciences de la Vie et de la Terre", emoji="🧬"),
            discord.SelectOption(label="1 Bac SM", description="1ère Bac Sciences Mathématiques", emoji="📐"),
            discord.SelectOption(label="1 Bac PC", description="1ère Bac Physique-Chimie", emoji="🔬"),
            discord.SelectOption(label="CPGE MP", description="Classes Préparatoires MP", emoji="⚡"),
            discord.SelectOption(label="CPGE MPSI", description="Classes Préparatoires MPSI", emoji="📊"),
            discord.SelectOption(label="CPGE TSI", description="Classes Préparatoires TSI", emoji="⚙️"),
            discord.SelectOption(label="CPGE EST", description="Classes Préparatoires EST", emoji="🏛️"),
        ]
        super().__init__(placeholder="Choisis ton Grade...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        
        # Liste de tous les rôles de grades possibles pour le nettoyage
        all_grades = [
            ROLE_GRADE_1BAC_PC_ID, ROLE_GRADE_1BAC_SM_ID,
            ROLE_GRADE_2BAC_SM_ID, ROLE_GRADE_2BAC_PC_ID, ROLE_GRADE_2BAC_SVT_ID,
            ROLE_GRADE_CPGE_MP_ID, ROLE_GRADE_CPGE_EST_ID,
            ROLE_GRADE_CPGE_TSI_ID, ROLE_GRADE_CPGE_MPSI_ID
        ]

        # Retirer tous les anciens grades du membre
        for role_id in all_grades:
            r = guild.get_role(role_id)
            if r and r in member.roles:
                await member.remove_roles(r)

        # Assigner le nouveau rôle sélectionné
        selected = self.values[0]
        mapping = {
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

        target_role_id = mapping.get(selected)
        if target_role_id:
            target_role = guild.get_role(target_role_id)
            if target_role:
                await member.add_roles(target_role)
                await interaction.response.send_message(f"✅ Ton grade **{selected}** a bien été attribué !", ephemeral=True)
                return

        await interaction.response.send_message("❌ Erreur : Impossible d'attribuer ce grade.", ephemeral=True)

# 2. FORMULAIRE MODAL (S'ouvre avec le bouton vert)
class VerifModal(discord.ui.Modal, title="Formulaire de Vérification"):
    genre_input = discord.ui.TextInput(
        label="Ton Genre (Boy / Girl ou Homme / Femme)",
        placeholder="Écris boy ou girl...",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        valeur_genre = self.genre_input.value.strip().lower()
        member = interaction.user
        guild = interaction.guild

        role_verified = guild.get_role(ROLE_VERIFIED_ID)
        r_boy = guild.get_role(ROLE_GENDER_MALE_ID)
        r_girl = guild.get_role(ROLE_GENDER_FEMALE_ID)

        assigned_gender = None
        if "boy" in valeur_genre or "homme" in valeur_genre or "garcon" in valeur_genre:
            assigned_gender = r_boy
        elif "girl" in valeur_genre or "femme" in valeur_genre or "fille" in valeur_genre:
            assigned_gender = r_girl

        roles_to_add = [role_verified]
        if assigned_gender:
            roles_to_add.append(assigned_gender)

        try:
            await member.add_roles(*[r for r in roles_to_add if r])
            await interaction.response.send_message("🎉 Vérification réussie ! Ton rôle Verified et ton genre ont été attribués.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'attribution des rôles.", ephemeral=True)

# 3. VUE AVEC LE BOUTON VERT ET LE MENU DÉROULANT
class VerifView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GradeSelect())

    @discord.ui.button(label="Ouvrir le formulaire de vérification", style=discord.ButtonStyle.green, emoji="🔓")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerifModal())

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")

# Commande slash /setup_verif
@bot.tree.command(name="setup_verif", description="Envoie le panneau de vérification du serveur")
@app_commands.default_permissions(administrator=True)
async def setup_verif(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔒 Panneau de Vérification",
        description=(
            "1. Sélectionne ton **Grade** (2 Bac, 1 Bac ou CPGE) dans le menu déroulant.\n"
            "2. Clique sur le bouton vert pour entrer ton **Genre** (Boy/Girl) et valider ta vérification !"
        ),
        color=discord.Color.blurple()
    )
    await interaction.channel.send(embed=embed, view=VerifView())
    await interaction.response.send_message("✅ Panneau de vérification généré avec succès !", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("Erreur : Le token DISCORD_TOKEN n'a pas été trouvé !")
else:
    bot.run(TOKEN)
