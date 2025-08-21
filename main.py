import os
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
        super().__init__(
            label="🔒 Đóng Ticket",
            style=discord.ButtonStyle.danger,
            custom_id="close_ticket"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != ADMIN_ID:
                await interaction.response.send_message(
                    "❌ Bạn không có quyền đóng ticket này.", ephemeral=True
                )
                return

            await interaction.response.send_message("Ticket sẽ đóng sau 5 giây...", ephemeral=True)
            await interaction.channel.send("🔒 Ticket này sẽ bị đóng...")
            await interaction.channel.delete()

        except Exception as e:
            print(f"[ERROR] CloseTicketButton: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Có lỗi khi đóng ticket.", ephemeral=True
                )

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
        super().__init__(
            placeholder="Chọn loại ticket...",
            options=options,
            custom_id="ticket_select"  # BẮT BUỘC: custom_id cố định
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            qid = self.values[0]
            user = interaction.user
            guild = interaction.guild
            category = discord.utils.get(guild.categories, id=CATEGORY_ID)

            print(f"[DEBUG] User chọn: {qid}")
            print(f"[DEBUG] Guild: {guild} (ID: {guild.id})")
            print(f"[DEBUG] Category: {category}")
            print(f"[DEBUG] Admin member: {guild.get_member(ADMIN_ID)}")

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

            view = discord.ui.View(timeout=None)
            view.add_item(CloseTicketButton())

            await channel.send(
                f"Xin chào {user.mention}, cảm ơn bạn đã mở ticket **{questions[qid]['label']}**.\nAdmin sẽ sớm phản hồi bạn.",
                view=view
            )
            await interaction.response.send_message(
                f"✅ Ticket của bạn đã được tạo: {channel.mention}", ephemeral=True
            )

        except Exception as e:
            import traceback
            print("[ERROR] TicketSelect:", e)
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Có lỗi khi tạo ticket liên hệ admin.", ephemeral=True
                )


            # tạo kênh ticket
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}-{questions[qid]['suffix']}",
                category=category,
                overwrites=overwrites
            )

            view = discord.ui.View(timeout=None)
            view.add_item(CloseTicketButton())

            await channel.send(
                f"Xin chào {user.mention}, cảm ơn bạn đã mở ticket **{questions[qid]['label']}**.\nAdmin sẽ sớm phản hồi bạn.",
                view=view
            )
            await interaction.response.send_message(
                f"✅ Ticket của bạn đã được tạo: {channel.mention}", ephemeral=True
            )

        except Exception as e:
            import traceback
            print("[ERROR] TicketSelect:", e)
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Có lỗi khi tạo ticket.", ephemeral=True
                )

            # tạo kênh ticket
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}-{questions[qid]['suffix']}",
                category=category,
                overwrites=overwrites
            )
            view = discord.ui.View(timeout=None)
            view.add_item(CloseTicketButton())

            await channel.send(
                f"Xin chào {user.mention}, cảm ơn bạn đã mở ticket **{questions[qid]['label']}**.\nAdmin sẽ sớm phản hồi bạn.",
                view=view
            )
            await interaction.response.send_message(
                f"✅ Ticket của bạn đã được tạo: {channel.mention}", ephemeral=True
            )

        except Exception as e:
            print(f"[ERROR] TicketSelect: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Có lỗi khi tạo ticket.", ephemeral=True
                )

# --- Ticket Panel View ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- setup_hook để giữ view persistent ---
@bot.event
async def setup_hook():
    bot.add_view(TicketView())  # đăng ký view để không mất khi restart

# --- Command gửi panel ---
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

# --- Run bot ---
bot.run(os.getenv("BOT_TOKEN"))
