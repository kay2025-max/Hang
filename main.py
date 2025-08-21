import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIG ---
CHANNEL_ID = 1407910664621789234   # kênh gửi panel
CATEGORY_ID = 1407910925922467941  # danh mục chứa ticket
ADMIN_ID = 1407879481217253416     # admin luôn có quyền xem

# --- Questions ---
questions = {
    "help-ticket": {
        "label": "Cần hỗ trợ",
        "emoji": "🆘",
        "placeholder": "Mô tả ngắn vấn đề của bạn",
        "suffix": "help",
    },
    "partner": {
        "label": "Hợp tác",
        "emoji": "🤝",
        "placeholder": "Nội dung hợp tác",
        "suffix": "partner",
    }
}

# --- Button đóng ticket ---
class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🔒 Đóng Ticket", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        # chỉ admin mới được đóng
        if interaction.user.id != ADMIN_ID:
            await interaction.response.send_message("❌ Bạn không có quyền đóng ticket này.", ephemeral=True)
            return

        await interaction.response.send_message("Ticket sẽ đóng sau 5 giây...", ephemeral=True)
        await interaction.channel.send("🔒 Ticket này sẽ bị đóng...")
        await interaction.channel.edit(archived=True) if isinstance(interaction.channel, discord.Thread) else await interaction.channel.delete()


# --- UI Dropdown ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=questions[qid]["label"],
                emoji=questions[qid]["emoji"],
                value=qid,
                description=questions[qid]["placeholder"]
            )
            for qid in questions
        ]
        super().__init__(placeholder="Chọn loại ticket...", options=options)

    async def callback(self, interaction: discord.Interaction):
        qid = self.values[0]
        user = interaction.user
        guild = interaction.guild

        # lấy category
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.get_member(ADMIN_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        # tạo kênh ticket
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}-{questions[qid]['suffix']}",
            category=category,
            overwrites=overwrites
        )
        view = discord.ui.View()
        view.add_item(CloseTicketButton())

        await channel.send(
            f"Xin chào {user.mention}, cảm ơn bạn đã mở ticket **{questions[qid]['label']}**.\nAdmin sẽ sớm phản hồi bạn.",
            view=view
        )
        await interaction.response.send_message(f"Ticket của bạn đã được tạo: {channel.mention}", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None => persistent view
        self.add_item(TicketSelect())

# Thêm hàm này trong Bot
async def setup_hook():
    bot.add_view(TicketView())

bot.setup_hook = setup_hook



@bot.command()
async def sendpanel(ctx):
    embed = discord.Embed(
        title="🎫 Hệ thống hỗ trợ",
        description="Chọn loại ticket bên dưới để liên hệ đội ngũ hỗ trợ.",
        color=discord.Color.blue()
    )
    view = TicketView()
    channel = ctx.guild.get_channel(CHANNEL_ID) or ctx.channel
    await channel.send(embed=embed, view=view)
    await ctx.send("✅ Panel ticket đã được gửi.", delete_after=5)


import os

bot.run(os.getenv("BOT_TOKEN"))


