
import os
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIG ---
CHANNEL_ID = 1407910664621789234   # kênh gửi panel
CATEGORY_ID = 1407910925922467941  # danh mục chứa ticket
ADMIN_IDS = [1406537391577104423, 1396146181939265609, 1407418688902271000]    # danh sách admin có quyền đóng ticket
ADMIN_ROLES = [1407879479485010060, 1407879480558616627]    # danh sách role có quyền đóng ticket

# --- Questions ---
questions = {
    "help-ticket": {
        "label": "🆘 Cần hỗ trợ",
        "emoji": "🆘",
        "placeholder": "Mô tả ngắn vấn đề của bạn",
        "suffix": "help",
        "description": "Cần hỗ trợ kỹ thuật hoặc giải đáp thắc mắc"
    },
    "partner": {
        "label": "🤝 Hợp tác",
        "emoji": "🤝",
        "placeholder": "Nội dung hợp tác",
        "suffix": "partner",
        "description": "Đề xuất hợp tác kinh doanh"
    },
    "report": {
        "label": "⚠️ Báo cáo",
        "emoji": "⚠️",
        "placeholder": "Nội dung báo cáo",
        "suffix": "report",
        "description": "Báo cáo vi phạm hoặc vấn đề"
    },
    "suggestion": {
        "label": "💡 Góp ý",
        "emoji": "💡",
        "placeholder": "Ý kiến đóng góp",
        "suffix": "suggestion",
        "description": "Đóng góp ý kiến cải thiện"
    }
}

