import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional

# These commands will be added to the main bot file

# Level Role Configuration Commands for Admins

@commands.hybrid_command(name='level-role-set', aliases=['set-level-role'])
@app_commands.describe(
    level="Level number (must be multiple of 5, from 5 to 100)",
    role="The role to assign at this level",
    description="Optional description for this level role"
)
@commands.has_permissions(administrator=True)
async def set_level_role(ctx: commands.Context, level: int, role: discord.Role, *, description: str = None):
    """Set a role reward for a specific level (Admin only)"""
    
    # Import here to avoid circular imports
    from progressive_leveling import progressive_leveling
    
    # Validate level
    if not progressive_leveling.is_role_level(level):
        embed = discord.Embed(
            title="❌ Invalid Level",
            description=f"Level must be a multiple of 5 between 5 and 100.\n\n"
                       f"**Valid levels:** 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Check if role is manageable by bot
    if role.position >= ctx.guild.me.top_role.position:
        embed = discord.Embed(
            title="❌ Role Position Error",
            description=f"I cannot manage the role **{role.name}** because it's higher than or equal to my highest role.\n\n"
                       f"Please move my role above **{role.name}** in the server settings.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Set the role configuration
    success = await progressive_leveling.set_level_role_config(
        str(ctx.guild.id), 
        level, 
        str(role.id), 
        role.name,
        description
    )
    
    if success:
        embed = discord.Embed(
            title="✅ Level Role Configured",
            description=f"Successfully configured role reward for **Level {level}**",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🎯 Level", 
            value=f"**{level}**", 
            inline=True
        )
        embed.add_field(
            name="🏷️ Role", 
            value=f"{role.mention}\n`{role.name}`", 
            inline=True
        )
        embed.add_field(
            name="📝 Description", 
            value=description or f"Level {level} Role", 
            inline=False
        )
        embed.add_field(
            name="📊 XP Required",
            value=f"**{progressive_leveling.calculate_total_xp_for_level(level):,}** total XP",
            inline=True
        )
        embed.set_footer(text=f"Configured by {ctx.author.display_name}")
        
    else:
        embed = discord.Embed(
            title="❌ Configuration Failed",
            description="Failed to configure the level role. Please try again.",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='level-role-remove', aliases=['remove-level-role'])
@app_commands.describe(level="Level number to remove role from")
@commands.has_permissions(administrator=True)
async def remove_level_role(ctx: commands.Context, level: int):
    """Remove a role reward from a specific level (Admin only)"""
    
    from progressive_leveling import progressive_leveling
    
    # Check if role exists for this level
    role_config = await progressive_leveling.get_level_role_config(str(ctx.guild.id), level)
    if not role_config:
        embed = discord.Embed(
            title="❌ No Role Configured",
            description=f"No role is configured for Level {level}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Remove the role configuration
    success = await progressive_leveling.remove_level_role_config(str(ctx.guild.id), level)
    
    if success:
        embed = discord.Embed(
            title="✅ Level Role Removed",
            description=f"Successfully removed role configuration for **Level {level}**",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🏷️ Removed Role", 
            value=f"`{role_config['role_name']}`", 
            inline=True
        )
        embed.add_field(
            name="🎯 Level", 
            value=f"**{level}**", 
            inline=True
        )
    else:
        embed = discord.Embed(
            title="❌ Removal Failed",
            description="Failed to remove the level role configuration.",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='level-roles-list', aliases=['list-level-roles', 'level-roles'])
@app_commands.describe()
async def list_level_roles(ctx: commands.Context):
    """List all configured level roles for this server"""
    
    from progressive_leveling import progressive_leveling
    
    configured_roles = await progressive_leveling.get_all_configured_roles(str(ctx.guild.id))
    
    if not configured_roles:
        embed = discord.Embed(
            title="📋 Level Roles",
            description="No level roles have been configured yet.\n\n"
                       "Use `/level-role-set` to configure roles for specific levels.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="💡 Available Levels",
            value="5, 10, 15, 20, 25, 30, 35, 40, 45, 50\n55, 60, 65, 70, 75, 80, 85, 90, 95, 100",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Sort by level
    sorted_roles = sorted(configured_roles.items())
    
    embed = discord.Embed(
        title="📋 Configured Level Roles",
        description=f"**{len(configured_roles)}** level roles configured",
        color=discord.Color.blue()
    )
    
    # Add fields for each configured role
    for level, role_data in sorted_roles:
        role = ctx.guild.get_role(int(role_data['role_id']))
        role_display = role.mention if role else f"`{role_data['role_name']}` (Deleted)"
        
        xp_needed = progressive_leveling.calculate_total_xp_for_level(level)
        
        embed.add_field(
            name=f"🎯 Level {level}",
            value=f"{role_display}\n"
                  f"📊 **{xp_needed:,}** XP\n"
                  f"📝 {role_data.get('description', 'No description')}",
            inline=True
        )
    
    # Add pagination if too many roles
    if len(configured_roles) > 25:  # Discord embed field limit
        embed.set_footer(text="Some roles may not be displayed due to Discord limits")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='level-role-info', aliases=['level-role-check'])
@app_commands.describe(level="Level number to check")
async def level_role_info(ctx: commands.Context, level: int):
    """Get information about a specific level role"""
    
    from progressive_leveling import progressive_leveling
    
    # Check if level is valid
    if not progressive_leveling.is_role_level(level):
        embed = discord.Embed(
            title="❌ Invalid Level",
            description=f"Level {level} is not a valid role level.\n\n"
                       f"Roles are available every 5 levels: 5, 10, 15, 20, etc.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    role_config = await progressive_leveling.get_level_role_config(str(ctx.guild.id), level)
    xp_needed = progressive_leveling.calculate_total_xp_for_level(level)
    
    if role_config:
        role = ctx.guild.get_role(int(role_config['role_id']))
        role_display = role.mention if role else f"`{role_config['role_name']}` (Deleted)"
        
        embed = discord.Embed(
            title=f"🎯 Level {level} Role Information",
            description="Here's the configured role for this level:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🏷️ Role",
            value=role_display,
            inline=True
        )
        embed.add_field(
            name="📊 XP Required",
            value=f"**{xp_needed:,}** total XP",
            inline=True
        )
        embed.add_field(
            name="📝 Description",
            value=role_config.get('description', 'No description'),
            inline=False
        )
        
        if role:
            embed.add_field(
                name="👥 Members with Role",
                value=f"**{len(role.members)}** members",
                inline=True
            )
            embed.add_field(
                name="🎨 Role Color",
                value=f"`{role.color}`",
                inline=True
            )
        
        embed.set_footer(text=f"Configured on {role_config.get('created_at', 'Unknown date')}")
        
    else:
        embed = discord.Embed(
            title=f"📭 Level {level} - No Role Configured",
            description="This level doesn't have a role reward configured yet.",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="📊 XP Required",
            value=f"**{xp_needed:,}** total XP",
            inline=True
        )
        embed.add_field(
            name="⚙️ Configure Role",
            value=f"Use `/level-role-set {level} @role` to set up a role reward",
            inline=False
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='xp-calculator', aliases=['xp-calc'])
@app_commands.describe(level="Target level to calculate XP for (1-100)")
async def xp_calculator(ctx: commands.Context, level: int):
    """Calculate XP requirements for any level (1-100)"""
    
    from progressive_leveling import progressive_leveling
    
    if level < 1 or level > progressive_leveling.max_level:
        embed = discord.Embed(
            title="❌ Invalid Level",
            description=f"Level must be between 1 and {progressive_leveling.max_level}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if level == 1:
        embed = discord.Embed(
            title="🎯 Level 1 XP Information",
            description="Level 1 is the starting level and requires no XP.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📊 Total XP",
            value="**0** XP",
            inline=True
        )
        embed.add_field(
            name="⬆️ Next Level",
            value=f"**{progressive_leveling.calculate_xp_needed(2)}** XP needed for Level 2",
            inline=True
        )
        await ctx.send(embed=embed)
        return
    
    total_xp = progressive_leveling.calculate_total_xp_for_level(level)
    xp_for_this_level = progressive_leveling.calculate_xp_needed(level)
    
    embed = discord.Embed(
        title=f"🎯 Level {level} XP Calculator",
        description=f"XP requirements for reaching Level {level}",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 Total XP Required",
        value=f"**{total_xp:,}** XP",
        inline=True
    )
    embed.add_field(
        name="⬆️ XP for This Level",
        value=f"**{xp_for_this_level:,}** XP",
        inline=True
    )
    
    # Show next level info if not at max
    if level < progressive_leveling.max_level:
        next_level_xp = progressive_leveling.calculate_xp_needed(level + 1)
        embed.add_field(
            name="➡️ XP for Next Level",
            value=f"**{next_level_xp:,}** XP needed for Level {level + 1}",
            inline=False
        )
    
    # Show if this level has a role
    if progressive_leveling.is_role_level(level):
        role_config = await progressive_leveling.get_level_role_config(str(ctx.guild.id), level)
        if role_config:
            role = ctx.guild.get_role(int(role_config['role_id']))
            role_display = role.mention if role else f"`{role_config['role_name']}`"
            embed.add_field(
                name="🏷️ Role Reward",
                value=role_display,
                inline=True
            )
        else:
            embed.add_field(
                name="🏷️ Role Reward",
                value="Not configured",
                inline=True
            )
    
    # Add some milestone information
    milestones = []
    for milestone in [10, 25, 50, 75, 100]:
        if level <= milestone:
            milestone_xp = progressive_leveling.calculate_total_xp_for_level(milestone)
            milestones.append(f"Level {milestone}: **{milestone_xp:,}** XP")
            if len(milestones) >= 3:
                break
    
    if milestones:
        embed.add_field(
            name="🎯 Upcoming Milestones",
            value="\n".join(milestones),
            inline=False
        )
    
    await ctx.send(embed=embed)

# Error handlers for the commands

@set_level_role.error
async def set_level_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You need **Administrator** permission to configure level roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)

@remove_level_role.error
async def remove_level_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permission Denied", 
            description="You need **Administrator** permission to remove level roles.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)