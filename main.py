
import os
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

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
    # Main embed với gradient effect
    main_embed = discord.Embed(
        title="",
        description="",
        color=0x7289da
    )
    
    # Header với ASCII art
    header_text = """
```
╔══════════════════════════════════════╗
║          🎫 HỆ THỐNG HỖ TRỢ           ║
║        CHUYÊN NGHIỆP & NHANH CHÓNG    ║
╚══════════════════════════════════════╝
```
"""
    
    # Main content với styling đẹp
    main_content = """
**🌟 CHÀO MỪNG ĐẾN VỚI HỆ THỐNG HỖ TRỢ CHUYÊN NGHIỆP!**

┌─────────────────────────────────────┐
│ 📋 **HƯỚNG DẪN SỬ DỤNG**            │
├─────────────────────────────────────┤
│ ▸ Chọn loại hỗ trợ từ menu bên dưới  │
│ ▸ Kênh riêng sẽ được tạo tự động     │
│ ▸ Mô tả chi tiết để được hỗ trợ tốt  │
│ ▸ Admin sẽ phản hồi trong 24h        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎯 **CÁC LOẠI HỖ TRỢ**              │
├─────────────────────────────────────┤
│ 🆘 **Hỗ trợ kỹ thuật** - Giải đáp    │
│ 🤝 **Hợp tác kinh doanh** - Đối tác  │
│ ⚠️ **Báo cáo vi phạm** - An toàn     │
│ 💡 **Góp ý cải thiện** - Phát triển  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ⚡ **THÔNG TIN QUAN TRỌNG**          │
├─────────────────────────────────────┤
│ 🕐 Thời gian phản hồi: < 24 giờ     │
│ 🔒 Bảo mật: Chỉ bạn và admin xem    │
│ 📊 Hệ thống: 24/7 hoạt động         │
│ 🎫 Giới hạn: 3 ticket/người dùng    │
└─────────────────────────────────────┘
"""
    
    main_embed.description = header_text + main_content
    
    # Thêm fields đẹp
    main_embed.add_field(
        name="🏆 Chất lượng dịch vụ",
        value="```fix\n✓ Hỗ trợ chuyên nghiệp\n✓ Phản hồi nhanh chóng\n✓ Giải pháp hiệu quả```",
        inline=True
    )
    
    main_embed.add_field(
        name="📞 Liên hệ khẩn cấp",
        value="```css\nDM trực tiếp Admin\nnếu có vấn đề khẩn cấp```",
        inline=True
    )
    
    main_embed.add_field(
        name="🎉 Cam kết",
        value="```yaml\n- Hỗ trợ tận tâm\n- Giải quyết triệt để\n- Bảo mật thông tin```",
        inline=True
    )
    
    # Set thumbnail và footer
    if ctx.guild.icon:
        main_embed.set_thumbnail(url=ctx.guild.icon.url)
    
    main_embed.set_image(url="https://via.placeholder.com/800x200/7289da/ffffff?text=TICKET+SUPPORT+SYSTEM")
    
    main_embed.set_footer(
        text="💎 Chọn loại hỗ trợ từ menu bên dưới để bắt đầu • Powered by Discord Bot",
        icon_url=bot.user.display_avatar.url
    )
    
    main_embed.timestamp = discord.utils.utcnow()
    
    # Tạo embed thống kê
    category = discord.utils.get(ctx.guild.categories, id=CATEGORY_ID)
    total_tickets = len([ch for ch in category.channels if ch.name.startswith("ticket-")]) if category else 0
    
    stats_embed = discord.Embed(
        title="📊 THỐNG KÊ HỆ THỐNG",
        color=0x00ff9f
    )
    
    stats_embed.add_field(
        name="🎫 Ticket đang mở",
        value=f"```fix\n{total_tickets} tickets```",
        inline=True
    )
    
    stats_embed.add_field(
        name="👥 Admin trực tuyến",
        value=f"```css\n{len(ADMIN_IDS)} admins```",
        inline=True
    )
    
    stats_embed.add_field(
        name="⚡ Trạng thái",
        value="```diff\n+ HOẠT ĐỘNG```",
        inline=True
    )
    
    # Gửi panel
    view = TicketView()
    channel = ctx.guild.get_channel(CHANNEL_ID) or ctx.channel
    
    await channel.send(embeds=[main_embed, stats_embed], view=view)
    
    # Success message với animation
    success_embed = discord.Embed(
        title="✅ PANEL ĐÃ ĐƯỢC GỬI THÀNH CÔNG!",
        description="```css\n🎉 Hệ thống ticket đã sẵn sàng hoạt động!\n📍 Vị trí: " + channel.mention + "\n⏰ Thời gian: " + discord.utils.format_dt(discord.utils.utcnow(), 'F') + "```",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    success_embed.set_footer(text="Bot by Admin • Ticket System v2.0")
    
    await ctx.send(embed=success_embed, delete_after=10)

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

@bot.command(name="help", aliases=["h", "giupdo", "trogiup"])
async def help_command(ctx, category: str = None):
    """Lệnh help chất lượng với giao diện đẹp"""
    
    if category is None:
        # Main help embed
        main_embed = discord.Embed(
            title="",
            description="",
            color=0x5865f2
        )
        
        # Header đẹp
        header_text = """
```ansi
[2;32m╔══════════════════════════════════════════╗[0m
[2;32m║[0m[2;36m            🤖 HƯỚNG DẪN SỬ DỤNG BOT          [0m[2;32m║[0m
[2;32m║[0m[2;35m           TICKET SYSTEM V2.0             [0m[2;32m║[0m
[2;32m╚══════════════════════════════════════════╝[0m
```
"""
        
        main_content = """
**🎯 DANH SÁCH LỆNH CƠ BẢN**

┌────────────────────────────────────────┐
│ **📋 LỆNH CHO NGƯỜI DÙNG**             │
├────────────────────────────────────────┤
│ `!help [category]` - Xem hướng dẫn     │
│ `!help user` - Lệnh người dùng         │
│ `!help admin` - Lệnh admin             │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ **🎫 HỆ THỐNG TICKET**                 │
├────────────────────────────────────────┤
│ • Sử dụng panel để tạo ticket          │
│ • Chọn loại hỗ trợ phù hợp             │
│ • Mô tả chi tiết vấn đề                │
│ • Chờ admin phản hồi                   │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ **⚡ TÍNH NĂNG NỔI BẬT**               │
├────────────────────────────────────────┤
│ 🔒 Bảo mật cao - Chỉ admin và bạn xem  │
│ 🚀 Tạo ticket tự động trong 2 giây     │
│ 📊 Thống kê chi tiết                   │
│ 🎨 Giao diện đẹp, dễ sử dụng           │
└────────────────────────────────────────┘
"""
        
        main_embed.description = header_text + main_content
        
        # Thêm các field hướng dẫn
        main_embed.add_field(
            name="📚 Các loại help",
            value="```css\n!help user   - Lệnh người dùng\n!help admin  - Lệnh quản trị\n!help ticket - Về hệ thống ticket```",
            inline=True
        )
        
        main_embed.add_field(
            name="🆘 Hỗ trợ khẩn cấp",
            value="```fix\nDM trực tiếp Admin\nhoặc tạo ticket báo cáo```",
            inline=True
        )
        
        main_embed.add_field(
            name="🔗 Links hữu ích",
            value="```yaml\nServer: discord.gg/yourserver\nGithub: github.com/yourbot\nWebsite: yoursite.com```",
            inline=True
        )
        
        main_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else bot.user.display_avatar.url)
        main_embed.set_footer(
            text="💡 Sử dụng !help [category] để xem chi tiết • Bot by Admin",
            icon_url=bot.user.display_avatar.url
        )
        main_embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=main_embed)
    
    elif category.lower() in ["user", "nguoidung", "u"]:
        # User commands help
        user_embed = discord.Embed(
            title="👤 LỆNH CHO NGƯỜI DÙNG",
            color=0x00ff9f,
            timestamp=discord.utils.utcnow()
        )
        
        user_embed.description = """
```ansi
[2;34m╭─────────────────────────────────────────╮[0m
[2;34m│[0m[2;33m          🎫 HỆ THỐNG TICKET             [0m[2;34m│[0m
[2;34m╰─────────────────────────────────────────╯[0m
```

**📋 CÁCH TẠO TICKET:**
• Tìm kênh có panel ticket
• Chọn loại hỗ trợ từ dropdown menu
• Kênh riêng sẽ được tạo tự động
• Mô tả vấn đề chi tiết để được hỗ trợ tốt nhất

**🎯 CÁC LOẠI HỖ TRỢ:**
🆘 **Hỗ trợ kỹ thuật** - Giải đáp thắc mắc
🤝 **Hợp tác kinh doanh** - Đề xuất đối tác  
⚠️ **Báo cáo vi phạm** - Báo cáo vi phạm
💡 **Góp ý cải thiện** - Ý kiến phát triển
"""
        
        user_embed.add_field(
            name="⏰ Thời gian phản hồi",
            value="```fix\n< 24 giờ```",
            inline=True
        )
        
        user_embed.add_field(
            name="🎫 Giới hạn ticket",
            value="```yaml\n3 tickets/người```",
            inline=True
        )
        
        user_embed.add_field(
            name="🔒 Bảo mật",
            value="```css\nChỉ bạn & admin xem```",
            inline=True
        )
        
        user_embed.set_footer(text="💡 Tip: Mô tả chi tiết giúp admin hỗ trợ nhanh hơn")
        
        await ctx.send(embed=user_embed)
    
    elif category.lower() in ["admin", "a", "quanly"]:
        # Admin commands help
        if not (ctx.author.id in ADMIN_IDS or any(role.id in ADMIN_ROLES for role in ctx.author.roles)):
            error_embed = discord.Embed(
                title="❌ Không có quyền",
                description="Bạn không có quyền xem lệnh admin.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
            return
            
        admin_embed = discord.Embed(
            title="👑 LỆNH DÀNH CHO ADMIN",
            color=0xff6b6b,
            timestamp=discord.utils.utcnow()
        )
        
        admin_embed.description = """
```ansi
[2;31m╭─────────────────────────────────────────╮[0m
[2;31m│[0m[2;33m         🛠️ CÔNG CỤ QUẢN TRỊ             [0m[2;31m│[0m
[2;31m╰─────────────────────────────────────────╯[0m
```

**🎛️ LỆNH CHÍNH:**
"""
        
        commands_list = [
            ("📤 `!sendpanel`", "Gửi panel ticket mới"),
            ("🔒 `!closeticket`", "Đóng ticket hiện tại"),  
            ("➕ `!adduser @user`", "Thêm người vào ticket"),
            ("📊 `!stats`", "Xem thống kê hệ thống"),
            ("❓ `!help admin`", "Xem lệnh admin")
        ]
        
        for i, (cmd, desc) in enumerate(commands_list):
            admin_embed.add_field(
                name=cmd,
                value=f"```{desc}```",
                inline=False
            )
        
        admin_embed.add_field(
            name="🎫 Quản lý ticket trong kênh",
            value="```yaml\n- Nút 🔒 Đóng Ticket\n- Nút ✏️ Đổi tên\n- Nút ➕ Thêm người```",
            inline=False
        )
        
        admin_embed.set_footer(text="⚠️ Chỉ admin có quyền sử dụng các lệnh này")
        
        await ctx.send(embed=admin_embed)
    
    elif category.lower() in ["ticket", "t"]:
        # Ticket system detailed help
        ticket_embed = discord.Embed(
            title="🎫 HỆ THỐNG TICKET CHI TIẾT",
            color=0x9b59b6,
            timestamp=discord.utils.utcnow()
        )
        
        ticket_embed.description = """
```ansi
[2;35m╭─────────────────────────────────────────╮[0m
[2;35m│[0m[2;36m        📋 HƯỚNG DẪN CHI TIẾT            [0m[2;35m│[0m
[2;35m╰─────────────────────────────────────────╯[0m
```

**🚀 QUY TRÌNH TẠO TICKET:**

**Bước 1:** Tìm panel ticket trong server
**Bước 2:** Click vào dropdown menu bên dưới  
**Bước 3:** Chọn loại hỗ trợ phù hợp
**Bước 4:** Kênh riêng được tạo tự động
**Bước 5:** Mô tả chi tiết vấn đề của bạn
**Bước 6:** Chờ admin phản hồi (< 24h)

**🎯 MẸO VIẾT TICKET TỐT:**
• Tiêu đề ngắn gọn, rõ ràng
• Mô tả chi tiết từng bước
• Đính kèm ảnh/video nếu cần
• Ghi rõ thời gian xảy ra sự cố
"""
        
        ticket_embed.add_field(
            name="✅ Ticket tốt",
            value="```fix\n+ Mô tả chi tiết\n+ Có ảnh minh họa\n+ Thời gian cụ thể\n+ Các bước đã thử```",
            inline=True
        )
        
        ticket_embed.add_field(
            name="❌ Ticket kém",
            value="```diff\n- Chỉ viết 'help'\n- Không rõ ràng\n- Thiếu thông tin\n- Không lịch sự```",
            inline=True
        )
        
        ticket_embed.add_field(
            name="📏 Quy tắc",
            value="```yaml\n- Tối đa 3 ticket/người\n- Không spam\n- Lịch sự với admin\n- Đóng ticket khi xong```",
            inline=False
        )
        
        await ctx.send(embed=ticket_embed)
    
    else:
        # Invalid category
        error_embed = discord.Embed(
            title="❌ Danh mục không hợp lệ",
            description="**Các danh mục có sẵn:**\n• `user` - Lệnh người dùng\n• `admin` - Lệnh quản trị\n• `ticket` - Hệ thống ticket\n\n**Cách dùng:** `!help [category]`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=error_embed)

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