# --- Ticket Management Buttons ---
class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Đóng Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            has_admin_permission = (
                interaction.user.id in ADMIN_IDS or 
                any(role.id in ADMIN_ROLES for role in interaction.user.roles)
            )

            if not has_admin_permission:
                embed = discord.Embed(
                    title="❌ Không có quyền",
                    description="Bạn không có quyền đóng ticket này.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            embed = discord.Embed(
                title="🔒 Đóng Ticket",
                description="Ticket sẽ được đóng sau 5 giây...",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            
            close_embed = discord.Embed(
                title="🔒 Ticket Đã Đóng",
                description=f"Ticket này đã được đóng bởi {interaction.user.mention}",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await interaction.channel.send(embed=close_embed)
            
            await asyncio.sleep(5)
            await interaction.channel.delete()

        except Exception as e:
            print(f"[ERROR] CloseTicket: {e}")
            if not interaction.response.is_done():
                error_embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Có lỗi khi đóng ticket.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @discord.ui.button(label="✏️ Đổi tên", style=discord.ButtonStyle.secondary, custom_id="rename_ticket")
    async def rename_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            has_admin_permission = (
                interaction.user.id in ADMIN_IDS or 
                any(role.id in ADMIN_ROLES for role in interaction.user.roles)
            )

            if not has_admin_permission:
                embed = discord.Embed(
                    title="❌ Không có quyền",
                    description="Bạn không có quyền đổi tên ticket này.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            modal = RenameTicketModal()
            await interaction.response.send_modal(modal)

        except Exception as e:
            print(f"[ERROR] RenameTicket: {e}")

    @discord.ui.button(label="➕ Thêm người", style=discord.ButtonStyle.success, custom_id="add_user")
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            has_admin_permission = (
                interaction.user.id in ADMIN_IDS or 
                any(role.id in ADMIN_ROLES for role in interaction.user.roles)
            )

            if not has_admin_permission:
                embed = discord.Embed(
                    title="❌ Không có quyền",
                    description="Bạn không có quyền thêm người vào ticket này.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            modal = AddUserModal()
            await interaction.response.send_modal(modal)

        except Exception as e:
            print(f"[ERROR] AddUser: {e}")

# --- Modal for renaming ticket ---
class RenameTicketModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="✏️ Đổi tên Ticket")

    new_name = discord.ui.TextInput(
        label="Tên mới cho ticket",
        placeholder="Nhập tên mới...",
        max_length=50,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_channel_name = self.new_name.value.lower().replace(" ", "-")
            new_channel_name = "".join(c for c in new_channel_name if c.isalnum() or c == "-")
            
            await interaction.channel.edit(name=new_channel_name)
            
            embed = discord.Embed(
                title="✅ Đổi tên thành công",
                description=f"Ticket đã được đổi tên thành: **{new_channel_name}**",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Đổi tên bởi {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"[ERROR] RenameModal: {e}")
            error_embed = discord.Embed(
                title="❌ Lỗi",
                description="Không thể đổi tên ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

# --- Modal for adding user ---
class AddUserModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="➕ Thêm người vào Ticket")

    user_input = discord.ui.TextInput(
        label="User ID hoặc @mention",
        placeholder="Nhập ID hoặc @mention người dùng...",
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_text = self.user_input.value.strip()
            
            # Tìm user bằng mention hoặc ID
            user = None
            if user_text.startswith("<@") and user_text.endswith(">"):
                user_id = user_text[2:-1]
                if user_id.startswith("!"):
                    user_id = user_id[1:]
                user = interaction.guild.get_member(int(user_id))
            else:
                try:
                    user = interaction.guild.get_member(int(user_text))
                except ValueError:
                    pass

            if not user:
                embed = discord.Embed(
                    title="❌ Không tìm thấy",
                    description="Không tìm thấy người dùng. Vui lòng kiểm tra lại ID hoặc mention.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Thêm quyền cho user
            await interaction.channel.set_permissions(
                user, 
                view_channel=True, 
                send_messages=True, 
                read_message_history=True
            )

            embed = discord.Embed(
                title="✅ Thêm thành công",
                description=f"{user.mention} đã được thêm vào ticket này.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Thêm bởi {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(f"[ERROR] AddUserModal: {e}")
            error_embed = discord.Embed(
                title="❌ Lỗi",
                description="Không thể thêm người dùng vào ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

# --- UI Dropdown ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=questions[qid]["label"],
                emoji=questions[qid]["emoji"],
                value=qid,
                description=questions[qid]["description"]
            )
            for qid in questions
        ]
        super().__init__(
            placeholder="🎯 Chọn loại hỗ trợ bạn cần...",
            options=options,
            custom_id="ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            qid = self.values[0]
            user = interaction.user
            guild = interaction.guild
            category = discord.utils.get(guild.categories, id=CATEGORY_ID)

            # Kiểm tra xem user đã có ticket chưa
            existing_tickets = [ch for ch in category.channels if f"ticket-{user.name}" in ch.name.lower()]
            if len(existing_tickets) >= 3:  # Giới hạn 3 ticket/user
                embed = discord.Embed(
                    title="⚠️ Giới hạn ticket",
                    description="Bạn đã có quá nhiều ticket đang mở. Vui lòng đóng ticket cũ trước khi tạo mới.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            }

            # Thêm quyền cho admin users
            for admin_id in ADMIN_IDS:
                admin_member = guild.get_member(admin_id)
                if admin_member:
                    overwrites[admin_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

            # Thêm quyền cho admin roles
            for role_id in ADMIN_ROLES:
                admin_role = guild.get_role(role_id)
                if admin_role:
                    overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

            # Tạo kênh ticket
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}-{questions[qid]['suffix']}",
                category=category,
                overwrites=overwrites
            )

            # Embed chào mừng
            welcome_embed = discord.Embed(
                title=f"🎫 {questions[qid]['label']}",
                description=f"Xin chào {user.mention}!\n\nCảm ơn bạn đã mở ticket **{questions[qid]['label']}**.\n\n📋 **Hướng dẫn:**\n• Mô tả chi tiết vấn đề của bạn\n• Admin sẽ phản hồi trong thời gian sớm nhất\n• Sử dụng các nút bên dưới để quản lý ticket",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            welcome_embed.set_thumbnail(url=user.display_avatar.url)
            welcome_embed.set_footer(text=f"Ticket ID: {channel.id}")

            view = TicketManagementView()
            await channel.send(embed=welcome_embed, view=view)

            # Phản hồi cho user
            success_embed = discord.Embed(
                title="✅ Ticket đã được tạo",
                description=f"Ticket của bạn đã được tạo thành công!\n\n🔗 **Kênh:** {channel.mention}\n📋 **Loại:** {questions[qid]['label']}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)

        except Exception as e:
            import traceback
            print("[ERROR] TicketSelect:", e)
            traceback.print_exc()
            if not interaction.response.is_done():
                error_embed = discord.Embed(
                    title="❌ Lỗi hệ thống",
                    description="Có lỗi khi tạo ticket. Vui lòng liên hệ admin.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)

# --- Ticket Panel View ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# --- setup_hook ---
@bot.event
async def setup_hook():
    bot.add_view(TicketView())
    bot.add_view(TicketManagementView())

@bot.event
async def on_ready():
    print(f"🤖 Bot {bot.user} đã sẵn sàng!")
    print(f"📊 Đang hoạt động trên {len(bot.guilds)} server(s)")

# --- Commands ---
@bot.command(name="sendpanel", aliases=["panel"])
@commands.has_permissions(administrator=True)
async def sendpanel(ctx):
    """Gửi panel ticket với giao diện đẹp"""
    embed = discord.Embed(
        title="🎫 Hệ thống hỗ trợ",
        description="**Chào mừng đến với hệ thống hỗ trợ!**\n\n📋 **Hướng dẫn sử dụng:**\n• Chọn loại hỗ trợ phù hợp từ menu bên dưới\n• Một kênh riêng sẽ được tạo để bạn trao đổi với admin\n• Mô tả chi tiết vấn đề để được hỗ trợ nhanh nhất\n\n⚡ **Thời gian phản hồi:** Dưới 24 giờ\n🔒 **Bảo mật:** Chỉ bạn và admin có thể xem nội dung",
        color=0x00ff9f
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text="💡 Chọn loại hỗ trợ bên dưới để bắt đầu", icon_url=bot.user.display_avatar.url)
    
    view = TicketView()
    channel = ctx.guild.get_channel(CHANNEL_ID) or ctx.channel
    await channel.send(embed=embed, view=view)
    
    success_embed = discord.Embed(
        title="✅ Thành công",
        description="Panel ticket đã được gửi thành công!",
        color=discord.Color.green()
    )
    await ctx.send(embed=success_embed, delete_after=5)

@bot.command(name="closeticket", aliases=["close"])
async def close_ticket_command(ctx):
    """Đóng ticket hiện tại"""
    if not ctx.channel.name.startswith("ticket-"):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này chỉ có thể sử dụng trong kênh ticket.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    has_admin_permission = (
        ctx.author.id in ADMIN_IDS or 
        any(role.id in ADMIN_ROLES for role in ctx.author.roles)
    )

    if not has_admin_permission:
        embed = discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền đóng ticket này.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="🔒 Đóng Ticket",
        description="Ticket sẽ được đóng sau 5 giây...",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    
    await asyncio.sleep(5)
    await ctx.channel.delete()

@bot.command(name="adduser", aliases=["add"])
async def add_user_command(ctx, user: discord.Member = None):
    """Thêm người dùng vào ticket"""
    if not ctx.channel.name.startswith("ticket-"):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này chỉ có thể sử dụng trong kênh ticket.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    has_admin_permission = (
        ctx.author.id in ADMIN_IDS or 
        any(role.id in ADMIN_ROLES for role in ctx.author.roles)
    )

    if not has_admin_permission:
        embed = discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền thêm người vào ticket này.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if not user:
        embed = discord.Embed(
            title="❌ Thiếu thông tin",
            description="Vui lòng mention người dùng cần thêm.\n**Cách dùng:** `!adduser @user`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    await ctx.channel.set_permissions(
        user, 
        view_channel=True, 
        send_messages=True, 
        read_message_history=True
    )

    embed = discord.Embed(
        title="✅ Thêm thành công",
        description=f"{user.mention} đã được thêm vào ticket này.",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Thêm bởi {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def ticket_stats(ctx):
    """Thống kê ticket"""
    category = discord.utils.get(ctx.guild.categories, id=CATEGORY_ID)
    if not category:
        await ctx.send("❌ Không tìm thấy danh mục ticket.")
        return

    total_tickets = len([ch for ch in category.channels if ch.name.startswith("ticket-")])
    
    embed = discord.Embed(
        title="📊 Thống kê Ticket",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="🎫 Tổng ticket đang mở", value=total_tickets, inline=True)
    embed.add_field(name="📁 Danh mục", value=category.name, inline=True)
    embed.add_field(name="👥 Admin", value=len(ADMIN_IDS), inline=True)
    
    await ctx.send(embed=embed)

# Error handlers
@sendpanel.error
async def sendpanel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Không có quyền",
            description="Bạn cần có quyền Administrator để sử dụng lệnh này.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# --- Run bot ---
bot.run(os.getenv("BOT_TOKEN"))
