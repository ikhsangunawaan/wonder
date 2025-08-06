import discord
import asyncio
import random
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import math

from database import database
from config import config
from cooldown_manager import cooldown_manager

class GamesSystem:
    """Manages gambling games like coinflip, dice, and slots"""
    
    def __init__(self):
        self.games_config = config.games
        
        # Slot machine symbols and their values
        self.slot_symbols = {
            '🍎': {'value': 2, 'weight': 25},  # Common
            '🍊': {'value': 3, 'weight': 20},
            '🍇': {'value': 4, 'weight': 15},
            '🍒': {'value': 5, 'weight': 12},
            '🍓': {'value': 6, 'weight': 10},
            '💎': {'value': 10, 'weight': 8},
            '⭐': {'value': 15, 'weight': 5},
            '👑': {'value': 25, 'weight': 3},
            '💰': {'value': 50, 'weight': 2}   # Rare
        }
        
        self.dice_faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
    
    async def coinflip(self, user_id: str, bet_amount: int, choice: str) -> Dict[str, Any]:
        """Play coinflip game"""
        try:
            # Validate bet amount
            min_bet = self.games_config.get('coinflip', {}).get('minBet', 10)
            max_bet = self.games_config.get('coinflip', {}).get('maxBet', 1000)
            
            if bet_amount < min_bet or bet_amount > max_bet:
                return {
                    "success": False,
                    "message": f"Bet amount must be between {min_bet:,} and {max_bet:,} {config.currency['symbol']}"
                }
            
            # Check cooldown
            cooldown_check = await cooldown_manager.check_cooldown(user_id, 'coinflip')
            if cooldown_check['on_cooldown']:
                return {
                    "success": False,
                    "message": cooldown_manager.create_cooldown_message('coinflip', cooldown_check['time_left'])
                }
            
            # Check user balance
            user_data = await database.get_user(user_id)
            if not user_data or user_data['balance'] < bet_amount:
                return {
                    "success": False,
                    "message": f"Insufficient funds! You need {bet_amount:,} {config.currency['symbol']}"
                }
            
            # Validate choice
            choice = choice.lower()
            if choice not in ['heads', 'tails', 'h', 't']:
                return {
                    "success": False,
                    "message": "Please choose 'heads' or 'tails'"
                }
            
            # Normalize choice
            user_choice = 'heads' if choice in ['heads', 'h'] else 'tails'
            
            # Check for gambling luck effect
            has_luck = await cooldown_manager.apply_gambling_luck(user_id)
            luck_bonus = 0.1 if has_luck else 0  # 10% better odds
            
            # Flip the coin (slightly favor user if they have luck)
            win_chance = 0.5 + luck_bonus
            result = 'heads' if random.random() < win_chance else 'tails'
            
            # Determine win/loss
            won = (result == user_choice)
            
            # Calculate payout
            if won:
                winnings = bet_amount  # 1:1 payout
                total_return = bet_amount + winnings
                await database.update_balance(user_id, winnings)
                await database.add_transaction(user_id, 'coinflip_win', winnings, f'Coinflip win: {result}')
            else:
                await database.update_balance(user_id, -bet_amount)
                await database.add_transaction(user_id, 'coinflip_loss', -bet_amount, f'Coinflip loss: {result}')
                total_return = 0
                winnings = -bet_amount
            
            # Set cooldown
            await cooldown_manager.set_cooldown(user_id, 'coinflip')
            
            # Create result embed
            coin_emoji = "🪙" if result == "heads" else "🪙"
            result_emoji = "🎉" if won else "😔"
            
            embed = discord.Embed(
                title=f"{coin_emoji} Coinflip Result",
                color=int(config.colors['success' if won else 'error'].replace('#', ''), 16)
            )
            
            embed.add_field(name="Your Choice", value=user_choice.title(), inline=True)
            embed.add_field(name="Result", value=result.title(), inline=True)
            embed.add_field(name="Outcome", value="Won! 🎉" if won else "Lost 😔", inline=True)
            
            if won:
                embed.add_field(
                    name="Winnings", 
                    value=f"+{winnings:,} {config.currency['symbol']}", 
                    inline=False
                )
            else:
                embed.add_field(
                    name="Loss", 
                    value=f"-{bet_amount:,} {config.currency['symbol']}", 
                    inline=False
                )
            
            if has_luck:
                embed.set_footer(text="🍀 Gambling luck was used!")
            
            return {
                "success": True,
                "won": won,
                "result": result,
                "winnings": winnings,
                "embed": embed
            }
            
        except Exception as e:
            logging.error(f"Error in coinflip game: {e}")
            return {"success": False, "message": "An error occurred while playing coinflip."}
    
    async def dice(self, user_id: str, bet_amount: int, target: int) -> Dict[str, Any]:
        """Play dice game"""
        try:
            # Validate bet amount
            min_bet = self.games_config.get('dice', {}).get('minBet', 10)
            max_bet = self.games_config.get('dice', {}).get('maxBet', 500)
            
            if bet_amount < min_bet or bet_amount > max_bet:
                return {
                    "success": False,
                    "message": f"Bet amount must be between {min_bet:,} and {max_bet:,} {config.currency['symbol']}"
                }
            
            # Validate target
            if target < 1 or target > 6:
                return {
                    "success": False,
                    "message": "Target must be between 1 and 6"
                }
            
            # Check cooldown
            cooldown_check = await cooldown_manager.check_cooldown(user_id, 'dice')
            if cooldown_check['on_cooldown']:
                return {
                    "success": False,
                    "message": cooldown_manager.create_cooldown_message('dice', cooldown_check['time_left'])
                }
            
            # Check user balance
            user_data = await database.get_user(user_id)
            if not user_data or user_data['balance'] < bet_amount:
                return {
                    "success": False,
                    "message": f"Insufficient funds! You need {bet_amount:,} {config.currency['symbol']}"
                }
            
            # Check for gambling luck effect
            has_luck = await cooldown_manager.apply_gambling_luck(user_id)
            
            # Roll the dice
            if has_luck and random.random() < 0.3:  # 30% chance to get desired result with luck
                result = target
            else:
                result = random.randint(1, 6)
            
            # Determine win/loss
            won = (result == target)
            
            # Calculate payout (5:1 for exact match)
            if won:
                winnings = bet_amount * 5
                await database.update_balance(user_id, winnings)
                await database.add_transaction(user_id, 'dice_win', winnings, f'Dice win: rolled {result}')
            else:
                await database.update_balance(user_id, -bet_amount)
                await database.add_transaction(user_id, 'dice_loss', -bet_amount, f'Dice loss: rolled {result}')
                winnings = -bet_amount
            
            # Set cooldown
            await cooldown_manager.set_cooldown(user_id, 'dice')
            
            # Create result embed
            dice_emoji = self.dice_faces[result - 1]
            
            embed = discord.Embed(
                title=f"🎲 Dice Roll Result",
                color=int(config.colors['success' if won else 'error'].replace('#', ''), 16)
            )
            
            embed.add_field(name="Your Target", value=f"{target} {self.dice_faces[target-1]}", inline=True)
            embed.add_field(name="Result", value=f"{result} {dice_emoji}", inline=True)
            embed.add_field(name="Outcome", value="Won! 🎉" if won else "Lost 😔", inline=True)
            
            if won:
                embed.add_field(
                    name="Winnings", 
                    value=f"+{winnings:,} {config.currency['symbol']} (5x)", 
                    inline=False
                )
            else:
                embed.add_field(
                    name="Loss", 
                    value=f"-{bet_amount:,} {config.currency['symbol']}", 
                    inline=False
                )
            
            if has_luck:
                embed.set_footer(text="🍀 Gambling luck was used!")
            
            return {
                "success": True,
                "won": won,
                "result": result,
                "winnings": winnings,
                "embed": embed
            }
            
        except Exception as e:
            logging.error(f"Error in dice game: {e}")
            return {"success": False, "message": "An error occurred while playing dice."}
    
    async def slots(self, user_id: str, bet_amount: int) -> Dict[str, Any]:
        """Play slots game"""
        try:
            # Validate bet amount
            min_bet = self.games_config.get('slots', {}).get('minBet', 20)
            max_bet = self.games_config.get('slots', {}).get('maxBet', 200)
            
            if bet_amount < min_bet or bet_amount > max_bet:
                return {
                    "success": False,
                    "message": f"Bet amount must be between {min_bet:,} and {max_bet:,} {config.currency['symbol']}"
                }
            
            # Check cooldown
            cooldown_check = await cooldown_manager.check_cooldown(user_id, 'slots')
            if cooldown_check['on_cooldown']:
                return {
                    "success": False,
                    "message": cooldown_manager.create_cooldown_message('slots', cooldown_check['time_left'])
                }
            
            # Check user balance
            user_data = await database.get_user(user_id)
            if not user_data or user_data['balance'] < bet_amount:
                return {
                    "success": False,
                    "message": f"Insufficient funds! You need {bet_amount:,} {config.currency['symbol']}"
                }
            
            # Check for gambling luck effect
            has_luck = await cooldown_manager.apply_gambling_luck(user_id)
            luck_multiplier = 1.5 if has_luck else 1.0
            
            # Spin the slots
            reels = []
            for _ in range(3):
                reel = self._spin_reel(luck_multiplier)
                reels.append(reel)
            
            # Calculate winnings
            win_info = self._calculate_slots_win(reels, bet_amount)
            
            # Process the bet
            if win_info['winnings'] > 0:
                net_winnings = win_info['winnings'] - bet_amount
                await database.update_balance(user_id, net_winnings)
                await database.add_transaction(user_id, 'slots_win', net_winnings, f'Slots win: {win_info["type"]}')
            else:
                await database.update_balance(user_id, -bet_amount)
                await database.add_transaction(user_id, 'slots_loss', -bet_amount, 'Slots loss')
            
            # Set cooldown
            await cooldown_manager.set_cooldown(user_id, 'slots')
            
            # Create result embed
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=int(config.colors['success' if win_info['winnings'] > 0 else 'error'].replace('#', ''), 16)
            )
            
            # Show the reels
            reels_display = f"┌─────────────┐\n│ {reels[0]} │ {reels[1]} │ {reels[2]} │\n└─────────────┘"
            embed.add_field(name="Result", value=f"```\n{reels_display}\n```", inline=False)
            
            if win_info['winnings'] > 0:
                embed.add_field(name="🎉 Winner!", value=win_info['type'], inline=True)
                embed.add_field(
                    name="Winnings", 
                    value=f"+{win_info['winnings'] - bet_amount:,} {config.currency['symbol']} ({win_info['multiplier']}x)", 
                    inline=True
                )
            else:
                embed.add_field(name="😔 No Match", value="Better luck next time!", inline=True)
                embed.add_field(
                    name="Loss", 
                    value=f"-{bet_amount:,} {config.currency['symbol']}", 
                    inline=True
                )
            
            if has_luck:
                embed.set_footer(text="🍀 Gambling luck was used!")
            
            return {
                "success": True,
                "won": win_info['winnings'] > 0,
                "reels": reels,
                "winnings": win_info['winnings'] - bet_amount,
                "win_type": win_info['type'],
                "embed": embed
            }
            
        except Exception as e:
            logging.error(f"Error in slots game: {e}")
            return {"success": False, "message": "An error occurred while playing slots."}
    
    def _spin_reel(self, luck_multiplier: float = 1.0) -> str:
        """Spin a single reel of the slot machine"""
        # Create weighted list of symbols
        weighted_symbols = []
        for symbol, data in self.slot_symbols.items():
            # Apply luck multiplier to rare symbols (higher value = more rare)
            weight = data['weight']
            if data['value'] >= 10:  # Rare symbols
                weight = int(weight * luck_multiplier)
            
            weighted_symbols.extend([symbol] * weight)
        
        return random.choice(weighted_symbols)
    
    def _calculate_slots_win(self, reels: List[str], bet_amount: int) -> Dict[str, Any]:
        """Calculate slots winnings based on the reels"""
        # Check for three of a kind (jackpot)
        if reels[0] == reels[1] == reels[2]:
            symbol_value = self.slot_symbols[reels[0]]['value']
            multiplier = symbol_value
            return {
                'winnings': bet_amount * multiplier,
                'multiplier': multiplier,
                'type': f"JACKPOT! Three {reels[0]}"
            }
        
        # Check for two of a kind
        if reels[0] == reels[1] or reels[0] == reels[2] or reels[1] == reels[2]:
            # Find the matching symbol
            if reels[0] == reels[1]:
                symbol = reels[0]
            elif reels[0] == reels[2]:
                symbol = reels[0]
            else:
                symbol = reels[1]
            
            symbol_value = self.slot_symbols[symbol]['value']
            multiplier = max(1.5, symbol_value * 0.5)  # Minimum 1.5x for any pair
            
            return {
                'winnings': int(bet_amount * multiplier),
                'multiplier': multiplier,
                'type': f"Pair of {symbol}"
            }
        
        # Check for special combinations
        unique_symbols = set(reels)
        if len(unique_symbols) == 3:
            # All different symbols
            total_value = sum(self.slot_symbols[symbol]['value'] for symbol in reels)
            if total_value >= 30:  # High value combination
                multiplier = 2.0
                return {
                    'winnings': int(bet_amount * multiplier),
                    'multiplier': multiplier,
                    'type': "High Value Combo"
                }
        
        # No win
        return {
            'winnings': 0,
            'multiplier': 0,
            'type': "No match"
        }
    
    async def get_gambling_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's gambling statistics"""
        try:
            # Get transaction history for gambling activities
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    
                    # Get all gambling transactions
                    async with db.execute(
                        """SELECT type, amount, description FROM transactions 
                           WHERE user_id = ? AND type LIKE '%_win' OR type LIKE '%_loss'
                           ORDER BY created_at DESC""",
                        (user_id,)
                    ) as cursor:
                        transactions = await cursor.fetchall()
            
            stats = {
                'total_games': 0,
                'total_wagered': 0,
                'total_won': 0,
                'total_lost': 0,
                'net_profit': 0,
                'win_rate': 0,
                'games': {
                    'coinflip': {'played': 0, 'won': 0, 'wagered': 0, 'profit': 0},
                    'dice': {'played': 0, 'won': 0, 'wagered': 0, 'profit': 0},
                    'slots': {'played': 0, 'won': 0, 'wagered': 0, 'profit': 0}
                }
            }
            
            for transaction in transactions:
                amount = transaction['amount']
                transaction_type = transaction['type']
                
                # Determine game type
                if 'coinflip' in transaction_type:
                    game = 'coinflip'
                elif 'dice' in transaction_type:
                    game = 'dice'
                elif 'slots' in transaction_type:
                    game = 'slots'
                else:
                    continue
                
                stats['games'][game]['played'] += 1
                stats['total_games'] += 1
                
                if '_win' in transaction_type:
                    stats['games'][game]['won'] += 1
                    stats['games'][game]['profit'] += amount
                    stats['total_won'] += amount
                else:  # loss
                    stats['games'][game]['wagered'] += abs(amount)
                    stats['games'][game]['profit'] += amount  # amount is negative
                    stats['total_lost'] += abs(amount)
                    stats['total_wagered'] += abs(amount)
            
            # Calculate overall stats
            stats['net_profit'] = stats['total_won'] - stats['total_lost']
            if stats['total_games'] > 0:
                wins = sum(game['won'] for game in stats['games'].values())
                stats['win_rate'] = (wins / stats['total_games']) * 100
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting gambling stats: {e}")
            return {}
    
    async def create_gambling_stats_embed(self, user_id: str, user_name: str) -> discord.Embed:
        """Create an embed showing user's gambling statistics"""
        stats = await self.get_gambling_stats(user_id)
        
        embed = discord.Embed(
            title=f"🎲 Gambling Stats - {user_name}",
            color=int(config.colors['info'].replace('#', ''), 16)
        )
        
        if stats['total_games'] == 0:
            embed.description = "No gambling history found!"
            return embed
        
        # Overall stats
        profit_color = "+" if stats['net_profit'] >= 0 else ""
        embed.add_field(
            name="📊 Overall Stats",
            value=f"**Games Played:** {stats['total_games']:,}\n"
                  f"**Win Rate:** {stats['win_rate']:.1f}%\n"
                  f"**Total Wagered:** {stats['total_wagered']:,} {config.currency['symbol']}\n"
                  f"**Net Profit:** {profit_color}{stats['net_profit']:,} {config.currency['symbol']}",
            inline=False
        )
        
        # Individual game stats
        for game_name, game_stats in stats['games'].items():
            if game_stats['played'] > 0:
                game_win_rate = (game_stats['won'] / game_stats['played']) * 100
                game_profit_color = "+" if game_stats['profit'] >= 0 else ""
                
                embed.add_field(
                    name=f"🎮 {game_name.title()}",
                    value=f"Played: {game_stats['played']}\n"
                          f"Won: {game_stats['won']} ({game_win_rate:.1f}%)\n"
                          f"Profit: {game_profit_color}{game_stats['profit']:,} {config.currency['symbol']}",
                    inline=True
                )
        
        return embed

# Global games system instance
games_system = GamesSystem()