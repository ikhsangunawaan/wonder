const { deployCommands } = require('./src/slash-commands');

async function deploy() {
    try {
        console.log('🚀 Starting deployment of slash commands...');
        await deployCommands();
        console.log('✅ Slash commands deployed successfully!');
        process.exit(0);
    } catch (error) {
        console.error('❌ Error deploying slash commands:', error);
        process.exit(1);
    }
}

deploy();