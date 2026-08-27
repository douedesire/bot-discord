import os
import discord
from discord.ext import commands
from discord import ui

# Récupération sécurisée du token pour l'hébergement
TOKEN = os.getenv("TOKEN")

# IDs des rôles
ROLE_VERIFIED = 1497741720698228778
ROLE_UNVERIFIED = 1541221546167898292
ROLE_BOY = 1497937296140275846
ROLE_GIRL = 1497936770166296747

# Dictionnaire complet de tous les grades (1 Bac, 2 Bac et CPGE)
GRADES_ROLES = {
    # 1 Bac
    "1bac_pc": 1542096954576736267,
    "1bac_sm": 1542096885316059256,
    # 2 Bac
    "2bac_sm": 1497943305315684384,
    "2bac_pc": 1497943106719318146,
    "2bac_svt": 1497942806327463957,
    "cmc": 1542228585471803432,
    # CPGE
    "cpge_mp": 1542175837887926372,
    "cpge_mpsi": 1542104923343429652,
    "cpge_tsi": 1542105252176724059,
    "cpge_est": 1542105302177026118
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Menu déroulant regroupant tous les Grades ---
class GradeSelect(ui.Select):
    def __init__(self):
        options = [
            # 1 Bac
            discord.SelectOption(label="1 Bac SM", value="1bac_sm"),
            discord.SelectOption(label="1 Bac PC", value="1bac_pc"),
            # 2 Bac & Autres
            discord.SelectOption(label="2 Bac SM", value="2bac_sm"),
            discord.SelectOption(label="2 Bac PC", value="2bac_pc"),
            discord.SelectOption(label="2 Bac SVT", value="2bac_svt"),
            discord.SelectOption(label="CMC", value="cmc"),
            # CPGE
            discord.SelectOption(label="CPGE MP", value="cpge_mp"),
            discord.SelectOption(label="CPGE MPSI", value="cpge_mpsi"),
            discord.SelectOption(label="CPGE TSI", value="cpge_tsi"),
            discord.SelectOption(label="CPGE EST", value="cpge_est")
        ]
        super().__init__(
            placeholder="Choisis ton Grade...", 
            min_values=1, 
            max_values=1, 
            options=options, 
            custom_id="grade_select_menu_all"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

# --- Formulaire (Modal) ---
class VerifModal(ui.Modal, title="Vérification de Membre"):
    target_id = ui.TextInput(label="User ID du membre", placeholder="Ex: 123456789012345678", required=True)
    genre = ui.TextInput(label="Genre (boy / girl)", placeholder="boy ou girl", required=True)

    def __init__(self, grade_value: str):
        super().__init__()
        self.grade_value = grade_value

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild

        user_id_str = self.target_id.value.strip()
        if not user_id_str.isdigit():
            await interaction.response.send_message("❌ L'ID utilisateur entré est invalide.", ephemeral=True)
            return

        member = guild.get_member(int(user_id_str))
        if not member:
            await interaction.response.send_message("❌ Impossible de trouver ce membre avec cet ID.", ephemeral=True)
            return

        roles_to_add = []

        # 1. Rôle Verified
        v_role = guild.get_role(ROLE_VERIFIED)
        if v_role:
            roles_to_add.append(v_role)

        # 2. Rôle Genre
        genre_val = self.genre.value.strip().lower()
        genre_id = ROLE_BOY if "boy" in genre_val else ROLE_GIRL
        g_role = guild.get_role(genre_id)
        if g_role:
            roles_to_add.append(g_role)

        # 3. Rôle Grade (depuis le menu sélectionné)
        grade_id = GRADES_ROLES.get(self.grade_value)
        if grade_id:
            gr_role = guild.get_role(grade_id)
            if gr_role:
                roles_to_add.append(gr_role)

        try:
            # Retirer le rôle Unverified (ProBot)
            unv_role = guild.get_role(ROLE_UNVERIFIED)
            if unv_role and unv_role in member.roles:
                await member.remove_roles(unv_role)

            if roles_to_add:
                await member.add_roles(*roles_to_add)

            added_names = [r.name for r in roles_to_add]
            print(f"[SUCCESS] Rôles attribués à {member.name} : {added_names}")

            await interaction.response.send_message(
                f"✅ Rôles attribués avec succès à **{member.name}** !\n**Rôles :** {', '.join(added_names)}",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ Erreur : Le bot n'a pas les permissions requises.", ephemeral=True)

class VerifView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GradeSelect())

    @ui.button(label="Ouvrir le formulaire de vérification", style=discord.ButtonStyle.success, custom_id="btn_open_modal_all")
    async def open_modal_button(self, interaction: discord.Interaction, button: ui.Button):
        grade_select_item = None
        for item in self.children:
            if isinstance(item, GradeSelect):
                grade_select_item = item
                break

        if not grade_select_item or not grade_select_item.values:
            await interaction.response.send_message("⚠️ Tu dois d'abord **choisir un Grade** dans le menu déroulant ci-dessus !", ephemeral=True)
            return
        
        selected_grade = grade_select_item.values[0]
        await interaction.response.send_modal(VerifModal(grade_value=selected_grade))

@bot.event
async def on_ready():
    bot.add_view(VerifView())
    synced = await bot.tree.sync()
    print(f"Bot connecté en tant que {bot.user} | {len(synced)} commande(s) synchronisée(s) !")

@bot.tree.command(name="setup_verif", description="Affiche le panneau de vérification complet")
async def setup_verif(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔒 Panneau de Vérification",
        description="1. Sélectionne ton **Grade** dans le menu déroulant.\n2. Clique sur le bouton pour entrer l'**ID du membre** et son **Genre** !",
        color=0x3498db
    )
    await interaction.channel.send(embed=embed, view=VerifView())
    await interaction.response.send_message("Panneau envoyé !", ephemeral=True)

bot.run(TOKEN)