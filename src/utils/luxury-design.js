const { EmbedBuilder } = require('discord.js');
const config = require('../../config.json');

class LuxuryDesign {
    constructor() {
        this.colors = config.colors;
        this.theme = config.theme;
    }

    // Create styled embed with Luxury Kingdom aesthetic
    createEmbed(type = 'primary') {
        const colorMap = {
            primary: this.colors.primary,
            secondary: this.colors.secondary,
            success: this.colors.success,
            error: this.colors.error,
            warning: this.colors.warning,
            info: this.colors.info,
            royal: this.colors.royal,
            luxury: this.colors.luxury,
            kingdom: this.colors.kingdom,
            accent: this.colors.accent
        };

        return new EmbedBuilder()
            .setColor(colorMap[type] || this.colors.primary)
            .setTimestamp();
    }

    // Add Luxury styling to embed title
    styleTitle(title, prefix = null) {
        const prefixMap = {
            royal: this.theme.prefixes.royal,
            luxury: this.theme.prefixes.luxury,
            kingdom: this.theme.prefixes.kingdom,
            legend: this.theme.prefixes.legend,
            elite: this.theme.prefixes.elite,
            majestic: this.theme.prefixes.majestic
        };

        const selectedPrefix = prefix ? prefixMap[prefix] : '';
        return `${selectedPrefix} ${title}`.trim();
    }

    // Create level badge with royal styling
    createLevelBadge(level, maxLevel = 50) {
        if (level >= maxLevel) {
            return `${this.theme.emojis.crown} Lv.${level} ${this.theme.emojis.crown}`;
        } else if (level >= 40) {
            return `${this.theme.emojis.diamond} Lv.${level}`;
        } else if (level >= 25) {
            return `${this.theme.emojis.medal} Lv.${level}`;
        } else if (level >= 10) {
            return `${this.theme.emojis.gem} Lv.${level}`;
        } else {
            return `Lv.${level}`;
        }
    }

    // Create progress bar with elegant aesthetic
    createProgressBar(current, max, length = 10) {
        const percentage = Math.min(Math.max(current / max, 0), 1);
        const filled = Math.floor(percentage * length);
        const empty = length - filled;
        
        const filledChar = '▰';
        const emptyChar = '▱';
        
        return `${filledChar.repeat(filled)}${emptyChar.repeat(empty)}`;
    }

    // Format numbers with royal styling
    formatNumber(num) {
        if (num >= 1000000) {
            return `${(num / 1000000).toFixed(1)}M`;
        } else if (num >= 1000) {
            return `${(num / 1000).toFixed(1)}K`;
        }
        return num.toLocaleString();
    }

    // Create rank display with royal emojis
    createRankDisplay(position) {
        switch (position) {
            case 1:
                return `${this.theme.emojis.crown} #1`;
            case 2:
                return `${this.theme.emojis.diamond} #2`;
            case 3:
                return `${this.theme.emojis.medal} #3`;
            default:
                return `${this.theme.emojis.gem} #${position}`;
        }
    }

    // Create level type icon
    getLevelTypeIcon(type, isMaxLevel = false) {
        const icons = {
            text: isMaxLevel ? `${this.theme.emojis.crown} 📜` : '📜',
            voice: isMaxLevel ? `${this.theme.emojis.crown} 🎤` : '🎤',
            role: isMaxLevel ? `${this.theme.emojis.crown} 🏅` : '🏅',
            overall: isMaxLevel ? `${this.theme.emojis.crown} ${this.theme.emojis.kingdom}` : this.theme.emojis.kingdom
        };
        return icons[type] || '❔';
    }

    // Create reward message with royal styling
    styleRewardMessage(amount, currency) {
        return `${this.theme.emojis.magic} **${this.formatNumber(amount)}** ${currency} ${this.theme.emojis.magic}`;
    }

    // Create royal divider line
    createDivider() {
        return '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
    }

    // Create footer with royal branding
    createFooter(text = null) {
        const defaultText = `${this.theme.emojis.castle} Luxury Kingdom ${this.theme.emojis.castle} • Royal Elegance Awaits`;
        return text || defaultText;
    }

    // Get color by nobility tier
    getLevelColor(level, maxLevel = 50) {
        if (level >= maxLevel) {
            return this.colors.kingdom; // Gold for max level
        } else if (level >= 40) {
            return this.colors.royal; // Purple for nobility
        } else if (level >= 25) {
            return this.colors.luxury; // Pink for high court
        } else if (level >= 10) {
            return this.colors.secondary; // Dark gold for courtiers
        } else {
            return this.colors.primary; // Gold for commoners
        }
    }

    // Create status indicator
    createStatusIndicator(status) {
        const indicators = {
            online: `${this.theme.emojis.magic} PRESENT`,
            offline: `${this.theme.emojis.pearl} ABSENT`,
            active: `${this.theme.emojis.star} ACTIVE`,
            legendary: `${this.theme.emojis.crown} LEGENDARY`,
            royal: `${this.theme.emojis.royal} ROYAL`,
            luxury: `${this.theme.emojis.diamond} LUXURY`
        };
        return indicators[status] || status;
    }

    // Create elegant field separator
    createFieldSeparator() {
        return '▸';
    }

    // Style username with nobility indication
    styleUsername(username, level, maxLevel = 50) {
        if (level >= maxLevel) {
            return `${this.theme.emojis.crown} ${username}`;
        } else if (level >= 40) {
            return `${this.theme.emojis.diamond} ${username}`;
        } else if (level >= 25) {
            return `${this.theme.emojis.medal} ${username}`;
        }
        return username;
    }
}

module.exports = LuxuryDesign;